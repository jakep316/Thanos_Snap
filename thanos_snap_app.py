import streamlit as st
from sleeper_wrapper import League, Players
import random
import base64
import time
import pandas as pd

# Initialize session state for GIF visibility
if 'show_gif' not in st.session_state:
    st.session_state.show_gif = False
if 'snap_done' not in st.session_state:
    st.session_state.snap_done = False

# Streamlit page configuration
st.set_page_config(page_title="Thanos Snap Fantasy Football", page_icon="🧤", layout="wide")

# Custom CSS for Thanos theme with improved readability
st.markdown("""
<style>
.stApp {
    background-color: #1c1c1c;
    color: #ffffff;
    font-family: 'Arial', sans-serif;
}
.title {
    color: #FFD700; /* Gold for Infinity Gauntlet */
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
    background-color: #4B0082; /* Purple for Thanos */
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
.stTextInput label {
    color: #F5F5F5; /* Light gray for input label */
    font-size: 1.2em;
}
.stTextInput input {
    background-color: #3a3a3a; /* Lighter background for input */
    color: #FFFFFF; /* White text for input */
    border: 1px solid #FFD700; /* Gold border */
    border-radius: 5px;
    padding: 8px;
}
.stTextInput input::placeholder {
    color: #B0C4DE; /* Light blue placeholder for contrast */
}
.stDataFrame {
    background-color: #3a3a3a; /* Lighter background for tables */
    border-radius: 10px;
    padding: 10px;
    border: 1px solid #FFD700; /* Gold border */
}
.stDataFrame table {
    color: #F5F5F5; /* Light gray/white for table text */
    font-size: 1.1em;
}
.stDataFrame th, .stDataFrame td {
    border: 1px solid #4B0082; /* Purple borders for table cells */
    padding: 8px;
}
.stDataFrame tr:nth-child(even) {
    background-color: #333333; /* Alternating row color */
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
Enter your Sleeper league ID, and Thanos will snap his fingers to randomly eliminate half of each team's roster. Perfectly balanced, as all things should be.
</div>
""", unsafe_allow_html=True)

# Input section for league ID
with st.container():
    league_id = st.text_input("Enter your Sleeper League ID", placeholder="e.g., 123456789012345678")
    snap_button = st.button("Perform Thanos Snap")

# Initialize Players object for player data
@st.cache_data
def get_player_data():
    players = Players()
    return players.get_all_players()

player_data = get_player_data()

# Handle button click
if snap_button and league_id:
    try:
        # Reset snap_done state
        st.session_state.snap_done = False
        # Show GIF
        st.session_state.show_gif = True
        # Force rerun to display GIF immediately
        st.rerun()

    except Exception as e:
        st.error(f"Error: {e}. Please check your league ID and try again.")
elif snap_button and not league_id:
    st.warning("Please enter a valid Sleeper League ID.")

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

    # Simulate snap processing with spinner
    with st.spinner("Thanos is snapping his fingers..."):
        time.sleep(3)  # Show GIF for 3 seconds
        # Perform API calls and snap logic
        league = League(league_id)
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
        
        # Perform Thanos Snap
        snap_results = {}
        for team_name, players in team_rosters.items():
            num_to_eliminate = len(players) // 2
            eliminated_players = random.sample(players, num_to_eliminate)
            snap_results[team_name] = eliminated_players
        
        # Update session state to hide GIF and show results
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
        if eliminated_players:
            player_data = pd.DataFrame([
                {"Player Name": player['name'], "Position": player['position']}
                for player in eliminated_players
            ])
            st.dataframe(player_data, use_container_width=True, hide_index=True)
        else:
            st.write("No players eliminated (empty roster).")