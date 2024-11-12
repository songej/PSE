import random
import streamlit as st

st.set_page_config(layout="wide", page_title="PSE StudyMate", page_icon="🎓")

st.markdown(
    """
    <style>
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem;
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

st.title('PSE StudyMate')

all_members = ['1번', '2번', '3번', '4번', '5번', '6번']
present_members = st.multiselect("Select Members", all_members, default=all_members)

def assign_roles(members):
    num_members = len(members)
    if num_members < 2:
        return None, [], "Not enough members to form a team!"
    
    random.shuffle(members)  # 무작위 섞기
    quizmaster = members[0]  # 단어 퀴즈 역할 지정
    teams = [members[i:i+2] for i in range(0, num_members, 2)]  # 소그룹 지정
    
    # 홀수 팀 구성 시 마지막 팀 조정
    if len(teams[-1]) == 1 and len(teams) > 1:
        if len(teams[-2]) < 3:
            teams[-2].append(teams.pop()[0])
    
    # 팀 구성 완료 확인
    if any(len(team) > 3 for team in teams):
        return None, [], "Team assignment error! Please try again."
    
    return quizmaster, teams, None

# 팀 구성 버튼
if st.button('Mix It Up!'):
    if not present_members:
        st.error("No members selected! Please choose at least two members.")
    else:
        random.seed(None)  # 매번 새로운 랜덤 시드 설정
        with st.spinner("Mixing teams and choosing the Vocabulary Quizmaster..."):
            quizmaster, teams, error = assign_roles(present_members)
        if error:
            st.error(error)
        else:
            st.success(f"Vocabulary Quizmaster: {quizmaster}")
            for i, team in enumerate(teams, start=1):
                st.write(f"sub-group #{i}: [ {', '.join(team)} ]")
