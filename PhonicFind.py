import streamlit as st
import requests
import re
import pandas as pd
import time
import io
from functools import lru_cache

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
word_list = list(filter(None, map(str.strip, st.text_area("단어 입력:", height=200).splitlines())))

API_URL = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/{}?key={}"

@lru_cache(maxsize=1000)
def get_singular(word):
    """복수형을 단수형으로 변환"""
    if word.endswith('ies') and len(word) > 3:
        return word[:-3] + 'y'
    elif word.endswith('es') and len(word) > 2:
        return word[:-2]
    elif word.endswith('s') and len(word) > 1:
        return word[:-1]
    return word

@lru_cache(maxsize=1000)
def get_phonetic(word):
    """발음기호 가져오기"""
    try:
        response = requests.get(API_URL.format(word, API_KEY), timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list) and data and 'hwi' in data[0] and 'prs' in data[0]['hwi']:
            return data[0]['hwi']['prs'][0].get('mw', "N/A")
        else:
            return "N/A"
    except requests.exceptions.RequestException as e:
        st.error(f"API 오류 발생 ({word}): {e}")
    except (ValueError, KeyError, IndexError):
        st.error(f"API 응답 오류 ({word}): API 키를 확인하세요.")
    return "N/A"

def process_word(word): 
    """각 단어의 발음기호 가져오기"""
    tokens = re.split(r'([ \-/,;.!?:])', word)
    phonetic_tokens = []
    for token in tokens:
        if re.match(r'[ \-/,;.!?:]', token):
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
            time.sleep(0.1)
    return ''.join(phonetic_tokens)

def validate_api_key(api_key):
    """API Key 유효성 검증"""
    test_word = "test"
    try:
        response = requests.get(API_URL.format(test_word, api_key), timeout=10)
        response.raise_for_status()
        data = response.json()
        return isinstance(data, list)
    except requests.exceptions.RequestException:
        return False

if "results_df" not in st.session_state:
    st.session_state["results_df"] = pd.DataFrame()

if st.button("발음기호 알아보기"):
    if not API_KEY:
        st.error("API Key를 입력하세요.")
    elif not validate_api_key(API_KEY):
        st.error("유효하지 않은 API Key입니다. 다시 확인해주세요.")
    elif word_list:
        with st.spinner("발음기호를 가져오는 중입니다..."):
            results = []
            missing_words = []
            for idx, word in enumerate(word_list, start=1):
                st.info(f"{idx}/{len(word_list)}: '{word}' 처리 중...")
                transcription = process_word(word)
                results.append((word, transcription))
                if "[N/A]" in transcription:
                    missing_words.append(word)
                
            df = pd.DataFrame(results, columns=["Word", "Phonetic (with Stress)"])
            df.index += 1
            st.session_state["results_df"] = df  # 결과표 세션 저장
            if missing_words:
                st.warning(f"발음기호를 찾지 못한 단어들: {', '.join(missing_words)}")

# 결과표 세션 유지
if not st.session_state["results_df"].empty:
    df = st.session_state["results_df"]
    def highlight_na(value):
        return 'background-color: yellow' if '[N/A]' in value else ''
    styled_df = df.style.applymap(highlight_na, subset=['Phonetic (with Stress)'])
    st.table(styled_df)

    # CSV 다운로드 (UTF-8 with BOM)
    csv = df.to_csv(index=True, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button(
        label="결과표 다운로드",
        data=csv,
        file_name='phonetic_transcriptions.csv',
        mime='text/csv'
    )
