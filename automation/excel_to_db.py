import os
import pandas as pd
from sqlalchemy import create_engine

# Replace 'sqlite:///my_database.db' with your database connection string
db_connection_string = 'sqlite:///my_database.db'

# Create a SQLAlchemy database engine
engine = create_engine(db_connection_string)

# Folder containing Excel files
folder_path = 'path_to_excel_files/'

# List all Excel files in the folder
excel_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]

for file in excel_files:
    file_path = os.path.join(folder_path, file)
    
    # Read the Excel file into a Pandas DataFrame
    df = pd.read_excel(file_path)

    # Replace 'table_name' with the name of the table you want to create or append to
    table_name = 'your_table_name'

    # Write the DataFrame to the SQL database
    df.to_sql(table_name, engine, if_exists='append', index=False)

print("Data imported into the database successfully.")
