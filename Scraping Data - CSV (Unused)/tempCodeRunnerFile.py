

import pandas as pd

def process_csv(input_csv_file, output_csv_file):
    # Read the CSV file
    df = pd.read_csv(input_csv_file)
    
    # Keep only the 'url' column
    df = df[['url']]
    
    # Add a new column with 'malware' as the value for each row
    df['type'] = 'phishing'
    
    # Save the modified dataframe to a new CSV file
    df.to_csv(output_csv_file, index=False)

# Example usage
input_csv_file = 'phphph.csv'  # Replace with your input file name
output_csv_file = 'actual_phishing.csv'  # Desired output file name
process_csv(input_csv_file, output_csv_file)

print(f"Processed {input_csv_file} and saved as {output_csv_file}")
