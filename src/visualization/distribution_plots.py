import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

def analyze_distribution(df, column_name):

    # Create a histogram with a density plot
    plt.figure(figsize=(12, 6))
    sns.histplot(df[column_name].dropna(), kde=True)
    plt.title(f'Distribution of {column_name}')
    plt.xlabel(column_name)
    plt.ylabel('Frequency')

    # Add a normal distribution line for comparison
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = stats.norm.pdf(x, df[column_name].mean(), df[column_name].std())
    plt.plot(x, p * df[column_name].dropna().shape[0] * (xmax - xmin) / 100, 'k', linewidth=2)

    plt.show()

    # Perform Shapiro-Wilk test for normality
    statistic, p_value = stats.shapiro(df[column_name].dropna())
    print(f"Shapiro-Wilk test - statistic: {statistic:.4f}, p-value: {p_value:.4f}")

    # Calculate skewness and kurtosis
    skewness = df[column_name].skew()
    kurtosis = df[column_name].kurtosis()
    print(f"Skewness: {skewness:.4f}")
    print(f"Kurtosis: {kurtosis:.4f}")

def visualize_null_values(df):

    null_columns = df.columns[df.isnull().any()].tolist()
    null_percentages = df[null_columns].isnull().mean().sort_values(ascending=False) * 100

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 15))
    fig.patch.set_facecolor('#f0f0f0')

    sns.heatmap(df[null_columns].isnull(), cmap='YlGnBu', cbar=False, ax=ax1)
    ax1.set_title('Distribution of Null Values', fontsize=16, fontweight='bold')
    ax1.set_xlabel('Columns', fontsize=12)
    ax1.set_ylabel('Rows', fontsize=12)
    ax1.set_xticks([])
    ax1.set_yticks([])

    null_percentages.plot(kind='barh', ax=ax2)
    ax2.set_title('Percentage of Null Values by Column', fontsize=16, fontweight='bold')
    ax2.set_xlabel('Percentage of Null Values', fontsize=12)
    ax2.set_ylabel('Columns', fontsize=12)

    for i, v in enumerate(null_percentages):
        ax2.text(v + 0.5, i, f'{v:.1f}%', va='center', fontsize=10)

    plt.tight_layout()
    fig.patch.set_edgecolor('black')
    fig.patch.set_linewidth(2)

    plt.show()

    print("Columns with null values (sorted by percentage, descending):")
    for col, percentage in null_percentages.items():
        null_count = df[col].isnull().sum()
        print(f"{col}: {null_count} null values ({percentage:.2f}%)")

def plot_mean_over_time(df, column_name):
    # Group by season and calculate mean
    mean_by_season = df.groupby('season')[column_name].mean().reset_index()
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    plt.plot(mean_by_season['season'], mean_by_season[column_name], marker='o')
    
    plt.title(f'Mean {column_name} Over Time')
    plt.xlabel('Season')
    plt.ylabel(f'Mean {column_name}')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Add value labels on the points
    for x, y in zip(mean_by_season['season'], mean_by_season[column_name]):
        plt.annotate(f'{y:.2f}', (x, y), textcoords="offset points", xytext=(0,10), ha='center')
    
    plt.tight_layout()
    plt.show()

def plot_null_frequency_by_season(df, columns_to_analyze):
    """
    Plot the null frequency by season for specified columns.

    Args:
    df (pd.DataFrame): The dataframe to analyze
    columns_to_analyze (list): List of column names to analyze

    Returns:
    None
    """
    def null_frequency_by_season(df, column):
        return df.groupby('year')[column].apply(lambda x: x.isnull().sum()) / df.groupby('year').size() * 100

    for column in columns_to_analyze:
        null_freq = null_frequency_by_season(df, column)
        
        plt.figure(figsize=(12, 6))
        null_freq.plot(kind='bar')
        plt.title(f'Null Frequency by Season for {column}')
        plt.xlabel('Season')
        plt.ylabel('Null Frequency (%)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

def plot_zero_values_by_year(df, column_name):
    """
    Plot the percentage of zero values by year for a specified column.

    Args:
    df (pd.DataFrame): The dataframe containing the column to analyze and 'season' column
    column_name (str): The name of the column to analyze

    Returns:
    None
    """
    # Calculate percentage of zero values by year
    zero_values_by_year = df[df[column_name] == 0].groupby('year').size() / df.groupby('year').size() * 100

    # Plot percentage of zero values by year
    plt.figure(figsize=(12, 6))
    zero_values_by_year.plot(kind='bar')
    plt.title(f'Percentage of Zero {column_name} by Year')
    plt.xlabel('Year')
    plt.ylabel(f'Percentage of Zero {column_name}')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
