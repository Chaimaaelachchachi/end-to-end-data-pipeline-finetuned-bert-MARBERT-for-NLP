import pandas as pd
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from pyarabic.araby import strip_tashkeel, strip_tatweel
# Download the required nltk resources (only required once)
nltk.download('punkt')
nltk.download('stopwords')
def preprocess_arabic_text(text):
    text = strip_tashkeel(text)
    text = strip_tatweel(text)

    additional_symbols = r'[،؟]'  

    pattern = r'[' + re.escape(additional_symbols) + ']'
    text = re.sub(pattern, '', text)
    
    # Remove non-Arabic characters and numbers
    text = re.sub(r'[^\u0600-\u06FF\s]', '', text)
    
    words = word_tokenize(text)
    
    stop_words = set(stopwords.words('arabic'))
    words = [word for word in words if word not in stop_words]
    
    preprocessed_text = ' '.join(words)
    
    return preprocessed_text

def main(input_file, output_file):
    # Load the data from the CSV file
    df = pd.read_excel(input_file)
    
    #df['source'] = 'twitter'
    
    df['Text_pro'] = df['Text'].apply(preprocess_arabic_text)
    
    # Save the preprocessed data to a new CSV file
    df.to_excel(output_file, index=False)

if __name__ == "__main__":
    input_excel_file = "all_data.xlsx"  # Replace with the path to your Arabic dataset CSV file
    output_csv_file = "preprocessed_arabic_data.xlsx"  # Replace with the desired output file path
    main(input_excel_file, output_csv_file)