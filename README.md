# College Football Predictor 2024

## Overview

I joined a college football pool this year with a few friends. I thought it would be fun to try and use machine learning to make picks that win more than 50% of the time.

## Outline

1. Scrape data from the [CollegeFootballData.com API](https://collegefootballdata.com/)
2. Clean and process the data
3. Explore the data and create features
4. Build a model to predict the outcome of each game
...
-   Review against betting lines
-   Create a dashboard of some sort, maybe using Replit/Streamlit

## Action Items

**Data Collection**
-   [x] Get game data
-   [x] Tons of data so limit to power five conferences for now: SEC, Big Ten, ACC, Big 12, Pac-12
    -   This reduces the number of games from 7k to 1k, much more manageable and probably more applicable
-   [ ] Add in post-season data
-   [ ] Add in player level data
    -   [ ] *Fix fetch player data function*
    -   [ ] We have some championship games in regular data as per notes, confirm no overlap of games. When we go to create a post-season flag, which one is correct?
-   [ ] Get current season data, at least schedule and starting rosters
-   [ ] Decide how late we'll grab data from (20yrs?)
-   [ ] Scope of additional data?

**Data Cleaning**

- [ ] Review what we have with game data
- [ ] Scope other data that we'll use like Player Data, Coach Data, etc.
