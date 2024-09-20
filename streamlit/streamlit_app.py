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
    *This app attempts to predict the outcome of college football games using machine learning models. 
    Select a week and search for specific teams to see their predicted win probabilities.*
    """)

    @st.cache_data
    def load_predictions():
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'predictions_2024_4.parquet')
        return pd.read_parquet(file_path)

    @st.cache_data
    def load_logos():
        file_path = 'logos.csv'
        return pd.read_csv(file_path)


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

    # Create a main container for the content
    main_container = st.container()

    # Create a fixed container for the button at the bottom
    button_container = st.container()

    # Custom CSS for gradient background and retro style
    st.markdown("""
    <style>
    #root > div:nth-child(1) > div > div > div > div > section.main.css-uf99v8.egzxvld5 {
        padding-bottom: 100px;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: white;
        color: black;
        text-align: center;
        padding: 10px 0;
        z-index: 999;
    }
    .content {
        margin-bottom: 100px; /* Adjust this value based on your footer height */
    }
    .gradient-bar-container {
        width: 80%;
        max-width: 400px; /* Adjust this value for desktop */
        margin: 0 auto;
        background-color: #333333;
        border-radius: 10px;
        overflow: hidden;
    }
    .gradient-bar {
        background: linear-gradient(90deg, #FFA500 0%, #FFD700 100%);
        height: 20px;
        border-radius: 10px;
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
    .team-logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 200px;  /* Adjust this value as needed for desktop */
    }
    .team-logo {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
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
    
    @media (max-width: 768px) {
        .team-logo-container {
            height: 150px;  /* Adjust this value as needed for tablets */
        }
        .team-logo {
            width: 30%;
            max-width: 120px;
        }
        .team-name {
            font-size: 16px;
            height: 40px;
        }
        .win-probability {
            font-size: 24px;
        }
        .team-to-win {
            font-size: 16px;
            height: 40px;
        }
        .gradient-bar-container {
            max-width: 300px; /* Adjust this value for tablets */
        }
    }

    @media (max-width: 480px) {
        .team-logo-container {
            height: 100px; /* adjust this value as needed for mobile */
        }
        .team-logo {
            width: 25%;
            max-width: 100px;
        }
        .team-name {
            font-size: 14px;
            height: 36px;
        }
        .win-probability {
            font-size: 20px;
        }
        .team-to-win {
            font-size: 14px;
            height: 36px;
        }
        .gradient-bar-container {
            max-width: 200px; /* Adjust this value for mobile */
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
    with main_container:
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
                        st.markdown(f'<div class="team-logo-container"><img src="data:image/png;base64,{image_to_base64(home_logo_circular)}" class="team-logo"></div>', unsafe_allow_html=True)
                
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
                        st.markdown(f'<div class="team-logo-container"><img src="data:image/png;base64,{image_to_base64(away_logo_circular)}" class="team-logo"></div>', unsafe_allow_html=True)
                
                st.markdown("---")

    # Add the button in the fixed container at the bottom
    with button_container:
        st.markdown("<hr>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("<h6 style='text-align: center; margin-bottom: 5px;'>If you enjoy this app, consider buying me a coffee!</h6>", unsafe_allow_html=True)
            st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
            button(username="tablecables", floating=False, width=220)
            st.markdown("</div>", unsafe_allow_html=True)

elif dashboard == "Support the Project":
    st.title("Support the Project")
    st.markdown("""
    If you find this project helpful and would like to support its development and maintenance, 
    consider buying me a coffee! Your support helps keep this project running and improving.
    """)
    button(username="tablecables", floating=False, width=220)