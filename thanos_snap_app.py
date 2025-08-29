import streamlit as st
from sleeper_wrapper import League, Players
import random

# Streamlit page configuration
st.set_page_config(page_title="Thanos Snap Fantasy Football", page_icon="🧤", layout="wide")

# Title and description
st.title("🧤 Thanos Snap Fantasy Football")
st.markdown("""
Welcome to the Thanos Snap app! Enter your Sleeper league ID below, and Thanos will snap his fingers to randomly eliminate half of each team's roster. Perfectly balanced, as all things should be.
""")

# Input section for league ID
league_id = st.text_input("Enter your Sleeper League ID", placeholder="e.g., 123456789012345678")
snap_button = st.button("Perform Thanos Snap")

# Initialize Players object for player data
players = Players()
player_data = players.get_all_players()  # Fetch player data once

if snap_button and league_id:
    try:
        # Initialize League object
        league = League(league_id)
        
        # Fetch rosters and users
        with st.spinner("Fetching league data..."):
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
        
        # Display results
        st.success("Thanos has snapped his fingers!")
        st.markdown("## Thanos Snap Results")
        
        for team_name, eliminated_players in snap_results.items():
            st.subheader(f"Team: {team_name}")
            if eliminated_players:
                # Create a table for eliminated players
                player_data = [
                    {"Player Name": player['name'], "Position": player['position']}
                    for player in eliminated_players
                ]
                st.table(player_data)
            else:
                st.write("No players eliminated (empty roster).")
                
    except Exception as e:
        st.error(f"Error: {e}. Please check your league ID and try again.")
else:
    if snap_button and not league_id:
        st.warning("Please enter a valid Sleeper League ID.")