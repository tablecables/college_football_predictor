import streamlit as st
from streamlit_extras.buy_me_a_coffee import button
import pandas as pd
import os
from PIL import Image, ImageDraw, ImageFilter
import requests
from io import BytesIO
import base64

st.set_page_config(layout="wide")

# Add sidebar
st.sidebar.title("Navigation")
dashboard = st.sidebar.radio(
    "Select a Dashboard",
    ["Weekly Win Probabilities",
     "Support the Project"]
)


if dashboard == "Weekly Win Probabilities":
    st.title("🏈 College Football Predictor")

    st.markdown("""
    *This app predicts the outcomes of college football games using machine learning models. 
    Select a week and search for specific teams to see their predicted win probabilities.*
    """)

<<<<<<< HEAD
    @st.cache_data
    def load_predictions():
        return pd.read_parquet('../models/win_probability/predictions_2024_3.parquet')

    @st.cache_data
    def load_logos():
        return pd.read_csv('../src/utils/logos/logos.csv')
=======
@st.cache_data
def load_predictions():
    file_path = os.path.join(os.path.dirname(__file__), 'predictions_2024_3.parquet')
    return pd.read_parquet(file_path)

@st.cache_data
def load_logos():
    file_path = os.path.join(os.path.dirname(__file__), 'logos.csv')
    return pd.read_csv(file_path)
>>>>>>> origin/main

    predictions = load_predictions()
    logos_df = load_logos()

    # Add week selection
    weeks = sorted(predictions['week'].unique())
    selected_week = st.selectbox("Select Week", weeks, index=len(weeks)-1, key="week_selector")

    # Filter predictions by selected week
    predictions = predictions[predictions['week'] == selected_week]

    def get_logo_url(team_id):
        logo_url = logos_df[logos_df['id'] == team_id]['logo'].values
        return logo_url[0] if len(logo_url) > 0 else None

    def create_circular_mask(image, size=(500, 500), border_width=3):
        # Resize and crop the image to a square
        image = image.convert('RGBA')
        image = image.resize((size[0], size[0]), Image.LANCZOS)
        
        # Create a white circle image for the border
        border = Image.new('RGBA', (size[0]+border_width*2, size[1]+border_width*2), (255, 255, 255, 0))
        draw = ImageDraw.Draw(border)
        draw.ellipse([0, 0, size[0]+border_width*2, size[1]+border_width*2], fill=(255, 255, 255, 255))
        
        # Create the mask
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        
        # Apply the mask to the image
        output = Image.new('RGBA', size, (0, 0, 0, 0))
        output.paste(image, (0, 0), mask)
        
        # Apply a slight blur to smooth edges
        output = output.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Paste the output onto the border
        bordered_output = Image.new('RGBA', (size[0]+border_width*2, size[1]+border_width*2), (0, 0, 0, 0))
        bordered_output.paste(border, (0, 0))
        bordered_output.paste(output, (border_width, border_width), output)
        
        return bordered_output

    # Improved search functionality
    search_query = st.text_input("Search for teams:")

    def match_teams(row, query_terms):
        teams = f"{row['home_team']} {row['away_team']}".lower()
        return all(term.lower() in teams for term in query_terms)

    if search_query:
        query_terms = search_query.split()
        filtered_predictions = predictions[predictions.apply(lambda row: match_teams(row, query_terms), axis=1)]
    else:
        filtered_predictions = predictions

    # Custom CSS for gradient background and retro style
    st.markdown("""
    <style>
    .gradient-bar {
        background: linear-gradient(90deg, #FFA500 0%, #FFD700 100%);
        height: 20px;
        border-radius: 10px;
    }
    .gradient-bar-container {
        width: 100%;
        background-color: #333333;
        border-radius: 10px;
        overflow: hidden;
    }
    .team-name {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    .win-probability {
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .team-to-win {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .team-logo {
        width: 100%;
        max-width: 200px;
    }
    .probability-info {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .centered-button {
        display: flex;
        justify-content: center;
        align-items: center;
    @media (max-width: 645px) {
        .team-logo {
            width: 40vw;
            max-width: 120px;
        }
        .team-name {
            font-size: 20px;
            height: 32px;
        }
        .win-probability {
            font-size: 20px;
        }
        .team-to-win {
            font-size: 20px;
            height: 32px;
        }
        .gradient-bar-container {
            width: 40vw;
            margin: 0 auto 20px;
        }
        .probability-info {
            flex-direction: row;
            justify-content: center;
            align-items: baseline;
            gap: 10px;
        }
        .team-to-win {
            margin-bottom: 0;
        }
        .centered-button {
            display: flex;
            justify-content: center;
            align-items: center;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Helper function to convert image to base64
    def image_to_base64(img):
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    # Display all games
    for index, game_data in filtered_predictions.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([2,3,2])
            
            # Home team
            with col1:
                st.markdown(f'<div class="team-name">{game_data["home_team"]}</div>', unsafe_allow_html=True)
                home_logo_url = get_logo_url(game_data['home_id'])
                if home_logo_url:
                    response = requests.get(home_logo_url)
                    home_logo = Image.open(BytesIO(response.content))
                    home_logo_circular = create_circular_mask(home_logo)
                    st.markdown(f'<div style="display: flex; justify-content: center;"><img src="data:image/png;base64,{image_to_base64(home_logo_circular)}" class="team-logo"></div>', unsafe_allow_html=True)
            
            # Win probability
            with col2:
                win_prob = game_data['win_probability']
                winning_team = game_data['home_team'] if win_prob > 0.5 else game_data['away_team']
                st.markdown(f"""
                <div style='text-align: center; padding: 20px;'>
                    <div class='probability-info'>
                        <div class='team-to-win'>{winning_team} to win</div>
                        <div class='win-probability'>{max(win_prob, 1-win_prob):.1%}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Gradient probability bar
                st.markdown(f"""
                <div class='gradient-bar-container'>
                    <div class='gradient-bar' style='width: {win_prob:.0%};'></div>
                </div>
                """, unsafe_allow_html=True)
            
            # Away team
            with col3:
                st.markdown(f'<div class="team-name">{game_data["away_team"]}</div>', unsafe_allow_html=True)
                away_logo_url = get_logo_url(game_data['away_id'])
                if away_logo_url:
                    response = requests.get(away_logo_url)
                    away_logo = Image.open(BytesIO(response.content))
                    away_logo_circular = create_circular_mask(away_logo)
                    st.markdown(f'<div style="display: flex; justify-content: center;"><img src="data:image/png;base64,{image_to_base64(away_logo_circular)}" class="team-logo"></div>', unsafe_allow_html=True)
            
            st.markdown("---")

    # Add the button at the bottom of the page, after all games
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<h6 style='text-align: center;'>If you enjoy this app, consider buying me a coffee!</h6>", unsafe_allow_html=True)
        st.markdown("<div class='centered-button'>", unsafe_allow_html=True)
        button(username="tablecables", floating=False, width=220)
        st.markdown("</div>", unsafe_allow_html=True)

elif dashboard == "Support the Project":
    st.title("Support the Project")
    st.markdown("""
    If you find this project helpful and would like to support its development and maintenance, 
    consider buying me a coffee! Your support helps keep this project running and improving.
    """)
    button(username="tablecables", floating=False, width=220)