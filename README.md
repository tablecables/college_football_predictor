# College Football Predictor 2024

## Overview

I joined a college football pool this year with a few friends. I thought it would be fun to try and use machine learning to make picks. Goal is to make two models:

1.  win_probability_model: to predict the probability of each team winning a specific matchup
2.  score_prediction_model: to predict the final score for both teams in a specific game

## Outline

1. Scrape data from the [CollegeFootballData.com API](https://collegefootballdata.com/)
2. Clean and process the data
3. Explore the data and create features
4. Build a model to predict the outcome of each game
...
-   Review against betting lines
-   Create a dashboard of some sort, maybe using Replit/Streamlit

## Current Action
-   [x] Monitor 2001-2024 API pull
-   [ ] Need to pull 2024 schedule separately, only pulls complete games
-   [ ] Figure out duplicate rows in data_cleaning (12.8%)
-   [ ] Start EDA
-   [ ] Feature engineering some time based values
-   [ ] Structure model selection to a few key model sections
-   [x] Clean up (multiple data folders, maybe model folder)


## Action Items

**Data Collection**
-   [x] Get game data
-   [x] Get team data
-   [x] Get advanced team data
-   [x] Tons of data so limit to power five conferences for now: SEC, Big Ten, ACC, Big 12, Pac-12
    -   This reduces the number of games from 7k to 1k, much more manageable and probably more applicable
-   [x] New API pull with 2021-23
-   [x] Team talent composite
-   [ ] Pull 2001-2024 data
-   [ ] Pull 2024 data, did Pac-12 dissappear??
-   [ ] Get coaches
-   [ ] Pull teams/matchup to replace history?
-   [ ] Add in post-season data
    -   [ ] We have some championship games in regular data as per notes, confirm no overlap of games. When we go to create a post-season flag, which one is correct?

-   [ ] Other Data to Consider
    -   [ ] Longer history of games for win rate data
    -   [ ] Coach Information
    -   [ ] Betting Lines
    -   [ ] Player level data


**Data Cleaning**

-   [x] Join game data to team game data
-   [x] Join advanced team data
-   [x] Join team talent composite
-   [x] Investigating null values, currently the 2.4% null advanced stats. I think some are teams outside the Power 5
    -   [x] Check if all games are exclusive of those with no nulls
-   [x] Create a team_id, team_name legend in utils
-   [x] Put a team and team_id dictionary in utils
-   [ ] Check what is in 2024 data
-   [ ] Revisit why we had null advanced stats for 2.5%, currently filtered out in data_cleaning
-   [ ] Convert data types: start_date, line_scores
-   [ ] Handle Outliers
-   [ ] Derived features: point difference, win column (1, 0), time-based features from start_date
-   [ ] Review and Validate

**Exploratory Data Analysis**

1. Data Distribution
-   [ ] Basic statistical summary
-   [ ] Histograms for numerical variables
-   [ ] Box plots to identify outliers
-   [ ] Q-Q plots for normality
2. Categorical
-   [ ] Unique values in categorical columns
-   [ ] Bar plots for categorical variables
3. Correlation Analysis
-   [ ] Correlation matrix
-   [ ] Visualize correlations with a heatmap
4. Time-based Analysis
-   [ ] Analyze trends over seasons
-   [ ] Performance by week within seasons
5. Team Performance Analysis
-   [ ] Home vs away performance
-   [ ] Win rates for teams
6. Advanced Stats
-   [ ] Explore impact of advanced stats on game outcomes
7. Feature Insights
-   [ ] Review key feature/target relationships
-   [ ] List potential features for modeling

**Feature Engineering**
-   [x] Fix the team v team win rate function
-   [x] MVP list of features

**Model Selection & Training**




**Model Evaluation**

**Predictions**
