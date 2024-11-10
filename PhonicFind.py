import streamlit as st
import requests
import re
import pandas as pd
import time
import io

st.set_page_config(page_title="PhonicFind", page_icon="🔠")

st.markdown(
    """
    <style>
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem;
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

st.title("PhonicFind: PSE 발음찾기")

st.markdown("""
메리엄-웹스터 사전에서 무료로 제공하는 API 키를 입력하고,  
하루에 1000 단어까지 한꺼번에 발음기호를 찾아보세요.
1. Merriam-Webster's Developer Center [회원가입](https://dictionaryapi.com/register/index)
   - Request API Key (1) 에는 Collegiate Dictionary 선택
   - Request API Key (2) 에는 Learners Dictionary 선택
2. 이메일 인증하고 [로그인](https://dictionaryapi.com/sign-in)
3. [Your Keys 페이지](https://dictionaryapi.com/account/my-keys) 에서 Key (Dictionary): 부분의 코드를 복사해서 붙여넣기
""")

API_KEY = st.text_input("API Key 입력:", type="password")

st.write("발음기호를 가져올 단어 목록을 입력하세요. (한 줄에 하나씩)")
word_list = st.text_area("단어 입력:", height=200).splitlines()

API_URL = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/{}?key={}"

# 복수형을 단수형으로 변환
def get_singular(word):
    if word.endswith('ies') and len(word) > 3:
        return word[:-3] + 'y'
    elif word.endswith('es') and len(word) > 2:
        return word[:-2]
    elif word.endswith('s') and len(word) > 1:
        return word[:-1]
    return word

# API에서 발음기호 가져오기
def get_phonetic(word):
    try:
        response = requests.get(API_URL.format(word, API_KEY), timeout=180)
        response.raise_for_status()
        data = response.json()
        
        if data and isinstance(data, list) and 'hwi' in data[0] and 'prs' in data[0]['hwi']:
            return data[0]['hwi']['prs'][0].get('mw', "N/A")
        else:
            return "N/A"  # 데이터가 있지만 발음기호가 없을 때
    except requests.exceptions.RequestException as e:
        st.error(f"API 오류 발생 ({word}): {e}")
    except ValueError:
        st.error(f"API 응답 오류 ({word}): API 키를 확인하세요.")
    return "N/A"

# 단어 처리 후 발음기호 가져오기
def process_word(word): 
    tokens = re.split(r'([ \-/,;.!?:])', word)  # 다양한 구분자 고려
    phonetic_tokens = []
    for token in tokens:
        if re.match(r'[ \-/,;.!?:]', token):  # 발음기호에 구분자 추가
            phonetic_tokens.append(token)
        elif token.strip():  # 공백이 아닌 실제 단어만 처리
            transcription = get_phonetic(token)
            if transcription == "N/A":  # 발음기호가 없는 경우 단수형 변환 후 다시 시도
                singular_form = get_singular(token)
                if singular_form != token:
                    transcription = get_phonetic(singular_form)
                    if transcription != "N/A":
                        transcription += f" [{singular_form}]"  # 단수형 단어를 [ ]로 표시
            phonetic_tokens.append(transcription if transcription != "N/A" else "[N/A]")
            time.sleep(0.1)  # API 요청 사이 지연
    return ''.join(phonetic_tokens)

# 발음기호 가져오기 실행
if st.button("발음기호 알아보기"):
    if not API_KEY:
        st.error("API Key를 입력하세요.")
    elif word_list:
        with st.spinner("발음기호를 가져오는 중입니다..."):
            results = []  # 결과를 저장할 리스트로 수정
            missing_words = []
            for word in word_list:
                if word.strip():
                    transcription = process_word(word)
                    results.append((word, transcription))  # 리스트에 단어와 발음기호 추가
                    if "[N/A]" in transcription:
                        missing_words.append(word)
            # 결과 출력
            df = pd.DataFrame(results, columns=["Word", "Phonetic (with Stress)"])  # 리스트를 데이터프레임으로 변환
            df.index += 1
            def highlight_na(value):
                if '[N/A]' in value:
                    return 'background-color: yellow'
                return ''
            styled_df = df.style.applymap(highlight_na, subset=['Phonetic (with Stress)'])
            st.table(styled_df)

            # 누락된 단어 표시
            if missing_words:
                st.warning(f"발음기호를 찾지 못한 단어들: {', '.join(missing_words)}")

            # CSV 다운로드 (UTF-8 with BOM)
            csv = df.to_csv(index=True, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(
                label="결과표 다운로드",
                data=csv,
                file_name='phonetic_transcriptions.csv',
                mime='text/csv'
            )
    else:
        st.warning("최소 한 단어를 입력하세요.")
