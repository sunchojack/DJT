import pandas as pd
import dask.dataframe as dd

# Read the data using Dask
data = dd.read_csv('gdelt_results.csv', assume_missing=True,
                   dtype={'SocialImageEmbeds': 'object'}).head(n=500)

# Compute the head to print the first 10 rows
print(data.head(10))

# Save the Dask DataFrame to a new CSV file
# data.to_csv('gdelt_results_500.csv', single_file=True)

data.to_csv('gdelt_results_500.csv', index=False)