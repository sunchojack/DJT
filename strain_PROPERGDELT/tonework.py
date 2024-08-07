import pandas as pd
from datetime import datetime as dt
import matplotlib.pyplot as plt
from scipy import stats

# Load the data
sentiment = pd.read_csv('workdata/sentiment.csv')
stock = pd.read_csv('workdata/djt_stock.csv')

# def calculate_avg_tone(v2tone_str):
#     values = v2tone_str.split(',')
#     # Exclude the last value and handle invalid values
#     values = values[:-1]
#     float_values = []
#     for v in values:
#         try:
#             float_values.append(float(v))
#         except ValueError:
#             continue
#     if float_values:
#         return sum(float_values) / len(float_values)
#     return None

def take_specific_tone(v2tone_str, which):
    values = v2tone_str.split(',')
    try:
        first_value = float(values[which])
        return first_value
    except ValueError:
        return None

# Apply the function to calculate the first tone value
sentiment['V2ToneOut'] = sentiment['V2Tone'].apply(lambda x: take_specific_tone(x, which=2))

# Convert DATE column to datetime format
sentiment['DATE'] = pd.to_datetime(sentiment['DATE'])

# Correct the column renaming
sentiment.rename(columns={'DATE': 'Date'}, inplace=True)  # Ensure the correct column name 'Date'

# Format the datetime as 'Day/Month/Year'
sentiment['Date'] = sentiment['Date'].dt.strftime('%d/%m/%Y')

print(sentiment.head(10))

sentiment_AGGR = sentiment.groupby('Date')['V2ToneOut'].mean().reset_index()
print(sentiment_AGGR.head())
# # Plot the chart
# plt.plot(sentiment_AGGR['Date'], sentiment_AGGR['V2ToneOut'])
# plt.grid(True)
# plt.show()

both = sentiment_AGGR.merge(stock, on='Date', how='inner')
print(both.head(10))
#
# plt.plot(both['Date'], both['Adj Close'], both['V2ToneOut'])
# plt.grid(True)
# plt.show()
#

both['diff_Adj Close'] = both['Adj Close'] - both['Adj Close'].shift(1)
both['diff_V2ToneOut'] = both['V2ToneOut'] - both['V2ToneOut'].shift(1)

fig, ax1 = plt.subplots()

# Plotting diff_Adj Close on first axis
ax1.plot(both['Date'], both['Adj Close'], color='darkgreen', label='Diff Adj Close')
ax1.set_xlabel('Date')
ax1.set_ylabel('Diff Adj Close', color='black')
ax1.tick_params(axis='y', labelcolor='black')
ax1.grid(False)

# Creating a second y-axis for diff_V2ToneOut
ax2 = ax1.twinx()
ax2.plot(both['Date'], both['V2ToneOut'], color='brown', label='Diff V2ToneOut', linestyle='dashed')
ax2.set_ylabel('Diff V2ToneOut', color='black')
ax2.tick_params(axis='y', labelcolor='black')

plt.title('Differences: Sentiment vs Stock Price')
plt.show()

plt.scatter(both['diff_V2ToneOut'], both['diff_Adj Close'])
# plt.scatter(both['V2ToneOut'], both['Adj Close'])
plt.grid(True)
plt.show()

both.dropna(subset=['diff_V2ToneOut', 'diff_Adj Close'], inplace=True)

slope, intercept, r_value, p_value, std_err = stats.linregress(both['diff_V2ToneOut'].astype('float'),
                                                               both['Adj Close'].astype('float'))
print(f"Slope: {slope:.2f}")
print(f"Intercept: {intercept:.2f}")
print(f"R-squared: {r_value**2:.2f}")
print(f"P-value: {p_value:.4f}")