import pandas as pd
import os

def group_csv_by_department_and_title(input_file, output_file):
    """
    Reads a CSV file, groups the data by 'department' and 'title',
    and writes the grouped data into a new CSV file with the columns:
    count, name, department, title, access.

    Args:
        input_file (str): Path to the input CSV file.
        output_file (str): Path to the output CSV file.
    """
    # Read the input CSV file with ',' as the separator
    df = pd.read_csv(input_file, sep=',')

    # Drop rows where 'department' is null
    df = df.dropna(subset=['department'])

    # Group by 'department', 'title', and 'access' and count occurrences
    grouped = df.groupby(['department', 'title', 'access']).size().reset_index(name='count')

    # Merge the grouped data back with the original to include other columns
    merged = pd.merge(grouped, df, on=['department', 'title', 'access'], how='left')

    # Drop duplicates to keep only one row per group
    result = merged[['count', 'name', 'department', 'title', 'access']].drop_duplicates()

    # Write the grouped data to a new CSV file with ',' as the separator
    result.to_csv(output_file, index=False, sep=',')
    print(f"Grouped data has been written to {output_file}")

# Example usage
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv = os.path.join(base_dir, "input.csv")  # Caminho absoluto para o arquivo de entrada
    output_csv = os.path.join(base_dir, "grouped_output.csv")  # Caminho absoluto para o arquivo de saída
    group_csv_by_department_and_title(input_csv, output_csv)