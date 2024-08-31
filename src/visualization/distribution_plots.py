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