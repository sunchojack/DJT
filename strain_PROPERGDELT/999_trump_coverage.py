import gdelt
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Initialize GDELT version 2
gd2 = gdelt.gdelt(version=2)

def process_dates(date_pair):
    start_date, end_date, output_folder = date_pair

    # Convert dates to the required format
    start_date_str = start_date.strftime('%Y%m%d%H%M')
    end_date_str = end_date.strftime('%Y%m%d%H%M')

    # Define the output filename
    output_filename = f'{output_folder}/{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}_gdelt.csv'

    # Skip processing if the file already exists
    if os.path.exists(output_filename):
        print(f'Skipping {output_filename}, already exists.')
        return

    try:
        print(f'Processing from {start_date} to {end_date}')
        # Full day pull, output to pandas dataframe, GKG table
        results = gd2.Search([start_date_str, end_date_str], table='gkg', coverage=False, output='csv')

        # Read the CSV string into a pandas DataFrame
        df = pd.read_csv(StringIO(results))

        # Filter the DataFrame for rows that mention "Trump"
        df_filtered = df[df.apply(lambda row: row.astype(str).str.contains('Trump', case=False).any(), axis=1)]

        # Save the filtered DataFrame to a CSV file with the appropriate filename
        df_filtered.to_csv(output_filename, index=False)
        print(f'Results saved to {output_filename}')
    except Exception as e:
        print(f'Error processing dates {start_date} to {end_date}: {e}')

def main():
    # Define the start date and end date
    start_date = datetime.strptime('20240101', '%Y%m%d')
    end_date = datetime.strptime('20240625', '%Y%m%d')

    # Create a folder for the results if it doesn't exist
    output_folder = 'spread_results'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Create a list of 2-day pairs, skipping those that already have CSV files
    two_day_pairs = []
    current_date = start_date
    while current_date < end_date:
        next_date = current_date + timedelta(days=2)
        if next_date > end_date:
            next_date = end_date

        output_filename = f'{output_folder}/{current_date.strftime("%Y%m%d")}_{next_date.strftime("%Y%m%d")}_gdelt.csv'

        if not os.path.exists(output_filename):
            two_day_pairs.append((current_date, next_date, output_folder))

        current_date = next_date + timedelta(days=1)

    # Write the list of date pairs we still need to get through to a text file
    with open('dates_to_process.txt', 'w') as f:
        for date_pair in two_day_pairs:
            f.write(f'{date_pair[0].strftime("%Y%m%d")}-{date_pair[1].strftime("%Y%m%d")}\n')

    # Use ThreadPoolExecutor to process date pairs concurrently
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(process_dates, date_pair): date_pair for date_pair in two_day_pairs}
        for future in as_completed(futures):
            date_pair = futures[future]
            try:
                future.result()
                # Remove successfully processed date pairs from the text file
                with open('dates_to_process.txt', 'r') as f:
                    lines = f.readlines()
                with open('dates_to_process.txt', 'w') as f:
                    for line in lines:
                        if line.strip() != f'{date_pair[0].strftime("%Y%m%d")}-{date_pair[1].strftime("%Y%m%d")}':
                            f.write(line)
            except Exception as e:
                print(f'Error processing {date_pair}: {e}')

if __name__ == "__main__":
    main()
