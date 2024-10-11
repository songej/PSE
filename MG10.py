import random
import streamlit as st

st.set_page_config(layout="wide", page_title="PSE Gamma StudyMate", page_icon="🎓")

st.title('PSE Gamma StudyMate')
all_members = ['Angela', 'Kate', 'Lily', 'Noel', 'Rae', 'Rain']

st.write("Select the present members:")
present_members = st.multiselect("Select Members", all_members, default=all_members)

def assign_roles(members):
    if len(members) < 2:
        return None, [], "Not enough members to form a team!"
    
    random.shuffle(members)
    word_tester = members[0]

    teams = [members[i:i+2] for i in range(0, len(members), 2)]
    if len(members) % 2 != 0:
        teams[0].append(members[-1])

    return word_tester, teams, None

if st.button('Mix It Up!'):
    if not present_members:
        st.error("No members selected! Please select at least 2 members.")
    else:
        with st.spinner("Shuffling teams and selecting a word tester..."):
            word_tester, teams, error = assign_roles(present_members)
        if error:
            st.error(error)
        else:
            st.success(f"Vocabulary Quizmaster: {word_tester}")
            for i, team in enumerate(teams, start=1):
                st.write(f"Gamma G1-{i}: {', '.join(team)}")

st.markdown(
    """
    <style>
    .stButton button {
        font-size: 18px;
        padding: 10px;
    }
    .stMarkdown p {
        font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)
