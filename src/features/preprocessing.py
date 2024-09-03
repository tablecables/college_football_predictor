import pandas as pd
import numpy as np
from src.features.feature_eng import (
    FEATURES,
    get_engineered_feature_functions,
    get_feature_names
)

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all engineered features to the dataframe."""
    engineered_funcs = get_engineered_feature_functions()
    
    # Calculate all engineered features at once
    new_features = {}
    for feature_name, func in engineered_funcs.items():
        if feature_name not in df.columns:  # Only add if not already present
            try:
                new_features[feature_name] = func(df)
            except KeyError as e:
                print(f"Warning: Could not calculate {feature_name}. Missing column: {str(e)}")
    
    # Create a new DataFrame with engineered features and concatenate with original
    engineered_df = pd.DataFrame(new_features, index=df.index)
    return pd.concat([df, engineered_df], axis=1)

def select_features(df: pd.DataFrame, selected_features: list = None) -> pd.DataFrame:
    """Select specified features from the dataframe."""
    if selected_features is None:
        selected_features = get_feature_names()
    
    # Only select features that exist in the dataframe
    existing_features = [f for f in selected_features if f in df.columns]
    return df[existing_features]

def preprocess_data(df: pd.DataFrame, selected_features: list = None) -> pd.DataFrame:
    """Main function to preprocess data: engineer features and select them."""
    df = engineer_features(df)  # Engineer features first
    df = select_features(df, selected_features)  # Then select features
    return df

# You might add more preprocessing steps here, like handling missing values,
# encoding categorical variables, etc.