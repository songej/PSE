import random
import streamlit as st

# 페이지 설정 (모바일 레이아웃을 고려하여 wide로 설정)
st.set_page_config(layout="wide", page_title="PSE Gamma StudyMate", page_icon="🎓")

st.title('PSE Gamma StudyMate')

# 기본 그룹 멤버
all_members = ['Angela', 'Kate', 'Lily', 'Noel', 'Rae', 'Rain']

# 팀 멤버 선택 체크박스 -> 모바일에서 리스트가 길어질 수 있으므로 multiselect로 변경
st.write("Select the present members:")
present_members = st.multiselect("Select Members", all_members, default=all_members)

# 단어시험 출제자 및 팀 랜덤 배정 함수
def assign_roles(members):
    if len(members) < 2:
        return None, [], "Not enough members to form a team!"
    
    random.shuffle(members)
    word_tester = members[0]  # 첫 번째 멤버를 퀴즈 출제자로 지정

    # 팀 구성 (2명씩 묶고, 홀수일 경우 첫 번째 팀에 추가)
    teams = [members[i:i+2] for i in range(0, len(members), 2)]
    if len(members) % 2 != 0:
        teams[0].append(members[-1])

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

# 사용자 안내 텍스트에 글자 크기를 조절하여 모바일에서 읽기 쉽게 만듦
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
