import streamlit as st
import pandas as pd
import os
from PIL import Image, ImageDraw, ImageFilter
import requests
from io import BytesIO

st.set_page_config(layout="wide")

# Add sidebar
st.sidebar.title("Navigation")
dashboard = st.sidebar.radio(
    "Select a Dashboard",
    ["Weekly Win Probabilities"]
)

if dashboard == "Weekly Win Probabilities":
    st.title("🏈 College Football Predictor")

    st.markdown("""
    *This app predicts the outcomes of college football games using machine learning models. 
    Select a week and search for specific teams to see their predicted win probabilities.*
    """)

@st.cache_data
def load_predictions():
    file_path = os.path.join(os.path.dirname(__file__), 'predictions_2024_3.parquet')
    return pd.read_parquet(file_path)

@st.cache_data
def load_logos():
    file_path = os.path.join(os.path.dirname(__file__), 'logos.csv')
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

# Custom CSS for gradient background and retro style
st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)

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
                st.image(home_logo_circular, use_column_width=True)
        
        # Win probability
        with col2:
            win_prob = game_data['win_probability']
            winning_team = game_data['home_team'] if win_prob > 0.5 else game_data['away_team']
            st.markdown(f"""
            <div style='text-align: center; padding: 20px;'>
                <div class='team-to-win'>{winning_team} to win</div>
                <div class='win-probability'>{max(win_prob, 1-win_prob):.1%}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Gradient probability bar
            st.markdown(f"""
            <div style='width: 100%; background-color: #333333; border-radius: 10px; overflow: hidden;'>
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
                st.image(away_logo_circular, use_column_width=True)
        
        st.markdown("---")