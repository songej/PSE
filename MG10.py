import random
import streamlit as st

st.set_page_config(layout="wide", page_title="PSE Gamma StudyMate", page_icon="🎓")

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
    }
    .stButton button {
        font-size: 18px;
        padding: 10px;
    }
    .stMarkdown p {
        font-size: 18px;
    }
    
    @media (max-width: 768px) {
        .block-container {
            padding-top: 0.5rem;
        }
        .stButton button {
            font-size: 16px;
            padding: 8px;
        }
        .stMarkdown p {
            font-size: 16px;
        }
    }
    </style>
    """, unsafe_allow_html=True
)

st.title('PSE Gamma StudyMate')

all_members = ['Angela', 'Kate', 'Lily', 'Noel', 'Rae', 'Rain']

present_members = st.multiselect("Select Members", all_members, default=all_members)

def assign_roles(members):
    num_members = len(members)
    if num_members < 2:
        return None, [], "Not enough members to form a team!"
    
    random.shuffle(members)
    quizmaster = members[0]
    teams = [members[i:i+2] for i in range(0, num_members, 2)]
    
    if len(teams) > 1 and len(teams[-1]) == 1:
        teams[-2].append(teams.pop()[0])
    return quizmaster, teams, None

if st.button('Mix It Up!'):
    if not present_members:
        st.error("No members selected! Please choose at least two members.")
    else:
        with st.spinner("Mixing teams and choosing the Vocabulary Quizmaster..."):
            quizmaster, teams, error = assign_roles(present_members)
        if error:
            st.error(error)
        else:
            st.success(f"Vocabulary Quizmaster: {quizmaster}")
            for i, team in enumerate(teams, start=1):
                st.write(f"Gamma G1-{i}: {', '.join(team)}")
