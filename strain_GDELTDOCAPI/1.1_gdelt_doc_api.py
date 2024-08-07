from gdeltdoc import GdeltDoc, Filters
from datetime import datetime, timedelta
import os
import pandas as pd


def main():
    # Initialize GDELT API
    gd = GdeltDoc()

    # Define the start date and end date
    start_date = datetime.strptime('2024-01-01', '%Y-%m-%d')
    end_date = datetime.strptime('2024-06-25', '%Y-%m-%d')

    # Create a folder for the results if it doesn't exist
    output_folder = 'gdelt_doc_api_daily'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate over the period daily
    current_date = start_date
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)

        # Convert dates to the required format
        start_date_str = current_date.strftime('%Y-%m-%d')
        end_date_str = next_date.strftime('%Y-%m-%d')

        # Set up the filters for the current daily period
        f = Filters(
            keyword="trump",
            country='US',
            start_date=start_date_str,
            end_date=end_date_str
        )

        # Search for articles matching the filters
        articles = gd.article_search(f)

        # Convert the articles to a DataFrame
        df_articles = pd.DataFrame(articles)

        # Save the filtered DataFrame to a CSV file with the appropriate filename
        output_filename = f'{output_folder}/gdelt_results_{start_date_str}.csv'
        df_articles.to_csv(output_filename, index=False)
        print(f'Results saved to {output_filename}')

        # Move to the next day
        current_date = next_date


if __name__ == "__main__":
    main()
