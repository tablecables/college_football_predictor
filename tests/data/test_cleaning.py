# test_cleaning

import unittest
import pandas as pd
import numpy as np
from src.data.cleaning import merge_and_clean_dataframes, create_team_centric_df

class TestDataCleaning(unittest.TestCase):
    def setUp(self):
        # Create sample dataframes for testing
        self.games_df = pd.DataFrame({
            'id': [1, 2],
            'season': [2021, 2021],
            'week': [1, 1],
            'season_type': ['regular', 'regular'],
            'start_date': ['2021-09-01', '2021-09-02'],
            'completed': [True, True],
            'home_id': [101, 102],
            'away_id': [201, 202],
            'home_team': ['Team A', 'Team B'],
            'away_team': ['Team C', 'Team D'],
            'home_conference': ['Conf1', 'Conf2'],
            'away_conference': ['Conf3', 'Conf4'],
            'home_division': ['Div1', 'Div2'],
            'away_division': ['Div3', 'Div4'],
            'home_points': [21, 28],
            'away_points': [14, 35],
            'venue_id': [1001, 1002],
            'venue': ['Stadium 1', 'Stadium 2'],
            'neutral_site': [False, True],
            'conference_game': [True, False],
            'attendance': [50000, 60000],
            'excitement_index': [0.8, 0.9],
            'highlights': ['highlight1', 'highlight2'],
            'notes': ['note1', 'note2']
        })

        self.team_stats_df = pd.DataFrame({
            'id': [1, 1, 2, 2],
            'team_id': [101, 201, 102, 202],
            'team_name': ['Team A', 'Team C', 'Team B', 'Team D'],
            'home_away': ['home', 'away', 'home', 'away'],
            'points': [21, 14, 28, 35],
            'total_yards': [300, 250, 350, 400],
            'turnovers': [1, 2, 0, 1]
        })

        self.advanced_stats_df = pd.DataFrame({
            'game_id': [1, 1, 2, 2],
            'season': [2021, 2021, 2021, 2021],
            'week': [1, 1, 1, 1],
            'team': ['Team A', 'Team C', 'Team B', 'Team D'],
            'opponent': ['Team C', 'Team A', 'Team D', 'Team B'],
            'offense': [{'ppa': 0.5}, {'ppa': 0.4}, {'ppa': 0.6}, {'ppa': 0.7}],
            'defense': [{'ppa': -0.3}, {'ppa': -0.2}, {'ppa': -0.4}, {'ppa': -0.5}]
        })

        self.team_talent_df = pd.DataFrame({
            'year': [2021, 2021, 2021, 2021],
            'school': ['Team A', 'Team B', 'Team C', 'Team D'],
            'talent': [800, 750, 700, 650]
        })

    def test_create_team_centric_df(self):
        result = create_team_centric_df(self.games_df)
        self.assertEqual(len(result), 4)  # Should have 4 rows (2 games * 2 teams per game)
        expected_columns = ['id', 'season', 'week', 'season_type', 'start_date', 'neutral_site', 
                            'conference_game', 'attendance', 'venue_id', 'venue', 
                            'excitement_index', 'highlights', 'notes', 'team_id', 'team', 
                            'team_division', 'team_points', 'opponent_id', 'opponent', 
                            'opponent_conference', 'opponent_division', 'opponent_points', 'is_home']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"Column {col} is missing from the result")

    def test_merge_and_clean_dataframes(self):
        result = merge_and_clean_dataframes(self.games_df, self.team_stats_df, self.advanced_stats_df, self.team_talent_df)
        
        # Check for duplicated rows
        duplicated_rows = result[result.duplicated()]
        if not duplicated_rows.empty:
            print("\nDuplicated rows found:")
            print(duplicated_rows)
            
            # Identify which columns are causing the duplication
            duplicate_causing_columns = []
            for col in result.columns:
                if result[col].duplicated().any():
                    duplicate_causing_columns.append(col)
            
            print("\nColumns potentially causing duplication:")
            for col in duplicate_causing_columns:
                print(f"- {col}")
            
            # Check for near-duplicates (rows that are identical except for a few columns)
            print("\nChecking for near-duplicates:")
            for i, row in duplicated_rows.iterrows():
                near_duplicates = result[(result != row).sum(axis=1) <= 3]  # Rows that differ in 3 or fewer columns
                if not near_duplicates.empty:
                    print(f"\nNear-duplicates for row {i}:")
                    print(near_duplicates)
                    print("\nDifferences:")
                    print(near_duplicates.ne(row).sum())
        
        # Assert that there should be no duplicates
        self.assertTrue(duplicated_rows.empty, f"Found {len(duplicated_rows)} duplicated rows")
        
        # Print additional information about the result
        print(f"\nShape of result: {result.shape}")
        print("\nColumn names:")
        for col in result.columns:
            print(f"- {col}")
        
        # Check for unexpected number of rows
        expected_rows = len(self.games_df) * 2  # Each game should result in two rows (one for each team)
        self.assertEqual(len(result), expected_rows, f"Expected {expected_rows} rows, but got {len(result)}")

        # Check for important columns
        important_columns = [
            'id', 'season', 'week', 'team_id', 'team', 'opponent_id', 'opponent',
            'team_points', 'opponent_points', 'venue_id', 'venue', 'neutral_site',
            'conference_game', 'attendance', 'excitement_index', 'total_yards',
            'turnovers', 'offense_ppa', 'defense_ppa', 'team_talent', 'opponent_talent',
            'point_difference', 'result'
        ]
        for col in important_columns:
            self.assertIn(col, result.columns, f"Column {col} is missing from the result")

    def test_handle_missing_values(self):
        # Introduce some missing values
        self.games_df.loc[0, 'attendance'] = np.nan
        self.team_stats_df.loc[0, 'total_yards'] = np.nan
        self.advanced_stats_df.loc[0, 'offense'] = np.nan
        
        result = merge_and_clean_dataframes(self.games_df, self.team_stats_df, self.advanced_stats_df, self.team_talent_df)
        
        # Check if columns exist
        self.assertIn('attendance', result.columns, "Attendance column is missing")
        self.assertIn('total_yards', result.columns, "Total yards column is missing")
        self.assertIn('offense_ppa', result.columns, "offense_ppa column is missing")
        
        # Print some diagnostic information
        print("Columns in result:")
        print(result.columns.tolist())
        print("\nShape of result:")
        print(result.shape)
        print("\nFirst few rows of result:")
        print(result.head())

        # Check for unexpected duplicates
        duplicates = result[result.duplicated()]
        if not duplicates.empty:
            print("\nUnexpected duplicates found:")
            print(duplicates)
        self.assertTrue(duplicates.empty, "Unexpected duplicate rows found in the result")

if __name__ == '__main__':
    unittest.main()