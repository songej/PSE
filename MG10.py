import random
import streamlit as st

st.title('PSE Gamma Shuffler')

# 기본 그룹 멤버
all_members = ['Angela', 'Kate', 'Lily', 'Noel', 'Rae', 'Rain']

# 팀 멤버 선택 체크박스 (기본값: 모두 체크)
st.write("Select team members (uncheck absent members):")
present_members = []
for member in all_members:
    if st.checkbox(f"{member}", value=True, key=member):
        present_members.append(member)

# 팀 이름을 동적으로 생성하는 함수
def generate_teams(num_teams):
    return [f"Gamma G1-{i+1}" for i in range(num_teams)]

# 팀을 랜덤하게 배정하는 함수 (팀의 구성원 수를 균형 있게 나눔)
def random_teams():
    random.shuffle(present_members)
    
    # 팀 수를 결정
    num_members = len(present_members)
    if num_members < 2:
        return None, "Not enough members to form a team!"
    
    team_size = 2 if num_members % 3 != 0 else 3  # 팀의 구성 인원 결정 (2명 또는 3명씩)
    num_teams = num_members // team_size
    
    if num_members % 2 != 0 and num_teams > 1:  # 나머지 인원이 있을 경우 조정
        last_team_size = num_members - (team_size * (num_teams - 1))
        teams = [present_members[i*team_size:(i+1)*team_size] for i in range(num_teams-1)]
        teams.append(present_members[-last_team_size:])
    else:
        teams = [present_members[i*team_size:(i+1)*team_size] for i in range(num_teams)]
    
    return teams, None

# 버튼을 눌러 팀을 섞는 기능
if st.button('Mix It Up!'):
    if len(present_members) == 0:
        st.write("No members selected! Please select at least 2 members.")
    else:
        team_assignments, error_message = random_teams()
        if error_message:
            st.write(error_message)
        else:
            num_teams = len(team_assignments)
            team_names = generate_teams(num_teams)
            
            st.write("Random Team Assignments:")
            for i, members in enumerate(team_assignments):
                st.write(f"{team_names[i]}: {', '.join(members)}")
