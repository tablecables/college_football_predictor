# feature engineering

FEATURES = [
    # Existing features
    {
        "name": "season",
        "description": "Year of the game",
        "type": "existing"
    },
    {
        "name": ,
        "description": ,
        "type": 
    },

    # Engineering features
    {
        "name": "win_rate_last_5",
        "description": "Win rate of the team in their last 5 games",
        "type": "engineered",
        "function": "calculate_win_rate_last_n"
    },


]



def get_feature_names(feature_type=None):
    if feature_type:
        return [f["name"] for f in FEATURES if f["type"] == feature_type]
    return [f["name"] for f in FEATURES]

def get_engineered_feature_functions():
    return {f["name"]: globals()[f["function"]] for f in FEATURES if f["type"] == "engineered"}