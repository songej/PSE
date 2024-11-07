import streamlit as st
import requests
import re
from nltk.corpus import wordnet
from nltk import download

# NLTK 다운로드
try:
    wordnet.ensure_loaded()  # 'wordnet' 모듈을 사용할 수 있는지 확인
except:
    download('wordnet')  # 필요 시 'wordnet' 모듈 다운로드

# Streamlit 인터페이스
st.title("Phonetic Transcription Finder")
st.write("발음기호를 가져올 단어 목록을 입력하세요. (한 줄에 하나씩)")

# 단어 리스트 입력
word_list = st.text_area("단어 입력:", height=200).splitlines()

# API 키 (실제 API 키로 'YOUR_API_KEY'를 교체하세요)
API_KEY = 'YOUR_API_KEY'
API_URL = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/{}?key={}"

# 단어가 복수형인지 확인하고 단수형으로 변환하는 함수
def get_singular(word):
    if not word:  # 단어가 비어 있을 경우 처리
        return word
    synsets = wordnet.synsets(word)
    if synsets and synsets[0].lemma_names()[0] == word:
        return word
    if word.endswith('s'):
        return word[:-1]
    return word

# 발음기호를 가져오는 함수
def get_phonetic(word):
    try:
        response = requests.get(API_URL.format(word, API_KEY))
        response.raise_for_status()  # HTTP 에러 발생 시 예외 처리
        data = response.json()
        # JSON 데이터 구조 확인 후 발음기호가 있는 경우 반환
        if data and isinstance(data, list) and 'hwi' in data[0] and 'prs' in data[0]['hwi']:
            return data[0]['hwi']['prs'][0]['mw']
    except (requests.exceptions.RequestException, KeyError, IndexError) as e:
        st.error(f"API 오류 발생: {e}")
    return "N/A"  # 발음기호가 없는 경우 N/A 반환

# 각 단어를 규칙에 맞게 처리하는 함수
def process_word(word):
    # 단어가 비어 있거나 공백인 경우 건너뜀
    if not word.strip():
        return "N/A"
    
    # 규칙 #1: 구분자로 분리하여 각 토큰을 개별적으로 처리하고, 원래 구분자로 다시 결합
    tokens = re.split(r'([ \-/.])', word)  # 구분자로 단어 분리
    phonetic_tokens = []
    
    for token in tokens:
        if re.match(r'[ \-/.]', token):  # 구분자는 그대로 추가
            phonetic_tokens.append(token)
        else:
            # 발음기호를 가져오고, 실패 시 단수형 변환 후 재시도
            transcription = get_phonetic(token)
            if transcription == "N/A":
                singular_form = get_singular(token)
                # 단수형으로 변환한 단어로 발음기호 재시도
                if singular_form != token:
                    transcription = get_phonetic(singular_form)
                    # 단수형으로 성공 시 "(단수형)"으로 표시
                    if transcription != "N/A":
                        transcription += f" ({singular_form})"
            phonetic_tokens.append(transcription if transcription != "N/A" else "N/A")

    return ''.join(phonetic_tokens)  # 원래 구분자로 결합하여 반환

# API 호출을 위한 버튼
if st.button("Get Phonetic Transcriptions"):
    if word_list:
        # 발음기호 가져오기 및 결과 표시
        transcriptions = {word: process_word(word) for word in word_list if word.strip()}
        
        # 결과를 테이블 형태로 출력
        st.write("## Phonetic Transcriptions")
        st.table(list(transcriptions.items()))
    else:
        st.warning("단어를 최소 하나 입력하세요.")
