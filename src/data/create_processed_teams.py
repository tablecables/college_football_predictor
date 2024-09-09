# Create Processed Teams

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

def create_processed_teams_db(source_db_path, target_db_path):
    print(f"Source DB path: {source_db_path}")
    print(f"Target DB path: {target_db_path}")
    
    # Connect to the source and target databases
    source_conn = sqlite3.connect(source_db_path)
    source_cursor = source_conn.cursor()
    target_conn = sqlite3.connect(target_db_path)
    target_cursor = target_conn.cursor()

    # Check if the transformed_teams table exists in the source database
    source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transformed_teams';")
    if not source_cursor.fetchone():
        raise ValueError("transformed_teams table not found in the source database")

    # SQL query to clean and process the data
    clean_data_query = """
    WITH team_info AS (
        SELECT team, 
               MAX(team_conference) AS team_conference, 
               MAX(team_division) AS team_division
        FROM transformed_teams
        WHERE team_conference IS NOT NULL AND team_conference != ''
          AND team_division IS NOT NULL AND team_division != ''
        GROUP BY team
    ),
    cleaned_data AS (
        SELECT t.*,
            COALESCE(t.team_conference, ti.team_conference, 'Unknown') AS team_conference,
            COALESCE(t.team_division, ti.team_division, 'Unknown') AS team_division,
            COALESCE(t.opponent_conference, oi.team_conference, 'Unknown') AS opponent_conference,
            COALESCE(t.opponent_division, oi.team_division, 'Unknown') AS opponent_division,
            CASE 
                WHEN attendance = 0 THEN NULL
                ELSE attendance
            END AS cleaned_attendance,
            CASE 
                WHEN possessionTime IS NULL THEN NULL
                WHEN possessionTime LIKE '%:%' THEN 
                    CAST(SUBSTR(possessionTime, 1, INSTR(possessionTime, ':') - 1) AS FLOAT) +
                    CAST(SUBSTR(possessionTime, INSTR(possessionTime, ':') + 1) AS FLOAT) / 60.0
                ELSE CAST(possessionTime AS FLOAT) / 60.0
            END AS possession_time_minutes,
            CAST(SUBSTR(thirdDownEff, 1, INSTR(thirdDownEff, '-') - 1) AS FLOAT) / 
                CAST(SUBSTR(thirdDownEff, INSTR(thirdDownEff, '-') + 1) AS FLOAT) AS thirdDownPct,
            CAST(SUBSTR(fourthDownEff, 1, INSTR(fourthDownEff, '-') - 1) AS FLOAT) / 
                CAST(SUBSTR(fourthDownEff, INSTR(fourthDownEff, '-') + 1) AS FLOAT) AS fourthDownPct,
            CAST(SUBSTR(completionAttempts, 1, INSTR(completionAttempts, '-') - 1) AS FLOAT) / 
                CAST(SUBSTR(completionAttempts, INSTR(completionAttempts, '-') + 1) AS FLOAT) AS completionPct,
            CAST(SUBSTR(totalPenaltiesYards, 1, INSTR(totalPenaltiesYards, '-') - 1) AS INTEGER) AS penalties,
            CAST(SUBSTR(totalPenaltiesYards, INSTR(totalPenaltiesYards, '-') + 1) AS INTEGER) AS penaltyYards
        FROM transformed_teams t
        LEFT JOIN team_info ti ON t.team = ti.team
        LEFT JOIN team_info oi ON t.opponent = oi.team
    ),
    yearly_avg_excitement AS (
    SELECT year, AVG(excitement_index) AS avg_excitement
    FROM cleaned_data
    WHERE excitement_index IS NOT NULL
        GROUP BY year
    )
    SELECT 
        id, year, week, season_type, start_date, completed, neutral_site,
        COALESCE(conference_game, 
            CASE 
                WHEN team_conference = opponent_conference THEN 1
                ELSE 0
            END
        ) AS conference_game,
        COALESCE(cleaned_attendance, 
            (SELECT AVG(cleaned_attendance) FROM cleaned_data c2 
             WHERE c2.year = cleaned_data.year AND c2.venue_id = cleaned_data.venue_id),
            (SELECT AVG(cleaned_attendance) FROM cleaned_data c3 
             WHERE c3.year = cleaned_data.year AND c3.team = cleaned_data.team),
            (SELECT AVG(cleaned_attendance) FROM cleaned_data c4 
             WHERE c4.year = cleaned_data.year)
        ) AS attendance,
        COALESCE(venue_id, -1) AS venue_id,
        COALESCE(venue, 'Unknown Venue') AS venue,
        team_id, team, team_conference, team_division, team_points,
        opponent_id, opponent, opponent_conference, opponent_division, opponent_points,
        CAST(home_away = 'home' AS INTEGER) AS is_home,
        CASE 
        WHEN year > 2013 AND completed = 1 AND excitement_index IS NULL THEN 
            (SELECT avg_excitement 
             FROM yearly_avg_excitement y 
             WHERE y.year = cleaned_data.year)
            ELSE excitement_index
        END AS excitement_index,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(fumblesLost, 0)
            ELSE fumblesLost
        END AS fumblesLost,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(fumblesRecovered, 0)
            ELSE fumblesRecovered
        END AS fumblesRecovered,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(fumblesLost, 0) + COALESCE(fumblesRecovered, 0)
            ELSE fumblesLost + fumblesRecovered
        END AS totalFumbles,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(puntReturnYards, 0)
            ELSE puntReturnYards
        END AS puntReturnYards,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(puntReturnTDs, 0)
            ELSE puntReturnTDs
        END AS puntReturnTDs,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(puntReturns, 0)
            ELSE puntReturns
        END AS puntReturns,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(kickingPoints, 0)
            ELSE kickingPoints
        END AS kickingPoints,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(interceptionYards, 0)
            ELSE interceptionYards
        END AS interceptionYards,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(interceptionTDs, 0)
            ELSE interceptionTDs
        END AS interceptionTDs,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(passesIntercepted, 0)
            ELSE passesIntercepted
        END AS passesIntercepted,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(passingTDs, 0)
            ELSE passingTDs
        END AS passingTDs,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(rushingTDs, 0)
            ELSE rushingTDs
        END AS rushingTDs,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(penalties, 0)
            ELSE penalties
        END AS penalties,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(penaltyYards, 0)
            ELSE penaltyYards
        END AS penaltyYards,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(firstDowns, 0)
            ELSE firstDowns
        END AS firstDowns,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(totalYards, 0)
            ELSE totalYards
        END AS totalYards,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(netPassingYards, 0)
            ELSE netPassingYards
        END AS netPassingYards,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(yardsPerPass, 0)
            ELSE yardsPerPass
        END AS yardsPerPass,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(rushingYards, 0)
            ELSE rushingYards
        END AS rushingYards,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(rushingAttempts, 0)
            ELSE rushingAttempts
        END AS rushingAttempts,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(yardsPerRushAttempt, 0)
            ELSE yardsPerRushAttempt
        END AS yardsPerRushAttempt,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(turnovers, 0)
            ELSE turnovers
        END AS turnovers,
        CASE
            WHEN year >= 2004 AND completed = 1
            THEN COALESCE(interceptions, 0)
            ELSE interceptions
        END AS interceptions,
        CASE
            WHEN year >= 2009 AND completed = 1
            THEN COALESCE(kickReturnYards, 0)
            ELSE kickReturnYards
        END AS kickReturnYards,
        CASE
            WHEN year >= 2009 AND completed = 1
            THEN COALESCE(kickReturnTDs, 0)
            ELSE kickReturnTDs
        END AS kickReturnTDs,
        CASE
            WHEN year >= 2009 AND completed = 1
            THEN COALESCE(kickReturns, 0)
            ELSE kickReturns
        END AS kickReturns,
        CASE
            WHEN year >= 2016 AND completed = 1
            THEN COALESCE(tacklesForLoss, 0)
            ELSE tacklesForLoss
        END AS tacklesForLoss,
        CASE
            WHEN year >= 2016 AND completed = 1
            THEN COALESCE(tackles, 0)
            ELSE tackles
        END AS tackles,
        CASE
            WHEN year >= 2016 AND completed = 1
            THEN COALESCE(defensiveTDs, 0)
            ELSE defensiveTDs
        END AS defensiveTDs,
        CASE
            WHEN year >= 2016 AND completed = 1
            THEN COALESCE(sacks, 0)
            ELSE sacks
        END AS sacks,
        CASE
            WHEN year >= 2016 AND completed = 1
            THEN COALESCE(qbHurries, 0)
            ELSE qbHurries
        END AS qbHurries,
        CASE
            WHEN year >= 2016 AND completed = 1
            THEN COALESCE(passesDeflected, 0)
            ELSE passesDeflected
        END AS passesDeflected,
        COALESCE(possession_time_minutes, 
            (SELECT AVG(possession_time_minutes) FROM cleaned_data c2 
             WHERE c2.year = cleaned_data.year AND c2.team = cleaned_data.team),
            (SELECT AVG(possession_time_minutes) FROM cleaned_data)
        ) AS possessionMinutes,
        COALESCE(thirdDownPct, 
            (SELECT AVG(thirdDownPct) FROM cleaned_data c2 
             WHERE c2.year = cleaned_data.year)) AS thirdDownPct,
        COALESCE(fourthDownPct, 
            (SELECT AVG(fourthDownPct) FROM cleaned_data c2 
             WHERE c2.year = cleaned_data.year)) AS fourthDownPct,
        COALESCE(completionPct, 
            (SELECT AVG(completionPct) FROM cleaned_data c2 
             WHERE c2.year = cleaned_data.year)) AS completionPct,
        json_extract(team_line_scores, '$[0]') AS team_score_first,
        json_extract(team_line_scores, '$[1]') AS team_score_second,
        json_extract(team_line_scores, '$[2]') AS team_score_third,
        json_extract(team_line_scores, '$[3]') AS team_score_fourth,
        json_extract(opponent_line_scores, '$[0]') AS opponent_score_first,
        json_extract(opponent_line_scores, '$[1]') AS opponent_score_second,
        json_extract(opponent_line_scores, '$[2]') AS opponent_score_third,
        json_extract(opponent_line_scores, '$[3]') AS opponent_score_fourth,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_plays,
                (SELECT AVG(offense_plays) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_plays) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_plays)
            ELSE offense_plays
        END AS offense_plays,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_drives,
                (SELECT AVG(offense_drives) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_drives) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_drives)
            ELSE offense_drives
        END AS offense_drives,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_ppa,
                (SELECT AVG(offense_ppa) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_ppa) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_ppa)
            ELSE offense_ppa
        END AS offense_ppa,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_total_ppa,
                (SELECT AVG(offense_total_ppa) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_total_ppa) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_total_ppa)
            ELSE offense_total_ppa
        END AS offense_total_ppa,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_success_rate,
                (SELECT AVG(offense_success_rate) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_success_rate) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_success_rate)
            ELSE offense_success_rate
        END AS offense_success_rate,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_explosiveness,
                (SELECT AVG(offense_explosiveness) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_explosiveness) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_explosiveness)
            ELSE offense_explosiveness
        END AS offense_explosiveness,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_power_success,
                (SELECT AVG(offense_power_success) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_power_success) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_power_success)
            ELSE offense_power_success
        END AS offense_power_success,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_stuff_rate,
                (SELECT AVG(offense_stuff_rate) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_stuff_rate) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_stuff_rate)
            ELSE offense_stuff_rate
        END AS offense_stuff_rate,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_line_yards,
                (SELECT AVG(offense_line_yards) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_line_yards) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_line_yards)
            ELSE offense_line_yards
        END AS offense_line_yards,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_line_yards_total,
                (SELECT AVG(offense_line_yards_total) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_line_yards_total) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_line_yards_total)
            ELSE offense_line_yards_total
        END AS offense_line_yards_total,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_second_level_yards,
                (SELECT AVG(offense_second_level_yards) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_second_level_yards) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_second_level_yards)
            ELSE offense_second_level_yards
        END AS offense_second_level_yards,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_second_level_yards_total,
                (SELECT AVG(offense_second_level_yards_total) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_second_level_yards_total) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_second_level_yards_total)
            ELSE offense_second_level_yards_total
        END AS offense_second_level_yards_total,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_open_field_yards,
                (SELECT AVG(offense_open_field_yards) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_open_field_yards) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_open_field_yards)
            ELSE offense_open_field_yards
        END AS offense_open_field_yards,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_open_field_yards_total,
                (SELECT AVG(offense_open_field_yards_total) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_open_field_yards_total) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_open_field_yards_total)
            ELSE offense_open_field_yards_total
        END AS offense_open_field_yards_total,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_standard_downs_ppa,
                (SELECT AVG(offense_standard_downs_ppa) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_standard_downs_ppa) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_standard_downs_ppa)
            ELSE offense_standard_downs_ppa
        END AS offense_standard_downs_ppa,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_standard_downs_success_rate,
                (SELECT AVG(offense_standard_downs_success_rate) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_standard_downs_success_rate) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_standard_downs_success_rate)
            ELSE offense_standard_downs_success_rate
        END AS offense_standard_downs_success_rate,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_standard_downs_explosiveness,
                (SELECT AVG(offense_standard_downs_explosiveness) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_standard_downs_explosiveness) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_standard_downs_explosiveness)
            ELSE offense_standard_downs_explosiveness
        END AS offense_standard_downs_explosiveness,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_passing_downs_ppa,
                (SELECT AVG(offense_passing_downs_ppa) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_passing_downs_ppa) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_passing_downs_ppa)
            ELSE offense_passing_downs_ppa
        END AS offense_passing_downs_ppa,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_passing_downs_success_rate,
                (SELECT AVG(offense_passing_downs_success_rate) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_passing_downs_success_rate) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_passing_downs_success_rate)
            ELSE offense_passing_downs_success_rate
        END AS offense_passing_downs_success_rate,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_passing_downs_explosiveness,
                (SELECT AVG(offense_passing_downs_explosiveness) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_passing_downs_explosiveness) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_passing_downs_explosiveness)
            ELSE offense_passing_downs_explosiveness
        END AS offense_passing_downs_explosiveness,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_rushing_plays_ppa,
                (SELECT AVG(offense_rushing_plays_ppa) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_rushing_plays_ppa) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_rushing_plays_ppa)
            ELSE offense_rushing_plays_ppa
        END AS offense_rushing_plays_ppa,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_rushing_plays_total_ppa,
                (SELECT AVG(offense_rushing_plays_total_ppa) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_rushing_plays_total_ppa) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_rushing_plays_total_ppa)
            ELSE offense_rushing_plays_total_ppa
        END AS offense_rushing_plays_total_ppa,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_rushing_plays_success_rate,
                (SELECT AVG(offense_rushing_plays_success_rate) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_rushing_plays_success_rate) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_rushing_plays_success_rate)
            ELSE offense_rushing_plays_success_rate
        END AS offense_rushing_plays_success_rate,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_rushing_plays_explosiveness,
                (SELECT AVG(offense_rushing_plays_explosiveness) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_rushing_plays_explosiveness) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_rushing_plays_explosiveness)
            ELSE offense_rushing_plays_explosiveness
        END AS offense_rushing_plays_explosiveness,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_passing_plays_ppa,
                (SELECT AVG(offense_passing_plays_ppa) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_passing_plays_ppa) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_passing_plays_ppa)
            ELSE offense_passing_plays_ppa
        END AS offense_passing_plays_ppa,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_passing_plays_total_ppa,
                (SELECT AVG(offense_passing_plays_total_ppa) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_passing_plays_total_ppa) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_passing_plays_total_ppa)
            ELSE offense_passing_plays_total_ppa
        END AS offense_passing_plays_total_ppa,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_passing_plays_success_rate,
                (SELECT AVG(offense_passing_plays_success_rate) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_passing_plays_success_rate) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_passing_plays_success_rate)
            ELSE offense_passing_plays_success_rate
        END AS offense_passing_plays_success_rate,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(offense_passing_plays_explosiveness,
                (SELECT AVG(offense_passing_plays_explosiveness) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(offense_passing_plays_explosiveness) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                offense_passing_plays_explosiveness)
            ELSE offense_passing_plays_explosiveness
        END AS offense_passing_plays_explosiveness,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_plays,
                (SELECT AVG(defense_plays) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_plays) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_plays)
            ELSE defense_plays
        END AS defense_plays,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_drives,
                (SELECT AVG(defense_drives) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_drives) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_drives)
            ELSE defense_drives
        END AS defense_drives,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_ppa,
                (SELECT AVG(defense_ppa) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_ppa) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_ppa)
            ELSE defense_ppa
        END AS defense_ppa,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_total_ppa,
                (SELECT AVG(defense_total_ppa) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_total_ppa) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_total_ppa)
            ELSE defense_total_ppa
        END AS defense_total_ppa,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_success_rate,
                (SELECT AVG(defense_success_rate) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_success_rate) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_success_rate)
            ELSE defense_success_rate
        END AS defense_success_rate,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_explosiveness,
                (SELECT AVG(defense_explosiveness) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_explosiveness) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_explosiveness)
            ELSE defense_explosiveness
        END AS defense_explosiveness,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_power_success,
                (SELECT AVG(defense_power_success) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_power_success) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_power_success)
            ELSE defense_power_success
        END AS defense_power_success,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_stuff_rate,
                (SELECT AVG(defense_stuff_rate) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_stuff_rate) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_stuff_rate)
            ELSE defense_stuff_rate
        END AS defense_stuff_rate,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_line_yards,
                (SELECT AVG(defense_line_yards) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_line_yards) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_line_yards)
            ELSE defense_line_yards
        END AS defense_line_yards,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_line_yards_total,
                (SELECT AVG(defense_line_yards_total) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_line_yards_total) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_line_yards_total)
            ELSE defense_line_yards_total
        END AS defense_line_yards_total,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_second_level_yards,
                (SELECT AVG(defense_second_level_yards) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_second_level_yards) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_second_level_yards)
            ELSE defense_second_level_yards
        END AS defense_second_level_yards,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_second_level_yards_total,
                (SELECT AVG(defense_second_level_yards_total) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_second_level_yards_total) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_second_level_yards_total)
            ELSE defense_second_level_yards_total
        END AS defense_second_level_yards_total,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_open_field_yards,
                (SELECT AVG(defense_open_field_yards) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_open_field_yards) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_open_field_yards)
            ELSE defense_open_field_yards
        END AS defense_open_field_yards,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_open_field_yards_total,
                (SELECT AVG(defense_open_field_yards_total) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_open_field_yards_total) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_open_field_yards_total)
            ELSE defense_open_field_yards_total
        END AS defense_open_field_yards_total,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_standard_downs_ppa,
                (SELECT AVG(defense_standard_downs_ppa) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_standard_downs_ppa) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_standard_downs_ppa)
            ELSE defense_standard_downs_ppa
        END AS defense_standard_downs_ppa,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_standard_downs_success_rate,
                (SELECT AVG(defense_standard_downs_success_rate) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_standard_downs_success_rate) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_standard_downs_success_rate)
            ELSE defense_standard_downs_success_rate
        END AS defense_standard_downs_success_rate,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_standard_downs_explosiveness,
                (SELECT AVG(defense_standard_downs_explosiveness) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_standard_downs_explosiveness) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_standard_downs_explosiveness)
            ELSE defense_standard_downs_explosiveness
        END AS defense_standard_downs_explosiveness,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_passing_downs_ppa,
                (SELECT AVG(defense_passing_downs_ppa) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_passing_downs_ppa) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_passing_downs_ppa)
            ELSE defense_passing_downs_ppa
        END AS defense_passing_downs_ppa,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_passing_downs_success_rate,
                (SELECT AVG(defense_passing_downs_success_rate) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_passing_downs_success_rate) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_passing_downs_success_rate)
            ELSE defense_passing_downs_success_rate
        END AS defense_passing_downs_success_rate,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_passing_downs_explosiveness,
                (SELECT AVG(defense_passing_downs_explosiveness) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_passing_downs_explosiveness) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_passing_downs_explosiveness)
            ELSE defense_passing_downs_explosiveness
        END AS defense_passing_downs_explosiveness,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_rushing_plays_ppa,
                (SELECT AVG(defense_rushing_plays_ppa) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_rushing_plays_ppa) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_rushing_plays_ppa)
            ELSE defense_rushing_plays_ppa
        END AS defense_rushing_plays_ppa,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_rushing_plays_total_ppa,
                (SELECT AVG(defense_rushing_plays_total_ppa) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_rushing_plays_total_ppa) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_rushing_plays_total_ppa)
            ELSE defense_rushing_plays_total_ppa
        END AS defense_rushing_plays_total_ppa,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_rushing_plays_success_rate,
                (SELECT AVG(defense_rushing_plays_success_rate) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_rushing_plays_success_rate) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_rushing_plays_success_rate)
            ELSE defense_rushing_plays_success_rate
        END AS defense_rushing_plays_success_rate,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_rushing_plays_explosiveness,
                (SELECT AVG(defense_rushing_plays_explosiveness) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_rushing_plays_explosiveness) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_rushing_plays_explosiveness)
            ELSE defense_rushing_plays_explosiveness
        END AS defense_rushing_plays_explosiveness,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_passing_plays_ppa,
                (SELECT AVG(defense_passing_plays_ppa) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_passing_plays_ppa) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_passing_plays_ppa)
            ELSE defense_passing_plays_ppa
        END AS defense_passing_plays_ppa,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_passing_plays_total_ppa,
                (SELECT AVG(defense_passing_plays_total_ppa) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_passing_plays_total_ppa) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_passing_plays_total_ppa)
            ELSE defense_passing_plays_total_ppa
        END AS defense_passing_plays_total_ppa,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_passing_plays_success_rate,
                (SELECT AVG(defense_passing_plays_success_rate) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_passing_plays_success_rate) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_passing_plays_success_rate)
            ELSE defense_passing_plays_success_rate
        END AS defense_passing_plays_success_rate,
        CASE
            WHEN year >= 2003 AND completed = 1 THEN COALESCE(defense_passing_plays_explosiveness,
                (SELECT AVG(defense_passing_plays_explosiveness) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
                (SELECT AVG(defense_passing_plays_explosiveness) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year),
                defense_passing_plays_explosiveness)
            ELSE defense_passing_plays_explosiveness
        END AS defense_passing_plays_explosiveness,
        COALESCE(team_pregame_elo,
            (SELECT AVG(team_pregame_elo) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
            (SELECT AVG(team_pregame_elo) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year)
        ) AS team_pregame_elo,
        COALESCE(opponent_pregame_elo,
            (SELECT AVG(team_pregame_elo) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.opponent_id),
            (SELECT AVG(team_pregame_elo) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year)
        ) AS opponent_pregame_elo,
        COALESCE(team_elo_rating,
            (SELECT AVG(team_elo_rating) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.team_id),
            (SELECT AVG(team_elo_rating) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year)
        ) AS team_elo_rating,
        COALESCE(opponent_elo_rating,
            (SELECT AVG(team_elo_rating) FROM cleaned_data c2 WHERE c2.year = cleaned_data.year AND c2.team_id = cleaned_data.opponent_id),
            (SELECT AVG(team_elo_rating) FROM cleaned_data c3 WHERE c3.year = cleaned_data.year)
        ) AS opponent_elo_rating,
        team_postgame_elo, opponent_postgame_elo,
        avg_line_spread, avg_line_spread_open, avg_line_over_under, avg_line_over_under_open,
        avg_line_team_moneyline, avg_line_opponent_moneyline,
        team_recruiting_rank, team_recruiting_points, opponent_recruiting_rank, opponent_recruiting_points,
        CASE 
            WHEN year < 2015 THEN NULL
            ELSE COALESCE(
                team_talent,
                (SELECT AVG(c2.team_talent) FROM cleaned_data c2 
                 WHERE c2.year = cleaned_data.year 
                 AND c2.team_conference = cleaned_data.team_conference
                 AND c2.team_talent IS NOT NULL),
                (SELECT AVG(c3.team_talent) FROM cleaned_data c3 
                 WHERE c3.year = cleaned_data.year
                 AND c3.team_talent IS NOT NULL)
            )
        END AS team_talent,
        CASE 
            WHEN year < 2015 THEN NULL
            ELSE COALESCE(
                opponent_talent,
                (SELECT AVG(c2.team_talent) FROM cleaned_data c2 
                 WHERE c2.year = cleaned_data.year 
                 AND c2.team_conference = cleaned_data.opponent_conference
                 AND c2.team_talent IS NOT NULL),
                (SELECT AVG(c3.team_talent) FROM cleaned_data c3 
                 WHERE c3.year = cleaned_data.year
                 AND c3.team_talent IS NOT NULL)
            )
        END AS opponent_talent,
        team_points - opponent_points AS point_difference,
        CASE 
            WHEN completed = 0 THEN NULL
            WHEN team_points > opponent_points THEN 'win'
            WHEN team_points < opponent_points THEN 'loss'
            ELSE 'tie'
        END AS result,
        CASE 
            WHEN completed = 0 THEN NULL
            WHEN team_points > opponent_points THEN 1
            WHEN team_points = opponent_points THEN 0.5
            ELSE 0
        END AS win
    FROM cleaned_data
    """

    # Execute the query and fetch results
    source_cursor.execute(clean_data_query)
    results = source_cursor.fetchall()

    # Get column names
    column_names = [description[0] for description in source_cursor.description]

    # Drop the existing table if it exists
    target_cursor.execute("DROP TABLE IF EXISTS processed_teams")

    # Create the table in the target database
    create_table_query = f"CREATE TABLE processed_teams ({', '.join(column_names)})"
    target_cursor.execute(create_table_query)

    # Insert the data into the target database
    insert_query = f"INSERT INTO processed_teams VALUES ({', '.join(['?' for _ in column_names])})"
    target_cursor.executemany(insert_query, results)

    # Commit changes and close connections
    target_conn.commit()
    source_conn.close()
    target_conn.close()

    print(f"Processed teams data has been written to {target_db_path}")

def load_processed_teams_df(db_path):
    """
    Load the processed_teams table from the SQLite database into a pandas DataFrame.

    Args:
    db_path (str): Path to the SQLite database file.

    Returns:
    pandas.DataFrame: DataFrame containing the processed_teams data.
    """
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM processed_teams"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

if __name__ == "__main__":
    import os

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    source_db_path = os.path.join(project_root, 'data', '02_interim', 'transformed_teams.db')
    target_db_path = os.path.join(project_root, 'data', '03_processed', 'processed_teams.db')
    
    create_processed_teams_db(source_db_path, target_db_path)
    
    # Load and display the processed data
    processed_teams_df = load_processed_teams_df(target_db_path)
    
    print(f"Loaded processed_teams data. Shape: {processed_teams_df.shape}")
    print(processed_teams_df.head())