import streamlit as st
import requests
import re
import pandas as pd
import time
from bs4 import BeautifulSoup
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

st.write("발음기호를 가져올 단어 목록을 입력하세요. (한 줄에 하나씩)")
word_list = list(filter(None, map(str.strip, st.text_area("단어 입력:", height=200).splitlines())))

# Daum 사전에서 발음기호 가져오기 함수 정의
@lru_cache(maxsize=5000)
def get_phonetic_from_daum(word, retries=3):
    url = f"https://dic.daum.net/search.do?q={word}"
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            phonetic = soup.find('span', {'class': 'txt_pronounce'})
            if phonetic:
                return phonetic.get_text()
            return "[N/A]"  # 발음기호가 없는 경우
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:  # 재시도 가능
                time.sleep(2 ** attempt)  # 지수적 지연
                continue
            st.error(f"웹 요청 오류 발생 ({word}): {e}")
            return "[N/A]"

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

# 추가 캐싱을 위한 딕셔너리
na_cache = set()  # 이미 N/A로 확인된 단어를 저장

# PSE 변환 규칙
conversion_table = {
    "au̇": "ɑu",
    "ȯi자음": "oi:",
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

# 모음 강세 기호
vowel_mapping = {
    "i": "í",
    "e": "é",
    "ʌ": "ʌ́",
    "ɑ:": "ɑ́:",
    "æ": "ǽ",
    "ɔ:": "ɔ́:",
    "u:": "ú:",
    "i:": "í:",
    "ə": "ə́",
    "u": "ú",
    "ɑi": "ɑ́i",
    "ɑi:": "ɑ́i:",
    "ei": "éi",
    "ei:": "éi:",
    "oi": "ói",
    "oi:": "ói:",
    "ou": "óu",
    "ɑu": "ɑ́u",
    "ər": "ə́r",
    "er": "ér",
    "i:r": "í:r",
    "or": "ór",
    "ɔ:r": "ɔ́:r",
    "u:r": "ú:r"
}

# 자음 정의
consonant_pattern = r"[bcdfghjklmnpqrstvwxyz]"

# PSE 규칙 변환
def convert_to_pse(ipa: str) -> str:
    # 1. PSE 변환 규칙 적용
    for pattern, pse in conversion_table.items():
        if pattern.endswith("자음"):
            base_pattern = pattern[:-2]
            ipa = re.sub(f"{base_pattern}(?={consonant_pattern})", pse, ipa)
        else:
            ipa = ipa.replace(pattern, pse)

    # 2. 강세 기호 변환: 모든 `ˈ` 뒤의 첫 모음 패턴에 강세 기호를 한 번에 적용
    ipa = re.sub(
        r"ˈ((?:ɑi|ei|oi|ou|ɑu|[iueɔʌəɑæ]+:?r?))",  # 모든 모음 패턴에 대응
        lambda m: vowel_mapping.get(m.group(1), m.group(1)),
        ipa
    )

    # 3. 변환 후 모든 `ˈ` 기호 제거
    ipa = ipa.replace("ˈ", "")
    
    return ipa

# 각 단어의 발음기호 가져오기 - 최적화된 함수
def process_word(word):
    tokens = re.split(r'([ \-/,;.!?:])', word)
    phonetic_tokens = []
    for token in tokens:
        if re.match(r'[ \-/,;.!?:]', token):
            phonetic_tokens.append(token)
        elif token.strip():
            transcription = get_phonetic_from_daum(token)
            phonetic_tokens.append(transcription)
    return ''.join(phonetic_tokens)

# 세션 상태로 결과 저장
if "results_df" not in st.session_state:
    st.session_state["results_df"] = pd.DataFrame()

# 버튼 선택 시 발음기호 가져오기
if st.button("발음기호 알아보기"):
    if word_list:
        with st.spinner("발음기호를 가져오는 중입니다..."):
            results = []
            missing_words = []
            processing_status = st.empty()
            for idx, word in enumerate(word_list, start=1):
                processing_status.info(f"{idx}/{len(word_list)}: '{word}' 처리 중...")
                transcription = process_word(word)
                pse_transcription = convert_to_pse(transcription)  # PSE 발음기호
                results.append((word, transcription, pse_transcription))
                if "[N/A]" in transcription:
                    missing_words.append(word)

            # 결과 세션 저장
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
    st.write("(PSE 발음기호 표기는 보완 중입니다.)")
    styled_df = df.style.applymap(highlight_cells, subset=['Phonetic (with Stress)', 'PSE'])
    st.dataframe(styled_df, use_container_width=True)

    # CSV 다운로드 (UTF-8 with BOM)
    csv = df.to_csv(index=True, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button(
        label="발음기호 목록 다운로드",
        data=csv,
        file_name='PhonicFind.csv',
        mime='text/csv'
    )
