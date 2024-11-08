import streamlit as st
import requests
import re
import pandas as pd

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

st.title("PhonicFind: PSE 발음기호 찾기")

st.markdown("""
Merriam-Webster Dictionary API 웹사이트에서 무료로 제공하는 API 키를 입력하고,  
하루에 1000 단어까지 한꺼번에 발음기호를 찾아보세요.
1. [Merriam-Webster's Developer Center](https://dictionaryapi.com/register/index) 회원가입
   - Request API Key (1) 는 Collegiate Dictionary 선택
   - Request API Key (2) 는 Learners Dictionary 선택
2. 이메일 인증
3. [Your Keys 페이지](https://dictionaryapi.com/account/my-keys) 에서 Key (Dictionary): 부분의 코드를 복사해서 붙여넣기
""")

API_KEY = st.text_input("API Key 입력:", type="password")

st.write("발음기호를 가져올 단어 목록을 입력하세요. (한 줄에 하나씩)")
word_list = st.text_area("단어 입력:", height=200).splitlines()

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

# API에서 발음기호 가져오기 (10개씩 묶어서 처리)
def get_phonetics(word_batch):
    """단어 목록을 10개씩 나누어 발음기호를 가져옵니다."""
    batch_phonetics = {}
    for word in word_batch:
        try:
            response = requests.get(API_URL.format(word, API_KEY), timeout=60)
            response.raise_for_status()
            data = response.json()
            if data and isinstance(data, list) and 'hwi' in data[0] and 'prs' in data[0]['hwi']:
                phonetic = data[0]['hwi']['prs'][0].get('mw', "N/A")
                batch_phonetics[word] = phonetic
            else:
                batch_phonetics[word] = "[N/A]"
        except requests.exceptions.RequestException as e:
            st.error(f"API 오류 발생: {e}")
            batch_phonetics[word] = "[N/A]"
        except ValueError:
            st.error("API에서 예상하지 않은 응답을 받았습니다. API 키를 확인하세요.")
            batch_phonetics[word] = "[N/A]"
    return batch_phonetics

# 단어 처리 후 발음기호 가져오기
def process_word(word):
    """단어의 발음기호를 규칙에 따라 가져옵니다."""
    tokens = re.split(r'([ \-/,;.!?:])', word)
    phonetic_tokens = []
    for token in tokens:
        if re.match(r'[ \-/,;.!?:]', token):
            phonetic_tokens.append(token)
        elif token.strip(): 
            phonetic_tokens.append(transcriptions.get(token, "[N/A]"))
    return ''.join(phonetic_tokens)

# 발음기호 가져오기 실행
if st.button("Get Phonetic Transcriptions"):
    if not API_KEY:
        st.error("API Key를 입력하세요.")
    elif word_list:
        with st.spinner("발음기호를 가져오는 중입니다..."):
            transcriptions = {}
            for i in range(0, len(word_list), 10):
                word_batch = word_list[i:i+10]
                batch_transcriptions = get_phonetics(word_batch)
                transcriptions.update(batch_transcriptions)
        
            processed_transcriptions = {word: process_word(word) for word in word_list if word.strip()}
            df = pd.DataFrame(list(processed_transcriptions.items()), columns=["Word", "Phonetic (with Stress)"])
            df.index += 1
            
            def highlight_na(value):
                if '[N/A]' in value:
                    return 'background-color: yellow'
                return ''
            
            styled_df = df.style.applymap(highlight_na, subset=['Phonetic (with Stress)'])
            st.dataframe(styled_df)
    else:
        st.warning("단어를 최소 하나 입력하세요.")
