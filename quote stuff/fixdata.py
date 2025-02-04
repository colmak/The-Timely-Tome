import pandas as pd

# Read the CSV file
df = pd.read_csv('combined_time_quotes.csv')

# Function to standardize time format
def standardize_time_format(time_str):
    if len(time_str) == 5:  # Format is HH:MM
        return time_str + ':00'
    return time_str  # Format is already HH:MM:SS

# Apply the function to the relevant columns
df['time-of-text'] = df['time-of-text'].apply(standardize_time_format)

# Save the modified DataFrame back to a CSV file
df.to_csv('combined_time_quotes_standardized.csv', index=False)