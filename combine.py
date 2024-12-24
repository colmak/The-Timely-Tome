import pandas as pd

def combine_datasets(dataset1_path, dataset2_path, output_path):
    """
    Combines two datasets, removes duplicates, and saves the combined dataset.
    
    Parameters:
        dataset1_path (str): Path to the first dataset (CSV with ',' delimiter).
        dataset2_path (str): Path to the second dataset ('|' delimiter).
        output_path (str): Path to save the combined dataset.
    """
    try:
        # Load the first dataset (CSV with ',' delimiter)
        dataset1 = pd.read_csv(dataset1_path)
        
        # Load the second dataset ('|' delimiter)
        dataset2 = pd.read_csv(
            dataset2_path, 
            delimiter='|', 
            # error_bad_lines=False,  # For older pandas versions
            on_bad_lines="skip"    # For pandas >= 1.3.0
        )
        
        # Ensure column names are consistent
        dataset2.columns = dataset1.columns  # Rename to match the first dataset
        
        # Combine the datasets
        combined = pd.concat([dataset1, dataset2], ignore_index=True)
        
        # Remove duplicates based on all columns
        combined = combined.drop_duplicates()
        
        # Save the combined dataset
        combined.to_csv(output_path, index=False)
        print(f"Combined dataset saved to {output_path}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    dataset1_path = "sorted_time_quotes.csv"  # Replace with the first dataset path
    dataset2_path = "times.csv"  # Replace with the second dataset path
    output_path = "combined_time_quotes.csv"  # Replace with the desired output file path
    
    combine_datasets(dataset1_path, dataset2_path, output_path)
