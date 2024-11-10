import streamlit as st
import requests
import re
import pandas as pd
import time
from functools import lru_cache

st.set_page_config(page_title="PhonicFind", page_icon="🔠")

st.markdown(
    """
    <style>
    @media (max-width: 768px) {
        .block-container { padding-top: 1rem; }
        .stButton button { font-size: 16px; padding: 8px; }
        .stMarkdown p { font-size: 16px; }
    }
    </style>
    """, unsafe_allow_html=True
)

st.title("PhonicFind: 발음기호 찾기")

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

# 복수형을 단수형으로 변환
@lru_cache(maxsize=1000)
def get_singular(word):
    if word.endswith('ies') and len(word) > 3:
        return word[:-3] + 'y'
    elif word.endswith('es') and len(word) > 2:
        return word[:-2]
    elif word.endswith('s') and len(word) > 1:
        return word[:-1]
    return word

# 발음기호 가져오기
@lru_cache(maxsize=5000)
def get_phonetic(word, api_key, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(API_URL.format(word, api_key), timeout=10)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and data and 'hwi' in data[0] and 'prs' in data[0]['hwi']:
                return data[0]['hwi']['prs'][0].get('mw', "N/A")
            return "N/A"
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:  # 재시도 가능
                time.sleep(2 ** attempt)  # 지수적 지연
                continue
            st.error(f"API 오류 발생 ({word}): {e}")
            return "N/A"

# 각 단어의 발음기호 가져오기
def process_word(word, api_key): 
    tokens = re.split(r'([ \-/,;.!?:])', word)
    phonetic_tokens = []
    delay = 0.1  # 기본 지연 시간
    for token in tokens:
        if re.match(r'[ \-/,;.!?:]', token):
            phonetic_tokens.append(token)
        elif token.strip():
            transcription = get_phonetic(token, api_key)
            if transcription == "N/A":
                singular_form = get_singular(token)
                if singular_form != token:
                    transcription = get_phonetic(singular_form, api_key)
                    if transcription != "N/A":
                        transcription += f" [{singular_form}]"
            phonetic_tokens.append(transcription if transcription != "N/A" else "[N/A]")
            time.sleep(delay)
            delay = min(delay + 0.05, 0.5)
    return ''.join(phonetic_tokens)

# PSE 변환 규칙
# 변환 표 정의 (긴 문자열 우선 순위 및 새로운 규칙 포함)
conversion_table = {
    "au̇": "ɑu",
    "ȯi자음": "oi:",  # 자음이 뒤따르는 경우
    "ȯi": "oi",
    "ī자음": "ɑi:",
    "ī": "ɑi",
    "ā자음": "ei:",
    "ā": "ei",
    "ȯr": "or",
    "är": "ɔ:r",
    "u̇r": "u:r",
    "ȯ": "ɔ:",
    "ü": "u:",
    "ē": "i:",
    "u̇": "u",
    "i": "i",
    "e": "e",
    "ə": "ʌ",
    "ä": "ɑ:",
    "a": "æ",
    "ō": "ou",
    "ər": "ər",
    "er": "er",
    "ir": "i:r",
    "j": "ʤ",
    "sh": "ʃ"
}

# 모든 모음에 대응하는 강세 기호 매핑
vowel_mapping = {
    "a": "ǽ",
    "e": "é",
    "i": "í",
    "o": "ó",
    "u": "ú",
    "ə": "ə́",
    "ä": "ǽ",
    "ȯ": "ǿ",
    "ü": "ǘ",
    "ē": "ḗ",
    "ī": "ḯ",
    "ā": "ǣ",
    "ō": "ṓ",
    "u̇": "ṹ"
}

# 자음 정의
consonant_pattern = r"[bcdfghjklmnpqrstvwxyz]"

# PSE 규칙 변환
def convert_to_pse(ipa: str) -> str:
    ipa = re.sub(
        r"ˈ([aeiouəäȯüēīāōu̇])",  # ˈ뒤의 첫모음 강세
        lambda m: vowel_mapping.get(m.group(1), m.group(1)),
        ipa,
        count=1
    )
    
    for pattern, pse in conversion_table.items():
        if pattern.endswith("자음"):  # 자음 여부를 판단
            base_pattern = pattern[:-2]
            if re.match(f"^{base_pattern}({consonant_pattern})", ipa):
                return pse
        elif ipa.startswith(pattern):
            return pse
    return ipa

# API Key 유효성 검증
def validate_api_key(api_key):
    test_word = "test"
    try:
        response = requests.get(API_URL.format(test_word, api_key), timeout=10)
        response.raise_for_status()
        data = response.json()
        return isinstance(data, list)
    except requests.exceptions.RequestException:
        return False

# 세션 상태를 사용하여 결과 저장
if "results_df" not in st.session_state:
    st.session_state["results_df"] = pd.DataFrame()

# 버튼 선택 시 발음기호 가져오기
if st.button("발음기호 알아보기"):
    if not API_KEY:
        st.error("API Key를 입력하세요.")
    elif not validate_api_key(API_KEY):
        st.error("유효하지 않은 API Key입니다. 다시 확인해주세요.")
    elif word_list:
        with st.spinner("발음기호를 가져오는 중입니다..."):
            results = []
            missing_words = []
            processing_status = st.empty()
            for idx, word in enumerate(word_list, start=1):
                processing_status.info(f"{idx}/{len(word_list)}: '{word}' 처리 중...")
                transcription = process_word(word, API_KEY)
                pse_transcription = convert_to_pse(transcription)  # PSE 발음기호
                results.append((word, transcription, pse_transcription))
                if "[N/A]" in transcription:
                    missing_words.append(word)

            # 결과를 세션 상태에 저장
            df = pd.DataFrame(results, columns=["Word", "Phonetic (with Stress)", "PSE"])
            df.index += 1
            st.session_state["results_df"] = df
            if missing_words:
                st.warning(f"발음기호를 찾지 못한 단어: {', '.join(missing_words)}")

# 결과 출력
if not st.session_state["results_df"].empty:
    df = st.session_state["results_df"]

    # 결과표 스타일링
    def highlight_cells(value):
        if '[N/A]' in value:
            return 'background-color: red; color: white;'
        elif '[' in value and ']' in value:
            return 'background-color: yellow;'
        return ''

    # 결과표 출력
    styled_df = df.style.applymap(highlight_cells, subset=['Phonetic (with Stress)', 'PSE'])
    st.write(styled_df)

    # CSV 다운로드 (UTF-8 with BOM)
    csv = df.to_csv(index=True, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button(
        label="발음기호 다운로드",
        data=csv,
        file_name='PhonicFind.csv',
        mime='text/csv'
    )
