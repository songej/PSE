import streamlit as st
import requests
import re
import pandas as pd  # pandas 임포트 추가

# 프로그램 제목
st.title("Phonetic Transcription Finder")

st.markdown("""
Merriam-Webster Dictionary API 웹사이트에서 무료로 제공하는 API 키를 입력하고,  
하루에 1000개까지 한꺼번에 발음기호를 찾아보세요.
1. [Merriam-Webster's Developer Center](https://dictionaryapi.com/register/index) 회원가입
   - Request API Key (1) 는 Collegiate Dictionary 선택
   - Request API Key (2) 는 Learners Dictionary 선택
2. 이메일 인증
3. [Your Keys 페이지](https://dictionaryapi.com/account/my-keys) 에서 Key (Dictionary): 부분의 코드를 복사해서 붙여넣기
""")

# API 키 입력 받기
API_KEY = st.text_input("API Key 입력:", type="password")

# 단어 리스트 입력 받기
st.write("발음기호를 가져올 단어 목록을 입력하세요. (한 줄에 하나씩)")
word_list = st.text_area("단어 입력:", height=200).splitlines()

# API URL 설정
API_URL = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/{}?key={}"

# 복수형을 단수형으로 변환
def get_singular(word):
    """단어를 복수형에서 단수형으로 변환합니다."""
    if word.endswith('ies') and len(word) > 3:
        return word[:-3] + 'y'
    elif word.endswith('es') and len(word) > 2:
        return word[:-2]
    elif word.endswith('s') and len(word) > 1:
        return word[:-1]
    return word

# 발음기호를 API에서 가져오기
def get_phonetic(word):
    """API에서 발음기호를 가져오고 오류를 처리합니다."""
    try:
        response = requests.get(API_URL.format(word, API_KEY), timeout=60)
        response.raise_for_status()
        if not response.text.strip():
            st.error("API에서 빈 응답을 받았습니다.")
            return "N/A"
        data = response.json()
        if data and isinstance(data, list) and 'hwi' in data[0] and 'prs' in data[0]['hwi']:
            return data[0]['hwi']['prs'][0].get('mw', "N/A")
        else:
            st.warning(f"'{word}'에 대한 발음기호가 존재하지 않습니다.")
    except requests.exceptions.RequestException as e:
        st.error(f"API 오류 발생: {e}")
    except ValueError:
        st.error("API에서 예상하지 않은 응답을 받았습니다. API 키를 확인하세요.")
    return "N/A"

# 단어 처리 후 발음기호 가져오기
def process_word(word):
    """단어의 발음기호를 규칙에 따라 가져옵니다."""
    tokens = re.split(r'([ \-/.])', word)
    phonetic_tokens = []

    for token in tokens:
        if re.match(r'[ \-/.]', token):
            phonetic_tokens.append(token)
        elif token.strip():
            transcription = get_phonetic(token)
            if transcription == "N/A":
                singular_form = get_singular(token)
                if singular_form != token:
                    transcription = get_phonetic(singular_form)
                    if transcription != "N/A":
                        transcription += f" [{singular_form}]"
            phonetic_tokens.append(transcription if transcription != "N/A" else "[N/A]")

    return ''.join(phonetic_tokens)

# 발음기호 찾기 버튼 클릭 시
if st.button("Get Phonetic Transcriptions"):
    if not API_KEY:
        st.error("API Key를 입력하세요.")
    elif word_list:
        with st.spinner("발음기호를 가져오는 중입니다..."):
            transcriptions = {word: process_word(word) for word in word_list if word.strip()}
        
        df = pd.DataFrame(list(transcriptions.items()), columns=["Word", "Phonetic (with Stress)"])
        df.index += 1

        # [N/A]가 포함된 셀을 노란색 배경으로 스타일링
        def highlight_na(value):
            if '[N/A]' in value:
                return 'background-color: yellow'
            return ''
        
        styled_df = df.style.applymap(highlight_na, subset=['Phonetic (with Stress)'])
        st.dataframe(styled_df)  # 스타일링된 데이터프레임 표시
    else:
        st.warning("단어를 최소 하나 입력하세요.")
