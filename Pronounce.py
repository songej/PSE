import streamlit as st
import requests
import re

# Streamlit 인터페이스 구성
st.title("Phonetic Transcription Finder")  # 프로그램 제목 설정
st.write("발음기호를 가져올 단어 목록을 입력하세요. (한 줄에 하나씩)")  # 사용자 안내 메시지

# 단어 리스트 입력 받기
word_list = st.text_area("단어 입력:", height=200).splitlines()  # 여러 줄 입력을 각 라인별로 리스트로 분리

# API 키 및 URL 설정 (실제 API 키로 'YOUR_API_KEY'를 교체)
API_KEY = 'YOUR_API_KEY'
API_URL = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/{}?key={}"

# 복수형을 단수형으로 변환하는 규칙 기반 함수
def get_singular(word):
    if word.endswith('ies') and len(word) > 3:
        return word[:-3] + 'y'  # 예: 'studies' -> 'study'
    elif word.endswith('es') and len(word) > 2:
        return word[:-2]  # 예: 'wishes' -> 'wish'
    elif word.endswith('s') and len(word) > 1:
        return word[:-1]  # 예: 'cats' -> 'cat'
    return word  # 복수형 변환에 해당하지 않으면 원래 단어 그대로 반환

# 발음기호를 API에서 가져오는 함수
def get_phonetic(word):
    try:
        # API 요청 보내기 (타임아웃 설정: 10초)
        response = requests.get(API_URL.format(word, API_KEY), timeout=10)
        response.raise_for_status()  # HTTP 상태 코드가 오류인 경우 예외 발생
        
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
        st.error("JSON 데이터를 파싱하는 중 오류가 발생했습니다.")
    return "N/A"  # 발음기호가 없는 경우 기본값 "N/A" 반환

# 단어를 규칙에 따라 처리하여 발음기호를 가져오는 함수
def process_word(word):
    if not word.strip():  # 공백 또는 빈 문자열인 경우 "N/A" 반환
        return "N/A"
    
    tokens = re.split(r'([ \-/.])', word)
    phonetic_tokens = []  # 발음기호 저장 리스트

    for token in tokens:
        if re.match(r'[ \-/.]', token):  # 구분 문자 그대로 저장
            phonetic_tokens.append(token)
        else:
            transcription = get_phonetic(token)
            if transcription == "N/A":  # 발음기호가 없는 경우 단수형 변환 후 다시 시도
                singular_form = get_singular(token)
                if singular_form != token:
                    transcription = get_phonetic(singular_form)
                    if transcription != "N/A":
                        transcription += f" ({singular_form})"
            phonetic_tokens.append(transcription if transcription != "N/A" else "N/A")

    return ''.join(phonetic_tokens)  # 최종적으로 모든 토큰 합쳐서 반환

# API 호출 버튼 - 클릭 시 발음기호 찾기
if st.button("Get Phonetic Transcriptions"):
    if word_list:  # 단어가 입력된 경우에만 실행
        with st.spinner("발음기호를 가져오는 중입니다..."):  # 스피너 추가
            transcriptions = {word: process_word(word) for word in word_list if word.strip()}
        
        # 발음기호 결과 출력
        st.write("## Phonetic Transcriptions")
        st.table(list(transcriptions.items()))  # 단어와 발음기호를 테이블 형태로 출력
    else:
        st.warning("단어를 최소 하나 입력하세요.")  # 단어 미입력 시 경고 메시지
