import torch
import torch.nn.functional as F
import torch.nn as nn
import pandas as pd
from transformers import DataCollatorWithPadding,AutoModelForSequenceClassification, Trainer, TrainingArguments,AutoTokenizer,AutoModel,AutoConfig
from torch.utils.data import DataLoader, Dataset

df= pd.read_excel("preprocessed_arabic_data.xlsx")

class MyDataset(Dataset):
    def __init__(self, dataframe, tokenizer, max_seq_length=256):
        self.data = dataframe
        self.tokenizer = tokenizer
        self.max_seq_length = max_seq_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        text = row["Text_pro"] #the column of the preprocessed data

        # Tokenize the text and truncate/pad to the desired sequence length
        inputs = self.tokenizer(
            text,
            padding='max_length',
            truncation=True,
            max_length=self.max_seq_length,
            return_tensors='pt'
        )

        input_ids = inputs["input_ids"].squeeze()
        attention_mask = inputs["attention_mask"].squeeze()

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask
        }
    
checkpoint = "UBC-NLP/MARBERT"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
max_seq_length = 256  # Adjust as needed

# Create train dataset and dataloader
dataset = MyDataset(df, tokenizer, max_seq_length)
batch_size = 32 # Adjust as needed
dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

class MyTopicPredictionModel(nn.Module):
    def __init__(self, checkpoint, num_topics):
        super(MyTopicPredictionModel, self).__init__()
        self.num_topics = num_topics

        self.model = AutoModel.from_pretrained(checkpoint, config=AutoConfig.from_pretrained(checkpoint, output_hidden_states=True))
        self.dropout = nn.Dropout(0.1)
        self.lstm = nn.LSTM(768, 256, num_layers=1, dropout=0.1, bidirectional=False, batch_first=True)
        self.classifier = nn.Linear(256, num_topics)  # Number of topics as output labels

    def forward(self, input_ids=None, attention_mask=None, labels=None):
        outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)

        last_hidden_state = outputs.last_hidden_state
        sequence_outputs = self.dropout(last_hidden_state)
        lstm_out, _ = self.lstm(sequence_outputs)  # Remove [:, -1, :]
        logits =F.softmax(self.classifier(lstm_out[:, -1, :]))
        #logits = self.classifier(sequence_outputs)
        #logits = F.softmax(logits)
  # Use the last output from LSTM
        return logits
    

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# Load the model
model = MyTopicPredictionModel(checkpoint='UBC-NLP/MARBERT', num_topics=7)

# Load the saved state dictionary
model.load_state_dict(torch.load('/content/drive/My Drive/model.pth'))
model.to(device)  # Ensure it's on the correct device (CPU or GPU)

# Set the model to evaluation mode
model.eval()

all_predicted_labels = []
with torch.no_grad():
    for batch in dataloader:  # Assuming you have a test DataLoader similar to train DataLoader
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)

        logits = model(input_ids=input_ids, attention_mask=attention_mask)
        predicted_labels = torch.argmax(logits, dim=1)
        all_predicted_labels.extend(predicted_labels.cpu().numpy())

df['topic'] = all_predicted_labels
label_to_topic = {
    0: 'Economy',
    1: 'Education',
    2: 'Sanitary Measures',
    3: 'Health',
    4: 'Social Life',
    5: 'Govt',
    6: 'Stats'
}
df['topic'] = df['topic'].map(label_to_topic)
df.to_excel('predicted_topics.xlsx', index=False)