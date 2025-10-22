import streamlit as st
from sleeper_wrapper import League, Players
import random
import base64
import time
import pandas as pd

# Initialize session state
if 'show_gif' not in st.session_state:
    st.session_state.show_gif = False
if 'snap_done' not in st.session_state:
    st.session_state.snap_done = False
if 'rosters_fetched' not in st.session_state:
    st.session_state.rosters_fetched = False
if 'team_rosters' not in st.session_state:
    st.session_state.team_rosters = {}
if 'immune_players' not in st.session_state:
    st.session_state.immune_players = {}

# Streamlit page configuration
st.set_page_config(page_title="Thanos Snap Fantasy Football", page_icon="🧤", layout="wide")

# Custom CSS for Thanos theme
st.markdown("""
<style>
.stApp {
    background-color: #1c1c1c;
    color: #ffffff;
    font-family: 'Arial', sans-serif;
}
.title {
    color: #FFD700;
    text-align: center;
    font-size: 3em;
    text-shadow: 0 0 10px #4B0082;
}
.subtitle {
    color: #B0C4DE;
    text-align: center;
    font-size: 1.5em;
}
.stButton>button {
    background-color: #4B0082;
    color: #FFD700;
    border: 2px solid #FFD700;
    border-radius: 10px;
    font-size: 1.2em;
    padding: 10px 20px;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background-color: #FFD700;
    color: #4B0082;
    transform: scale(1.05);
}
.stFormSubmitButton>button {
    background-color: #4B0082;
    color: #FFD700;
    border: 2px solid #FFD700;
    border-radius: 10px;
    font-size: 1.2em;
    padding: 10px 20px;
    transition: all 0.3s ease;
}
.stFormSubmitButton>button:hover {
    background-color: #FFD700;
    color: #4B0082;
    transform: scale(1.05);
}
.stTextInput label {
    color: #F5F5F5;
    font-size: 1.2em;
}
.stTextInput input {
    background-color: #3a3a3a;
    color: #FFFFFF;
    border: 1px solid #FFD700;
    border-radius: 5px;
    padding: 8px;
}
.stTextInput input::placeholder {
    color: #B0C4DE;
}
.stDataFrame {
    background-color: #3a3a3a;
    border-radius: 10px;
    padding: 10px;
    border: 1px solid #FFD700;
}
.stDataFrame table {
    color: #F5F5F5;
    font-size: 1.1em;
}
.stDataFrame th, .stDataFrame td {
    border: 1px solid #4B0082;
    padding: 8px;
}
.stDataFrame tr:nth-child(even) {
    background-color: #333333;
}

/* === More aggressive radio label styling to target nested text === */
.stRadio, 
.stRadio * {
    color: #F5F5F5 !important;   /* default light text for everything inside stRadio */
    opacity: 1 !important;       /* ensure no translucency */
    -webkit-text-fill-color: #F5F5F5 !important; /* for certain browsers */
}

/* Target the label container and inner text nodes specifically */
.stRadio > div[role="radiogroup"] label,
.stRadio > div[role="radiogroup"] label div,
.stRadio > div[role="radiogroup"] label span,
.stRadio > div[role="radiogroup"] label div > div {
    color: #F5F5F5 !important;
    opacity: 1 !important;
}

/* Keep hover & selected visuals (gold + purple) */
.stRadio > div[role="radiogroup"] label:hover {
    color: #FFD700 !important;
    background-color: rgba(75, 0, 130, 0.4) !important;
}
.stRadio > div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked),
.stRadio > div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) div,
.stRadio > div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) span {
    color: #FFD700 !important;
    background-color: #4B0082 !important;
    border: 1px solid #FFD700 !important;
    padding: 4px 6px !important;
    border-radius: 5px !important;
    transform: scale(1.02);
    opacity: 1 !important;
}

/* Radio circle color */
input[type="radio"] {
    accent-color: #FFD700 !important;
}

.snap-animation {
    animation: fadeIn 1s ease-in-out;
}
@keyframes fadeIn {
    0% { opacity: 0; transform: scale(0.8); }
    100% { opacity: 1; transform: scale(1); }
}
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<div class="title">🧤 Thanos Snap Fantasy Football</div>', unsafe_allow_html=True)
st.markdown("""
<div class="subtitle">
Enter your Sleeper league ID, select one immune player per team, and Thanos will snap his fingers to eliminate half of each team's roster (excluding immune players). Perfectly balanced, as all things should be.
</div>
""", unsafe_allow_html=True)

# Input section for league ID
with st.container():
    league_id = st.text_input("Enter your Sleeper League ID", placeholder="e.g., 123456789012345678")
    fetch_button = st.button("Fetch Rosters")

# Initialize Players object for player data
@st.cache_data
def get_player_data():
    players = Players()
    return players.get_all_players()

player_data = get_player_data()

# Handle roster fetch
if fetch_button and league_id:
    try:
        league = League(league_id)
        with st.spinner("Fetching league rosters..."):
            rosters = league.get_rosters()
            users = league.get_users()
        
        # Create team rosters dictionary
        team_rosters = {}
        for roster in rosters:
            owner_id = roster['owner_id']
            team_name = None
            for user in users:
                if user['user_id'] == owner_id:
                    team_name = user.get('display_name', f"Team {owner_id}")
                    break
            player_ids = roster.get('players', [])
            roster_players = [
                {
                    'name': player_data.get(pid, {}).get('full_name', 'Unknown Player'),
                    'id': pid,
                    'position': player_data.get(pid, {}).get('position', 'Unknown')
                } for pid in player_ids if pid in player_data
            ]
            team_rosters[team_name] = roster_players
        
        st.session_state.team_rosters = team_rosters
        st.session_state.rosters_fetched = True
        st.session_state.show_gif = False
        st.session_state.snap_done = False
        st.session_state.immune_players = {team: None for team in team_rosters}
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}. Please check your league ID and try again.")
elif fetch_button and not league_id:
    st.warning("Please enter a valid Sleeper League ID.")

# Player selection screen
if st.session_state.rosters_fetched and not st.session_state.show_gif and not st.session_state.snap_done:
    st.markdown('<div class="snap-animation"><h2>Select One Immune Player Per Team</h2></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='color: #B0C4DE; text-align: center; font-size: 1.2em;'>
    You can only save one! Choose wisely, for balance demands sacrifice!
    </div>
    """, unsafe_allow_html=True)
    with st.form("immune_players_form"):
        for team_name, players in st.session_state.team_rosters.items():
            st.subheader(f"Team: {team_name}")
            player_options = [f"{player['name']} ({player['position']})" for player in players]
            player_options.insert(0, "None")  # Allow no selection initially
            selected_player = st.radio(
                f"Select the one player to save from the snap for {team_name}",
                options=player_options,
                index=0,
                key=f"immune_{team_name}"
            )
            if selected_player != "None":
                st.session_state.immune_players[team_name] = next(
                    (p for p in players if f"{p['name']} ({p['position']})" == selected_player), None
                )
            else:
                st.session_state.immune_players[team_name] = None
        submit_immunities = st.form_submit_button("Confirm Selections and Perform Thanos Snap")

    if submit_immunities:
        if all(st.session_state.immune_players[team] is not None for team in st.session_state.team_rosters):
            st.session_state.show_gif = True
            st.rerun()
        else:
            st.warning("Please select one immune player for each team.")

