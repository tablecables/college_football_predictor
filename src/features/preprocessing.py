import pandas as pd
from src.features.feature_eng import FEATURES, get_engineered_feature_functions

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all engineered features to the dataframe."""
    engineered_funcs = get_engineered_feature_functions()
    
    for feature_name, func in engineered_funcs.items():
        df[feature_name] = func(df)
    
    return df

def select_features(df: pd.DataFrame, selected_features: list = None) -> pd.DataFrame:
    """Select specified features from the dataframe."""
    if selected_features is None:
        selected_features = [f['name'] for f in FEATURES]
    
    return df[selected_features]

def preprocess_data(df: pd.DataFrame, selected_features: list = None) -> pd.DataFrame:
    """Main function to preprocess data: engineer features and select them."""
    df = engineer_features(df)
    df = select_features(df, selected_features)
    return df

# You might add more preprocessing steps here, like handling missing values,
# encoding categorical variables, etc.