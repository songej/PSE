import random
import streamlit as st

st.title('Random Team Assignment')

def random_teams():
    names = ['Rae', 'Lily', 'Rain', 'Angela', 'Noel', 'Kate']
    teams = ['Gamma G1-1', 'Gamma G1-2', 'Gamma G1-3']
    
    random.shuffle(names)
    team_assignments = {teams[i]: names[i*2:(i+1)*2] for i in range(3)}
    return team_assignments

if st.button('Generate Random Teams'):
    team_assignments = random_teams()
    for team, members in team_assignments.items():
        st.write(f"{team}: {', '.join(members)}")
