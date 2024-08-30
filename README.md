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
-   [ ] First attempt at joining dataframes in data_cleaning
    -   Join logic is a bit weird, need to think about it a bit more
    -   There are duplicates, random nulls, etc.


## Action Items

**Data Collection**
-   [x] Get game data
-   [x] Get team data
-   [x] Get advanced team data
-   [x] Tons of data so limit to power five conferences for now: SEC, Big Ten, ACC, Big 12, Pac-12
    -   This reduces the number of games from 7k to 1k, much more manageable and probably more applicable
-   [ ] Add in post-season data
    -   [ ] We have some championship games in regular data as per notes, confirm no overlap of games. When we go to create a post-season flag, which one is correct?
-   [ ] Get current season data, at least schedule and starting rosters
-   [ ] Decide how late we'll grab data from (20yrs?)

-   [ ] Other Data to Consider
    -   [ ] Coach Information
    -   [ ] Betting Lines
    -   [ ] Team Talent Composite
    -   [ ] Player level data


**Data Cleaning**

- [ ] Review what we have with game data
- [ ] Scope other data that we'll use like Player Data, Coach Data, etc.

**Model Selection**
