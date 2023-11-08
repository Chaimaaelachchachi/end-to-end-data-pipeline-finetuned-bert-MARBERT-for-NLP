import os
import pandas as pd

# Specify the folder path where the Excel files are located
folder_path = 'C:\\Users\\LENOVO\\Desktop\\stage ticlab'  # Replace with the actual folder path

# Initialize an empty DataFrame to store the concatenated data
concatenated_data = pd.DataFrame(columns=['date', 'Text', 'source'])

# Iterate through all files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.xlsx') and filename != 'all_data.xlsx':  # Change to '.xls' if your files are in Excel 97-2003 format
        file_path = os.path.join(folder_path, filename)
        
        # Read the Excel file and extract the data
        df = pd.read_excel(file_path)
        
        # Append the data to the concatenated_data DataFrame
        concatenated_data = concatenated_data.append(df, ignore_index=True)

# Specify the output Excel file path
output_file_path = os.path.join(folder_path, 'all_data.xlsx')  # Replace with the desired output file path

# Write the concatenated data to a new Excel file
concatenated_data.to_excel(output_file_path, index=False)

