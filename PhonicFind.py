import streamlit as st
import requests
import re
import pandas as pd
import time  # API 요청 간의 지연을 위해 추가

st.set_page_config(page_title="PhonicFind", page_icon="🔠")

st.title("PhonicFind: PSE 발음기호 찾기")

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
        response = requests.get(API_URL.format(word, API_KEY), timeout=60)
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
            time.sleep(0.5)  # API 요청 사이에 지연 추가
    return ''.join(phonetic_tokens)

# 발음기호 가져오기 실행
if st.button("Get Phonetic Transcriptions"):
    if not API_KEY:
        st.error("API Key를 입력하세요.")
    elif word_list:
        with st.spinner("발음기호를 가져오는 중입니다..."):
            transcriptions = {}
            missing_words = []
            for word in word_list:
                if word.strip():
                    transcription = process_word(word)
                    transcriptions[word] = transcription
                    if "[N/A]" in transcription:
                        missing_words.append(word)
            # 결과 출력
            df = pd.DataFrame(list(transcriptions.items()), columns=["Word", "Phonetic (with Stress)"])
            df.index += 1
            def highlight_na(value):
                if '[N/A]' in value:
                    return 'background-color: yellow'
                return ''
            styled_df = df.style.applymap(highlight_na, subset=['Phonetic (with Stress)'])
            st.dataframe(styled_df)
            
            # 누락된 단어 표시
            if missing_words:
                st.warning(f"발음기호를 찾지 못한 단어들: {', '.join(missing_words)}")
    else:
        st.warning("단어를 최소 하나 입력하세요.")
