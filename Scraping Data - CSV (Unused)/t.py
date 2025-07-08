# import pandas as pd

# def count_rows(csv_file):
#     # Read the CSV file, skipping malformed rows
#     df = pd.read_csv(csv_file, on_bad_lines="skip")
    
#     # Get the number of rows
#     row_count = len(df)
#     print(f"The number of rows in {csv_file} is {row_count}")

# # Example usage
# csv_file = 'phphph.csv'  # Replace with your file name
# count_rows(csv_file)

import pandas as pd

def trim_csv(csv_file, max_rows=17882):
    # Read only the first 180,000 rows, skipping any bad lines if needed
    df = pd.read_csv(csv_file, nrows=max_rows, on_bad_lines="skip")
    
    # Overwrite the CSV file with only the first 180,000 rows
    df.to_csv(csv_file, index=False)
    print(f"Trimmed {csv_file} to the first {max_rows} rows.")

# Example usage
csv_file = 'phphph.csv'  # Replace with your actual file name
trim_csv(csv_file)


