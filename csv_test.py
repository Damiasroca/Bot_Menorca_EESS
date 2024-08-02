import pandas as pd

# Path to your CSV file
file_path = '/home/combustible/json_processing/combinat_per_importar.csvdata.csv'

# Load the CSV file
data = pd.read_csv(file_path)

# Check for rows with missing values in the 'ID' column
missing_id_rows = data[data['ID'].isnull()]

# Display the rows with missing 'ID' values
print(f"Rows with missing 'ID' values: {missing_id_rows}")
