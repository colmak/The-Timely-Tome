import pandas as pd
import matplotlib.pyplot as plt

def visualize_time_distribution(input_csv):
    """
    Visualizes the distribution of time occurrences in the dataset with reduced x-axis labels.
    
    Parameters:
        input_csv (str): Path to the input CSV file.
    """
    try:
        # Load the dataset
        df = pd.read_csv(input_csv)

        # Clean the 'time-of-text' column
        def parse_time_safe(time_str):
            try:
                return pd.to_datetime(time_str, format='%H:%M').time()
            except ValueError:
                return None  # Return None for invalid formats

        df['time-of-text'] = df['time-of-text'].apply(parse_time_safe)

        # Drop rows with invalid time entries
        df = df.dropna(subset=['time-of-text'])

        # Count occurrences of each time
        time_counts = df['time-of-text'].value_counts().sort_index()

        # Create a bar chart
        plt.figure(figsize=(12, 6))
        plt.bar(time_counts.index.astype(str), time_counts.values, width=0.5, alpha=0.7)

        # Customize x-axis to show fewer labels
        tick_indices = range(0, len(time_counts), max(1, len(time_counts) // 20))  # Show ~20 labels
        tick_labels = [str(time_counts.index[i]) for i in tick_indices]
        plt.xticks(tick_indices, tick_labels, rotation=90)

        # Add titles and labels
        plt.title("Distribution of Time Mentions")
        plt.xlabel("Time (HH:MM)")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.show()

        # Optional: Create a histogram (grouped by hour)
        df['hour'] = df['time-of-text'].apply(lambda t: t.hour)
        plt.figure(figsize=(10, 6))
        df['hour'].value_counts().sort_index().plot(kind='bar', alpha=0.7)
        plt.title("Time Mentions Grouped by Hour")
        plt.xlabel("Hour (24-hour format)")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    input_csv = "combined_time_quotes.csv"  # Replace with your combined dataset path
    visualize_time_distribution(input_csv)
