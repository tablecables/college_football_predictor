# TODO

## Current Action(s)
-   [ ] Two dataset output
-   [ ] Need to pull 2024 schedule separately, only pulls complete games
-   [x] Figure out duplicate rows in data_cleaning (12.8%)
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
-   [x] New API pull with 2021-24
-   [x] Team talent composite
-   [x] Pull 2001-2024 data
-   [ ] 2024 schedule for prediction (check pac-12)
-   [ ] Figure out where the duplicates are coming from, currently fixed in cleaning
-   [ ] Get coaches
-   [ ] Pull teams/matchup to replace history?
-   [ ] Add in post-season data
    -   [ ] We have some championship games in regular data as per notes, confirm no overlap of games. When we go to create a post-season flag, which one is correct?

-   [ ] Other Data to Consider
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
-   [ ] Convert any data types?
-   [ ] Revisit why we had null advanced stats for 2.5%, currently filtered out in data_cleaning
-   [ ] Handle Outliers?

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

-   [ ] Review against betting lines
-   [ ] Create a dashboard of some sort, maybe using Replit/Streamlit