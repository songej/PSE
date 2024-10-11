import random
import streamlit as st

st.set_page_config(layout="centered", page_title="PSE Gamma StudyMate", page_icon="🎓")

st.title('PSE Gamma StudyMate')

# 기본 그룹 멤버
all_members = ['Angela', 'Kate', 'Lily', 'Noel', 'Rae', 'Rain']

# 팀 멤버 선택 체크박스 (기본값: 모두 체크)
st.write("Select the present members:")
with st.expander("Select Members", expanded=True):
    present_members = [member for member in all_members if st.checkbox(member, value=True)]

# 단어시험 출제자 및 팀 랜덤 배정 함수
def assign_roles(members):
    if len(members) < 2:
        return None, [], "Not enough members to form a team!"
    
    random.shuffle(members)
    word_tester, team_members = members[0], members[1:]

    # 팀 구성
    teams = [team_members[i:i+2] for i in range(0, len(team_members), 2)]
    
    # 첫 팀에 3명 배정(홀수 인원일 때)
    if len(team_members) % 2 != 0:
        teams[0].append(team_members[-1])

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
