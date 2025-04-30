import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

# Set page config
st.set_page_config(
    page_title="Business Intelligence Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
    .sidebar .sidebar-content {
        background-color: #e9ecef;
    }
    h1 {
        color: #2c3e50;
    }
    </style>
    """, unsafe_allow_html=True)

class DataAnalyzer:
    def __init__(self, data_path: str):
        self.data = self.load_data(data_path)
        self.clean_data()
        
    def load_data(self, path: str) -> pd.DataFrame:
        """Load data from CSV or Excel file"""
        if path.endswith('.csv'):
            return pd.read_csv(path)
        elif path.endswith(('.xls', '.xlsx')):
            return pd.read_excel(path)
        else:
            raise ValueError("Unsupported file format. Please provide CSV or Excel file.")
    
    def clean_data(self):
        """Basic data cleaning"""
        # Standardize column names
        self.data.columns = [col.lower().replace(' ', '_') for col in self.data.columns]
        
        # Convert date columns if present
        if 'date' in self.data.columns:
            self.data['date'] = pd.to_datetime(self.data['date'])
            
        # Fill numeric NA values with 0
        numeric_cols = self.data.select_dtypes(include=['number']).columns
        self.data[numeric_cols] = self.data[numeric_cols].fillna(0)
    
    def get_summary_stats(self) -> pd.DataFrame:
        """Generate comprehensive statistics"""
        numeric_cols = self.data.select_dtypes(include=['number']).columns
        return self.data[numeric_cols].describe().transpose()
    
    def time_period_analysis(self, time_col: str, value_col: str, period: str = 'M') -> pd.DataFrame:
        """Analyze data by time period (D, W, M, Q, Y)"""
        if time_col not in self.data.columns:
            raise ValueError(f"Column '{time_col}' not found in data")
            
        return self.data.groupby(pd.Grouper(key=time_col, freq=period))[value_col].agg(['sum', 'mean', 'count'])
    
    def segment_analysis(self, segment_col: str, value_col: str) -> pd.DataFrame:
        """Analyze data by segments"""
        return self.data.groupby(segment_col)[value_col].agg(['sum', 'mean', 'count', 'std']).sort_values('sum', ascending=False)
    
    def correlation_analysis(self) -> pd.DataFrame:
        """Calculate correlation matrix"""
        numeric_cols = self.data.select_dtypes(include=['number']).columns
        return self.data[numeric_cols].corr()

class BIDashboard:
    def __init__(self, analyzer: DataAnalyzer):
        self.analyzer = analyzer
        self.setup_sidebar()
        
    def setup_sidebar(self):
        """Configure sidebar controls"""
        st.sidebar.title("Dashboard Controls")
        
        # Time period selector
        self.time_period = st.sidebar.selectbox(
            "Time Period",
            ["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"],
            index=2
        )
        
        # Value column selector
        numeric_cols = self.analyzer.data.select_dtypes(include=['number']).columns.tolist()
        self.value_column = st.sidebar.selectbox(
            "Value Column",
            numeric_cols,
            index=0
        )
        
        # Segment column selector
        all_cols = self.analyzer.data.columns.tolist()
        self.segment_column = st.sidebar.selectbox(
            "Segment By",
            [col for col in all_cols if col != self.value_column],
            index=0
        )
        
        # Date range filter (if date column exists)
        if 'date' in self.analyzer.data.columns:
            min_date = self.analyzer.data['date'].min().date()
            max_date = self.analyzer.data['date'].max().date()
            self.date_range = st.sidebar.date_input(
                "Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
    
    def display_summary_stats(self):
        """Show summary statistics"""
        st.header("Summary Statistics")
        stats = self.analyzer.get_summary_stats()
        st.dataframe(stats.style.format("{:,.2f}").background_gradient(cmap='Blues'))
        
        # KPI cards
        st.subheader("Key Metrics")
        total = stats.loc[self.value_column, 'mean']
        count = stats.loc[self.value_column, 'count']
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Records", f"{count:,.0f}")
        col2.metric(f"Average {self.value_column.title()}", f"{total:,.2f}")
        col3.metric("Standard Deviation", f"{stats.loc[self.value_column, 'std']:,.2f}")
    
    def display_time_series(self):
        """Show time series analysis"""
        st.header("Time Series Analysis")
        
        if 'date' not in self.analyzer.data.columns:
            st.warning("No date column found in dataset")
            return
            
        # Map period selection to pandas frequency
        period_map = {
            "Daily": "D",
            "Weekly": "W",
            "Monthly": "M",
            "Quarterly": "Q",
            "Yearly": "Y"
        }
        
        # Filter by date range if available
        filtered_data = self.analyzer.data
        if hasattr(self, 'date_range') and len(self.date_range) == 2:
            start_date, end_date = self.date_range
            filtered_data = filtered_data[
                (filtered_data['date'].dt.date >= start_date) & 
                (filtered_data['date'].dt.date <= end_date)
            ]
        
        # Time series analysis
        time_series = filtered_data.groupby(
            pd.Grouper(key='date', freq=period_map[self.time_period])
        )[self.value_column].sum().reset_index()
        
        # Plot
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.lineplot(data=time_series, x='date', y=self.value_column, ax=ax)
        ax.set_title(f"{self.value_column.title()} by {self.time_period}")
        ax.set_xlabel("Date")
        ax.set_ylabel(self.value_column.title())
        plt.xticks(rotation=45)
        st.pyplot(fig)
        
        # Show data table
        st.dataframe(time_series.style.format({
            'date': lambda x: x.strftime('%Y-%m-%d'),
            self.value_column: "{:,.2f}"
        }))
    
    def display_segment_analysis(self):
        """Show segment analysis"""
        st.header("Segment Analysis")
        
        segment_data = self.analyzer.segment_analysis(
            self.segment_column,
            self.value_column
        ).reset_index()
        
        # Plot top 10 segments
        fig, ax = plt.subplots(figsize=(12, 6))
        top_segments = segment_data.head(10)
        sns.barplot(
            data=top_segments,
            x=self.segment_column,
            y='sum',
            ax=ax,
            palette='Blues_d'
        )
        ax.set_title(f"{self.value_column.title()} by {self.segment_column.title()}")
        ax.set_xlabel(self.segment_column.title())
        ax.set_ylabel(f"Total {self.value_column.title()}")
        plt.xticks(rotation=45)
        st.pyplot(fig)
        
        # Show full segment data
        st.dataframe(segment_data.style.format({
            'sum': "{:,.2f}",
            'mean': "{:,.2f}",
            'std': "{:,.2f}"
        }))
    
    def display_correlation_analysis(self):
        """Show correlation between numeric columns"""
        st.header("Correlation Analysis")
        
        corr_matrix = self.analyzer.correlation_analysis()
        
        # Plot heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(
            corr_matrix,
            annot=True,
            fmt=".2f",
            cmap='coolwarm',
            center=0,
            ax=ax
        )
        ax.set_title("Correlation Matrix")
        st.pyplot(fig)
    
    def run(self):
        """Run the dashboard"""
        self.display_summary_stats()
        st.markdown("---")
        self.display_time_series()
        st.markdown("---")
        self.display_segment_analysis()
        st.markdown("---")
        self.display_correlation_analysis()

# Sample data generation (replace with your actual data loading)
@st.cache_data
def load_sample_data():
    """Generate sample sales data if no file uploaded"""
    dates = pd.date_range(start='2022-01-01', end='2023-12-31', freq='D')
    products = ['Electronics', 'Clothing', 'Home Goods', 'Grocery']
    regions = ['North', 'South', 'East', 'West']
    
    data = pd.DataFrame({
        'date': np.random.choice(dates, size=1000),
        'product': np.random.choice(products, size=1000),
        'region': np.random.choice(regions, size=1000),
        'sales_amount': np.random.normal(100, 30, size=1000).round(2),
        'units_sold': np.random.randint(1, 10, size=1000),
        'customer_id': np.random.randint(1000, 9999, size=1000)
    })
    return data

def main():
    st.title("Business Intelligence Dashboard")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload your data file (CSV or Excel)",
        type=['csv', 'xlsx']
    )
    
    if uploaded_file is not None:
        analyzer = DataAnalyzer(uploaded_file)
    else:
        st.info("Using sample data. Upload a file to analyze your own data.")
        sample_data = load_sample_data()
        analyzer = DataAnalyzer("sales_data.csv")  # This is just for the interface
        analyzer.data = sample_data  # Replace with our generated data
    
    dashboard = BIDashboard(analyzer)
    dashboard.run()

if __name__ == "__main__":
    main()