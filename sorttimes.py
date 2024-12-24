import pandas as pd

# Load the CSV file
def sort_csv_by_time(input_csv, output_csv):
    try:
        # Read the CSV file
        df = pd.read_csv(input_csv)
        
        if 'blank' in df.columns:
            df = df.drop(columns=['blank'])
        
        # Ensure 'time-of-text' is treated as a time type
        df['time-of-text'] = pd.to_datetime(df['time-of-text'], format='%H:%M').dt.time
        
        # Sort by the 'time-of-text' column
        df_sorted = df.sort_values(by='time-of-text')
        
        # Save the sorted CSV
        df_sorted.to_csv(output_csv, index=False)
        print(f"CSV sorted by 'time-of-text' and saved to {output_csv}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    # Input and output file paths
    input_csv = "moretimes.csv"   # Replace with your input file path
    output_csv = "sorted_time_quotes.csv"  # Replace with your desired output file path
    
    # Sort the CSV
    sort_csv_by_time(input_csv, output_csv)