# Display GIF if show_gif is True
if st.session_state.show_gif and not st.session_state.snap_done:
    try:
        with open("assets/thanos_snap.gif", "rb") as file:
            contents = file.read()
            data_url = base64.b64encode(contents).decode("utf-8")
            st.markdown(
                f'<img src="data:image/gif;base64,{data_url}" width="300" style="display: block; margin: 0 auto;">',
                unsafe_allow_html=True
            )
    except FileNotFoundError:
        st.image("https://media.giphy.com/media/3o7btPCcdN6Yk4tW4I/giphy.gif", width=300, caption="Thanos Snap")

    with st.spinner("Thanos is snapping his fingers..."):
        time.sleep(3)
        snap_results = {}
        for team_name, players in st.session_state.team_rosters.items():
            immune_player = st.session_state.immune_players.get(team_name)
            eligible_players = [p for p in players if p != immune_player]
            num_to_eliminate = (len(players) - (1 if immune_player else 0)) // 2
            num_to_eliminate = max(0, num_to_eliminate)
            eliminated_players = random.sample(eligible_players, min(num_to_eliminate, len(eligible_players)))
            snap_results[team_name] = eliminated_players
        
        st.session_state.show_gif = False
        st.session_state.snap_done = True
        st.session_state.snap_results = snap_results
        st.rerun()

# Display results if snap is done
if st.session_state.snap_done and 'snap_results' in st.session_state:
    st.success("Thanos has snapped his fingers! 💥")
    st.markdown('<div class="snap-animation"><h2>Thanos Snap Results</h2></div>', unsafe_allow_html=True)
    
    for team_name, eliminated_players in st.session_state.snap_results.items():
        st.subheader(f"Team: {team_name}")
        immune_player = st.session_state.immune_players.get(team_name)
        if immune_player:
            st.markdown(f"**Immune Player**: {immune_player['name']} ({immune_player['position']})")
        if eliminated_players:
            player_data = pd.DataFrame([
                {"Player Name": player['name'], "Position": player['position']}
                for player in eliminated_players
            ])
            st.dataframe(player_data, use_container_width=True, hide_index=True)
        else:
            st.write("No players eliminated (empty roster).")

