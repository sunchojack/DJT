# GDELT vs DJT Stock Analysis

A newer version might be available at: [GitHub Repository](https://github.com/sunchojack/DJT).

A Python package for analyzing the relationship between GDELT news sentiment data and DJT (Trump Media & Technology Group) stock performance.
The initial idea was to explore whether positive media coverage of Trump correlates with better stock performance of his company DJT.
The output is two pipelines (GDELT and Yahoo stock data fetcher). The analysis is naive and mainly done for fun.
Can be extended for more serious research -- beyond just API data fetching.

## Features

- **Dual GDELT Support**: Fetch data via GDELT API (`gdeltdoc`) or direct GDELT access. Difference:
  - _GDELT API: A homebrewed wrapper around GDELT API for structured article data_
  - **[PREFERRED] Direct GDELT**: Full GKG V2 data access with local filtering
  
- **Stock Data Integration**: Yahoo Finance integration for stock data
- **Visualization**: Time series plots, scatter plots, and correlation heatmaps
- **Parallel Processing**: Efficient data fetching with configurable worker threads
- **Modular Architecture**: Clean separation of concerns with fetchers, processors, and analyzers
- **Analytics**: Correlation analysis, regression modeling, and lag analysis. Do not consider seriously in the current implementation.

Please mind that the legacy folder contains proper old scripts that were written by a human. 
I used opencode/GROK to repackage everything into a more production-ready version.

## Project Structure

```
DJT/
├── main.py                    # Main entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── config/
│   └── settings.py            # Configuration management
├── src/                       # Main source code
│   ├── __init__.py
│   ├── fetchers/              # Data fetching modules
│   │   ├── __init__.py
│   │   ├── base.py           # Base fetcher classes
│   │   ├── gdelt_api.py      # GDELT API fetcher using gdeltdoc
│   │   ├── gdelt_direct.py   # Direct GDELT fetcher using gdelt library
│   │   └── stock.py          # Stock data fetcher using yfinance
│   ├── processors/            # Data processing
│   │   ├── __init__.py
│   │   └── data_processor.py # GDELT and stock data processing
│   ├── analyzers/             # Data analysis
│   │   ├── __init__.py
│   │   └── data_analyzer.py  # Statistical analysis and visualization
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       └── helpers.py        # Helper functions
├── data/
│   └── results/               # Analysis results and plots
│       ├── analysis_results.json
│       ├── correlation_heatmap.png
│       ├── differences.png
│       ├── scatter.png
│       ├── stock_vs_tone.png
│       └── time_series.png
├── legacy/                    # Legacy scripts (deprecated)
│   ├── README.md              # Documentation of legacy scripts
│   ├── OTHER SCRIPTS          # Please check the Readme
│   └── ...
├── logs/                      # Application logs
│   └── gdelt_djt.log
└── .gitignore                 # Git ignore rules
```

## Installation

1. Clone or download the project
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the complete analysis - the tool will prompt for required inputs:

```bash
python main.py
```

### Command Line Options

```bash
python main.py [OPTIONS]

Options:
  --use-api              Use GDELT API instead of direct access
  --start-date DATE      Override prompted start date (YYYY-MM-DD)
  --end-date DATE        Override prompted end date (YYYY-MM-DD)
  --config PATH          Path to configuration file
  --parallel             Enable parallel processing [default: True]
  --no-plots             Disable plot generation
```

### Interactive Prompts

When you run the tool, it will prompt for:

1. **Start date**: Number of days ago (default: 90)
2. **End date**: Number of days ago (default: 0)
3. **Stock ticker**: Symbol like DJT, AAPL (required)
4. **Keywords**: Comma-separated search terms for GDELT (required)

### Examples

1. **Use GDELT API instead of direct access:**
```bash
python main.py --use-api
```

2. **Override date range via command line:**
```bash
python main.py --start-date 2024-03-01 --end-date 2024-05-31
```
*(Note: You will still be prompted for ticker and keywords)*

3. **Disable plot generation for faster processing:**
```bash
python main.py --no-plots
```

## Configuration

The analysis can be configured through:

1. **Command line arguments** (as shown above)
2. **Configuration file** (JSON format) 
3. **Code-level configuration** in `config/settings.py`

Key configuration options:

- **GDELT Settings**: API vs direct access, date ranges, keywords, worker threads
- **Stock Settings**: Tickers, companies, data intervals
- **Analysis Settings**: Visualization options, statistical analysis parameters
- **Logging Settings**: Log levels, file outputs

## Data Sources

### GDELT Data
- **Direct Access**: GDELT Knowledge Graph (GKG) table, version 2
- **API Access**: `gdeltdoc` library for structured article data
- **Coverage**: Global news with keyword and country filtering

### Stock Data
- **Source**: Yahoo Finance API via `yfinance`
- **Data**: OHLCV (Open, High, Low, Close, Volume) with adjusted close prices
- **Frequency**: Daily data by default

## Analysis Features

### Statistical Analysis
- **Correlation Analysis**: Pearson and Spearman correlations
- **Regression Analysis**: Linear regression with significance testing
- **Lag Analysis**: Cross-correlations with time lags
- **Difference Analysis**: Daily changes in sentiment and stock prices

### Visualizations
- **Time Series**: Dual-axis plots of sentiment vs stock prices
- **Scatter Plots**: Correlation scatter with regression lines
- **Heatmaps**: Correlation matrices
- **Difference Plots**: Daily change comparisons

### Data Processing
- **Sentiment Extraction**: From GDELT V2Tone strings
- **Date Alignment**: Merging datasets by date
- **Missing Data Handling**: Robust processing of incomplete data
- **Normalization**: Consistent date formatting and data types

## Output

The analysis generates:

1. **Processed Data**: CSV files with merged sentiment and stock data
2. **Visualizations**: PNG plots in `data/plots/` folder
3. **Analysis Results**: JSON file with statistical results
4. **Logs**: Detailed execution logs in `logs/` folder

## Dependencies

- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computing
- `matplotlib`: Basic plotting
- `seaborn`: Statistical visualization
- `scipy`: Statistical functions and tests
- `yfinance`: Yahoo Finance API
- `gdelt`: Direct GDELT access
- `gdeltdoc`: GDELT API wrapper
- `dask`: Parallel data processing (optional)

## Error Handling

The application includes comprehensive error handling:

- **API Failures**: Graceful degradation when APIs are unavailable
- **Missing Data**: Validation and reporting of missing required columns
- **Date Errors**: Validation of date ranges and formats
- **File System Errors**: Directory creation and file write protections
- **Network Issues**: Timeout and retry logic for API calls

## Performance Considerations

- **Parallel Processing**: Configurable thread pool for concurrent data fetching
- **Chunking**: Large date ranges processed in manageable chunks
- **Caching**: Avoid re-fetching existing data files
- **Memory Management**: Efficient DataFrame operations for large datasets

## Troubleshooting

### Common Issues

1. **GDELT API Limits**: Use direct access or reduce concurrent workers
2. **Yahoo Finance Limits**: Check ticker symbols and market hours
3. **Memory Issues**: Process data in smaller date ranges
4. **Missing Dependencies**: Install all requirements.txt packages

### Logging

Check `logs/gdelt_djt.log` for detailed error messages and debugging information.

## Contributing

The modular structure makes it easy to add:
- New data sources (additional fetchers)
- Analysis methods (extended analyzers)
- Processing steps (custom processors)
- Visualizations (new plot types)

## License

This project is provided as-is for educational and research purposes.