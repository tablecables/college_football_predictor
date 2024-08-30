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



## Action Items

**Data Collection**
-   [x] Get game data
-   [x] Get team data
-   [x] Get advanced team data
-   [x] Tons of data so limit to power five conferences for now: SEC, Big Ten, ACC, Big 12, Pac-12
    -   This reduces the number of games from 7k to 1k, much more manageable and probably more applicable
-   [x] New API pull with 2021-23
-   [x] Team talent composite
-   [ ] Pull 2024 data, did Pac-12 dissappear??
-   [ ] Pull extended game history for win rate later
-   [ ] Add in post-season data
    -   [ ] We have some championship games in regular data as per notes, confirm no overlap of games. When we go to create a post-season flag, which one is correct?
-   [ ] Get current season data, at least schedule and starting rosters
-   [ ] Decide how late we'll grab data from (20yrs?)

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
-   [ ] Revisit why we had null advanced stats for 2.5%, currently filtered out in data_cleaning
-   [ ] Convert data types: start_date, line_scores
-   [ ] Handle Outliers
-   [ ] Derived features: point difference, win column (1, 0), time-based features from start_date
-   [ ] Review and Validate

**Feature Engineering**
-   [x] Fix the team v team win rate function
-   [ ] MVP list of features

**Model Selection**

**Model Training**

**Model Evaluation**

**Predictions**
