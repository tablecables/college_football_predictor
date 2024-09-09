# Data Cleaning Decisions

## Overview
This document outlines the key decisions made during the data cleaning process for the College Football Predictor project.

## Data Completeness
-   2001+: Game Data
    -   Attendance 2004, 2005, 2009-2011. Assuming 2020 is COVID numbers
-   2004+: Team Game Stats
    -   Some data 2016+
-   2001+: Advanced Stats
-   2015+: Team Talent
-   2013+: Betting Lines
    -   2013+: Pregame win probability, although also null 50% of the time...
    -   Moneyline null < 2021

## Handling Duplicates

-   Issue: After pulling the larger API datset, 2001-2024, we have a bunch of duplicate rows after merging (12.8%), which exist in the raw data from the API (7.6% of games, 5% of team_stats, and 0.14% of team_talent)
-   Decision: Drop duplicates from raw dataframes before merging
-   Rationale: This persisted even with a refactor of using the API. Confident issue is on the public dataset.

## Handling Missing Values

### Notes and Highlights
-   Issue: Null for 99% and 78% of rows.
-   Decision: Drop these columns
-   Rationale: Notes are mentioning something special about the game and highlights link to youtube links. Neither are scalable and are mostly null, so we're not losing much value here.

### Null team_stats_df
-   Issues: ~10% of rows have null values where we would be merging team_stats_df.
-   Decision: Drop these rows
-   Rationale: I tried to see if I could directly pull these games from the API by game id, and they returned null results. So we're empty at the source, let's just drop. We can always get more data with post-season games etc. later on. Note that advanced stats was missing from 40% of these rows as well, so not much we could recover.

### Fumbles [fumblesRecovered, fumblesLost, totalFumbles]
-   Issue: Many rows where total is null, but lost and recovered are not
-   Decision: Make totalFumbles the sum of the two other rows.
-   Rationale: Looks like a case of messy data. There are many rows where total is the sum of recovered and lost.

### Advanced Stats Columns
- Issue: About 1.4% of games at this point have null values for the advanced stats.
- Decision: Drop rows where all the advanced stats are null
- Rationale: Not losing a ton of data here, and we want advanced stats to be a main part of the features, so we'll filter around them. Note this is distributed over many years, so not a late start in the dataset like other columns.

### Null or 0 before Data 
- Issue: Excitement index is null before 2014 and a range of data is null before 2015 (qbHurries, passesDeflected, sacks, tackles, defensiveTDs, tacklesForLoss, team talent data). Attendance is 0 for 2011 and a few years earlier. Some data in mostly null pre-2009 (kickReturns, kickReturnYards, kickReturnTDs)
- Decision: Create two interim datasets. One that excludes 2015 and earlier, one that excludes the the null columns
- Rationale: This way we can create two separate models and ensemble them later, while also not complicating things too much with the gaps in data (ie: not 4 different data sets with different cutoffs, just one cutoff)

### Columns to fill to 0
-   Columns: passesIntercepted, interceptionYards, interceptionTDs, puntReturns, puntReturnYards, kickingPoints, passingTDs, rushingTDs
-   Decision: Fill with 0
-   Rationale: Intuitively can be 0, but in the data show up as nulls. Also groupings of similar data had the same null amounts, but didn't match other rows. Interceptions can be uncommon. Same with punt returns (touchbacks and fair catches negate them).

### Null venue_id and venue
-   Issue: Matching % of venue_id and venue nulls (~2.5%).
-   Decision: Give -1 for id and "Unknown Venue" for name.
-   Rationale: Likely a range of random non-standard venues. Shortcut to standardize these missing games.

## Columns to fill with Median
-   Columns: attendance, offense_open_field_yards, offense_open_field_yards_total, defense_open_field_yards, defense_open_field_yards_total, offense_second_level_yards, offense_second_level_yards_total, defense_second_level_yards, defense_second_level_yards_total, offense_rushing_plays.explosiveness, offense_standard_downs.explosiveness, defense_rushing_plays.explosiveness, defense_standard_downs.explosiveness, offense_passing_downs.explosiveness, offense_passing_plays.explosiveness, defense_passing_downs.explosiveness, defense_passing_plays.explosiveness, possessionTime, offense_passing_plays.ppa, offense_passing_plays.total_ppa, defense_passing_plays.ppa, defense_passing_plays.total_ppa, offense_explosiveness, defense_explosiveness
-   Decision: fill with specific median (season, venue, team, etc.) where possible, then season level for team
-   Rationale: Data points that could be uniquely untracked, but with decent distribution and tracking in the rest of the data set.

## Null Conference & Division
-   Issue: Two games (four rows) with null conference and division.
-   Decision: Drop these rows.
-   Rationale: Low frequency and relevency.