# Business Intelligence Dashboard

A Streamlit-based dashboard for analyzing business data. This project provides a comprehensive dashboard for exploring and visualizing data, including summary statistics, time series analysis, segment analysis, and correlation analysis.

## Features

- **Summary Statistics**: Provides key metrics and summary statistics for numeric columns.
- **Time Series Analysis**: Analyzes data over different time periods (daily, weekly, monthly, quarterly, yearly).
- **Segment Analysis**: Breaks down data by different segments and visualizes the results.
- **Correlation Analysis**: Displays the correlation matrix between numeric columns.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/business-intelligence-dashboard.git
    cd business-intelligence-dashboard
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

### Running the Dashboard

1. Run the Streamlit application:

    ```bash
    streamlit run main.py
    ```

2. Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

### Using the Dashboard

- **Upload Data**: Use the file uploader to upload your CSV or Excel file. If no file is uploaded, the dashboard will use sample data.
- **Dashboard Controls**: Use the sidebar controls to select the time period, value column, segment column, and date range.
- **Summary Statistics**: View key metrics and summary statistics for the selected value column.
- **Time Series Analysis**: Visualize the selected value column over the chosen time period.
- **Segment Analysis**: Analyze the data by segments and visualize the top segments.
- **Correlation Analysis**: View the correlation matrix between numeric columns.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you have any suggestions or improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
