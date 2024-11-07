import streamlit as st
import requests
import re

# 프로그램 제목
st.title("Phonetic Transcription Finder")

st.write("Merriam-Webster Dictionary API 웹사이트에서 무료로 제공하는 API 키를 입력하세요.")

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
word_list = st.text_area("단어 입력:", height=200).splitlines()  # 여러 줄 입력을 각 라인별로 리스트로 분리

# API URL 설정
API_URL = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/{}?key={}"

# 복수형을 단수형으로 변환
def get_singular(word):
    if word.endswith('ies') and len(word) > 3:
        return word[:-3] + 'y'  # 예: 'studies' -> 'study'
    elif word.endswith('es') and len(word) > 2:
        return word[:-2]  # 예: 'wishes' -> 'wish'
    elif word.endswith('s') and len(word) > 1:
        return word[:-1]  # 예: 'cats' -> 'cat'
    return word  # 복수형 변환에 해당하지 않으면 원래 단어 그대로 반환

# 발음기호를 API에서 가져오기
def get_phonetic(word):
    try:
        # API 요청 보내기 (타임아웃 설정: 60초)
        response = requests.get(API_URL.format(word, API_KEY), timeout=60)
        # 응답이 성공적이지 않으면 상태 코드와 메시지 출력
        response.raise_for_status()        
        # 빈 응답이 아닌지 확인
        if not response.text.strip():
            st.error("API에서 빈 응답을 받았습니다.")
            return "N/A"
        # API 응답을 JSON 형태로 변환
        data = response.json()
        # JSON 데이터 구조 확인 후 발음기호 반환
        if data and isinstance(data, list) and 'hwi' in data[0] and 'prs' in data[0]['hwi']:
            return data[0]['hwi']['prs'][0].get('mw', "N/A")  # 발음기호(mw)가 없으면 "N/A" 반환
        else:
            st.warning(f"'{word}'에 대한 발음기호가 존재하지 않습니다.")  # 발음기호가 없으면 사용자에게 경고
    except requests.exceptions.RequestException as e:
        st.error(f"API 오류 발생: {e}")
    except ValueError:
        # JSON 변환 중 오류 발생 시 예외 처리
        st.error("API에서 예상하지 않은 응답을 받았습니다. API 키를 확인하세요.")
    return "N/A"  # 발음기호가 없는 경우 기본값 "N/A" 반환

# 단어를 규칙에 따라 처리하여 발음기호 가져오기
def process_word(word):
    # 공백을 모두 제거한 상태에서 단어가 비어있으면 "N/A" 반환
    tokens = re.split(r'([ \-/.])', word)
    phonetic_tokens = []  # 발음기호 저장

    for token in tokens:
        if re.match(r'[ \-/.]', token):  # 구분 문자(공백, /, -)는 그대로 추가
            phonetic_tokens.append(token)
        elif token.strip():  # 공백이 아닌 실제 단어인 경우에만 처리
            transcription = get_phonetic(token)
            if transcription == "N/A":  # 발음기호가 없는 경우 단수형 변환 후 다시 시도
                singular_form = get_singular(token)
                if singular_form != token:
                    transcription = get_phonetic(singular_form)
                    if transcription != "N/A":
                        transcription += f" [{singular_form}]"  # 단수형을 [ ]로 표시
            phonetic_tokens.append(transcription if transcription != "N/A" else "[N/A]")  # N/A를 [N/A]로 변경

    return ''.join(phonetic_tokens)  # 최종적으로 모든 결과를 합쳐서 반환

# 발음기호 찾는 API 호출
if st.button("Get Phonetic Transcriptions"):
    if not API_KEY:
        st.error("API Key를 입력하세요.")
    elif word_list:
        with st.spinner("발음기호를 가져오는 중입니다..."):
            transcriptions = {word: process_word(word) for word in word_list if word.strip()}        
            
        # 발음기호 결과 출력
        st.write("## Phonetic Transcriptions")
        st.table(list(transcriptions.items()))
    else:
        st.warning("단어를 최소 하나 입력하세요.")
