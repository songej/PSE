import random
import streamlit as st

st.title('PSE Gamma Shuffler')

# Group Members
st.write("Group Members: Angela, Kate, Lily, Noel, Rae, Rain")

def random_teams():
    names = ['Angela', 'Kate', 'Lily', 'Noel', 'Rae', 'Rain']
    teams = ['Gamma G1-1', 'Gamma G1-2', 'Gamma G1-3']
    
    # Shuffle the names randomly
    random.shuffle(names)
    return {teams[i]: names[i*2:(i+1)*2] for i in range(3)}

if st.button('Mix It Up!'):
    team_assignments = random_teams()
    st.write("Random Team Assignments:")
    for team, members in team_assignments.items():
        st.write(f"{team}: {', '.join(members)}")
