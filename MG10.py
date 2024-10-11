import random
import streamlit as st

st.title('PSE Gamma Shuffler')

# 알파벳 순서로 조원 이름을 표시
names = ['Rae', 'Lily', 'Rain', 'Angela', 'Noel', 'Kate']
sorted_names = sorted(names)

st.write("조원들 (알파벳 순):")
st.write(", ".join(sorted_names))

def random_teams():
    teams = ['Gamma G1-1', 'Gamma G1-2', 'Gamma G1-3']
    
    # 이름을 무작위로 섞기
    random.shuffle(names)
    team_assignments = {teams[i]: names[i*2:(i+1)*2] for i in range(3)}
    return team_assignments

# Mix It Up 버튼을 눌렀을 때 랜덤 조편성 결과 표시
if st.button('Mix It Up!'):
    team_assignments = random_teams()
    st.write("랜덤 조편성 결과:")
    for team, members in team_assignments.items():
        st.write(f"{team}: {', '.join(members)}")
