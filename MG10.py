import random
import streamlit as st

st.title('PSE Gamma StudyMate')

# 기본 그룹 멤버
all_members = ['Angela', 'Kate', 'Lily', 'Noel', 'Rae', 'Rain']

# 팀 멤버 선택 체크박스 (기본값: 모두 체크)
present_members = [member for member in all_members if st.checkbox(f"{member}", value=True)]

# 단어시험 출제자 및 팀 랜덤 배정 함수
def assign_roles(members):
    if not members or len(members) < 2:
        return None, None, "Not enough members to form a team!"
    
    random.shuffle(members)
    word_tester = random.choice(members)
    
    # 팀 구성 (홀수인 경우 첫 번째 팀에 3명 배정)
    teams = []
    num_members = len(members)
    idx = 0

    if num_members % 2 != 0:  # 홀수 인원이면 첫 번째 팀에 3명 배정
        teams.append(members[:3])
        idx = 3

    # 나머지 팀을 2명씩 구성
    while idx < num_members:
        teams.append(members[idx:idx+2])
        idx += 2

    return word_tester, teams, None

# Mix It Up! 버튼 기능
if st.button('Mix It Up!'):
    if not present_members:
        st.write("No members selected! Please select at least 2 members.")
    else:
        word_tester, teams, error = assign_roles(present_members)
        if error:
            st.write(error)
        else:
            st.write(f"Word Tester: {word_tester}")
            for i, team in enumerate(teams, start=1):
                st.write(f"Gamma G1-{i}: {', '.join(team)}")

