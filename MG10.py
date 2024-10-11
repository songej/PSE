import random
import streamlit as st

st.title('PSE Gamma Shuffler')

# 기본 그룹 멤버
all_members = ['Angela', 'Kate', 'Lily', 'Noel', 'Rae', 'Rain']

# 팀 멤버 선택 체크박스 (기본값: 모두 체크)
present_members = [member for member in all_members if st.checkbox(f"{member}", value=True)]

# 팀을 랜덤하게 배정하는 함수 (2명씩의 팀이 우선, 나머지 인원이 있을 경우 3명으로 구성)
def random_teams():
    random.shuffle(present_members)
    num_members = len(present_members)
    
    if num_members < 2:
        return None, "Not enough members to form a team!"
    
    teams = []
    idx = 0

    if num_members % 2 != 0:  # 홀수 인원이면 먼저 3명 팀을 하나 만듦
        teams.append(present_members[idx:idx+3])
        idx += 3
    
    while idx < num_members:  # 나머지 인원은 2명씩 팀을 구성
        teams.append(present_members[idx:idx+2])
        idx += 2

    return teams, None

# 버튼을 눌러 팀을 섞는 기능
if st.button('Mix It Up!'):
    if len(present_members) == 0:
        st.write("No members selected! Please select at least 2 members.")
    else:
        teams, error = random_teams()
        if error:
            st.write(error)
        else:
            for i, members in enumerate(teams, start=1):
                st.write(f"Gamma G1-{i}: {', '.join(members)}")
