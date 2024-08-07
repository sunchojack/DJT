import gdelt
import pandas as pd
from io import StringIO
from datetime import datetime

# Initialize GDELT version 2
gd2 = gdelt.gdelt(version=2)

def main():
    # Define the date range from February 1, 2024 to today
    start_date = '20240201'
    end_date = datetime.now().strftime('%Y%m%d')

    # Full day pull, output to pandas dataframe, GKG table
    results = gd2.Search([start_date, end_date], table='gkg', coverage=False, output='csv')

    # Read the CSV string into a pandas DataFrame
    df = pd.read_csv(StringIO(results))

    # Filter the DataFrame for rows that mention "Trump"
    df_filtered = df[df.apply(lambda row: row.astype(str).str.contains('Trump', case=False).any(), axis=1)]

    # Save the filtered DataFrame to a CSV file
    df_filtered.to_csv('gdelt_results_v1.csv', index=False)

if __name__ == "__main__":
    main()
