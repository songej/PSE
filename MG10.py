import random
import streamlit as st

# 페이지 설정 (wide 레이아웃으로 설정하고 상단 여백 제거)
st.set_page_config(layout="wide", page_title="PSE Gamma StudyMate", page_icon="🎓")

# 상단 여백을 줄이기 위한 스타일 추가
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
    </style>
    """, unsafe_allow_html=True
)

st.title('PSE Gamma StudyMate')

# 기본 그룹 멤버
all_members = ['Angela', 'Kate', 'Lily', 'Noel', 'Rae', 'Rain']

# 팀 멤버 선택 (multiselect로 간결하게 멤버 선택)
st.write("Select the present members:")
present_members = st.multiselect("Select Members", all_members, default=all_members)

# 단어시험 출제자 및 팀 랜덤 배정 함수
def assign_roles(members):
    if len(members) < 2:
        return None, [], "Not enough members to form a team!"
    
    random.shuffle(members)  # 멤버 섞기
    word_tester = members[0]  # 첫 번째 멤버를 퀴즈 출제자로 설정

    # 2명씩 팀 나누기
    teams = [members[i:i+2] for i in range(0, len(members), 2)]

    # 한 명이 홀로 남지 않도록 마지막 팀 처리
    if len(teams) > 1 and len(teams[-1]) == 1:
        teams[-2].append(teams[-1][0])  # 마지막 남은 인원을 바로 앞 팀에 추가
        teams.pop()  # 빈 팀 제거

    return word_tester, teams, None

# Mix It Up! 버튼 기능
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
