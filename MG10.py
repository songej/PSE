import random
import streamlit as st

# 페이지 설정 (wide 레이아웃을 모바일에서 비활성화 옵션 고려)
st.set_page_config(layout="wide", page_title="PSE Gamma StudyMate", page_icon="🎓")

# 반응형 스타일 추가 (모바일 대응)
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
    
    @media (max-width: 768px) {
        .block-container {
            padding-top: 0.5rem;
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

st.title('PSE Gamma StudyMate')

# 기본 그룹 멤버
all_members = ['Angela', 'Kate', 'Lily', 'Noel', 'Rae', 'Rain']

# 팀 멤버 선택 (multiselect로 간결하게 멤버 선택)
present_members = st.multiselect("Select Members", all_members, default=all_members)

# 단어시험 출제자 및 팀 랜덤 배정 함수
def assign_roles(members):
    num_members = len(members)
    if num_members < 2:
        return None, [], "Not enough members to form a team!"
    
    # 랜덤으로 출제자를 선택하고, 남은 멤버는 다시 섞어 팀 구성
    word_tester = random.choice(members)
    remaining_members = [m for m in members if m != word_tester]  # 출제자를 제외한 나머지 멤버
    random.shuffle(remaining_members)

    # 2명씩 팀 구성
    teams = [remaining_members[i:i+2] for i in range(0, len(remaining_members), 2)]

    # 홀로 남는 인원 처리 (마지막 팀에 한 명만 있을 경우 앞 팀에 추가)
    if len(teams) > 1 and len(teams[-1]) == 1:
        teams[-2].append(teams.pop()[0])

    return word_tester, teams, None

# Mix It Up! 버튼 기능
if st.button('Mix It Up!'):
    if not present_members:
        st.error("No members selected! Please choose at least two members.")
    else:
        with st.spinner("Mixing teams and choosing the Vocabulary Tester..."):
            word_tester, teams, error = assign_roles(present_members)
        if error:
            st.error(error)
        else:
            st.success(f"Vocabulary Tester: {word_tester}")
            for i, team in enumerate(teams, start=1):
                st.write(f"Gamma G1-{i}: {', '.join(team)}")
