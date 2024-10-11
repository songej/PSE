import random
import streamlit as st

st.title('PSE Gamma Shuffler')

# 기본 그룹 멤버
all_members = ['Angela', 'Kate', 'Lily', 'Noel', 'Rae', 'Rain']
teams = ['Gamma G1-1', 'Gamma G1-2', 'Gamma G1-3']

# 결석 인원을 선택할 수 있는 체크박스 인터페이스
st.write("Select absent members:")
absent_members = []
for member in all_members:
    if st.checkbox(f"{member}", key=member):
        absent_members.append(member)

# 결석자를 제외한 현재 조원 명단
present_members = [member for member in all_members if member not in absent_members]

# 팀을 랜덤하게 배정하는 함수
def random_teams():
    random.shuffle(present_members)  # 현재 참석한 인원 섞기
    team_count = len(present_members) // 2  # 기본적으로 2명씩 묶음
    extra_members = len(present_members) % 2  # 인원이 홀수면 1명이 남음
    
    # 팀을 나누는 로직
    teams_dict = {}
    idx = 0
    for i in range(team_count):
        teams_dict[teams[i]] = present_members[idx:idx+2]
        idx += 2

    # 남은 인원이 있을 경우 마지막 팀에 추가
    if extra_members:
        teams_dict[teams[team_count-1]].append(present_members[-1])
    
    return teams_dict

# 버튼을 눌러 팀을 섞는 기능
if st.button('Mix It Up!'):
    if len(present_members) < 2:
        st.write("Not enough members to form a team!")
    else:
        team_assignments = random_teams()
        st.write("Random Team Assignments:")
        for team, members in team_assignments.items():
            st.write(f"{team}: {', '.join(members)}")
