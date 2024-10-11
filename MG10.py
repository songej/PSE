import random
import streamlit as st

st.title('PSE Gamma StudyMate')

# 기본 그룹 멤버
all_members = ['Angela', 'Kate', 'Lily', 'Noel', 'Rae', 'Rain']

# 팀 멤버 선택 체크박스 (기본값: 모두 체크)
present_members = [member for member in all_members if st.checkbox(f"{member}", value=True)]

# 단어시험 출제자 랜덤 선택
def choose_word_tester(members):
    if len(members) < 1:
        return None, "Not enough members to choose a word tester!"
    return random.choice(members), None

# 팀을 랜덤하게 배정하는 함수 (2명씩의 팀이 우선, 나머지 인원이 있을 경우 3명으로 구성)
def random_teams(members):
    random.shuffle(members)
    num_members = len(members)
    
    if num_members < 2:
        return None, "Not enough members to form a team!"
    
    teams = []
    idx = 0

    if num_members % 2 != 0:  # 홀수 인원이면 먼저 3명 팀을 하나 만듦
        teams.append(members[idx:idx+3])
        idx += 3
    
    while idx < num_members:  # 나머지 인원은 2명씩 팀을 구성
        teams.append(members[idx:idx+2])
        idx += 2

    return teams, None

# Mix It Up! 버튼 기능
if st.button('Mix It Up!'):
    if len(present_members) == 0:
        st.write("No members selected! Please select at least 2 members.")
    else:
        # 단어시험 출제자 선택
        word_tester, error = choose_word_tester(present_members)
        if error:
            st.write(error)
        else:
            st.write(f"Word Tester: {word_tester}")
        
        # 팀 구성
        teams, error = random_teams(present_members)
        if error:
            st.write(error)
        else:
            for i, members in enumerate(teams, start=1):
                st.write(f"Gamma G1-{i}: {', '.join(members)}")
