import streamlit as st
import openai
import pandas as pd
import io  # io 모듈 추가

st.set_page_config(page_title="PSE Ladder", page_icon="🪜")

# LLM API 설정
try:
    openai.api_key = st.secrets["API_key"]
except KeyError:
    st.error("API key를 설정하지 않았습니다. Streamlit Secrets에 API 키를 추가해주세요.")

# 문장 번역 및 변환
def process_sentence(sentence):
    eng_sentence = ""
    kor_sentence = ""
    
    try:
        # 언어 감지 및 번역 프롬프트 설정
        if any(ord(char) > 127 for char in sentence):  # 한국어가 포함된 경우
            eng_prompt = f"Translate this Korean sentence to English: '{sentence}'"
            kor_sentence = sentence
        else:
            eng_prompt = f"Translate this English sentence to Korean: '{sentence}'"
            eng_sentence = sentence

        # 번역 요청
        with st.spinner("문장을 번역하는 중입니다..."):
            translation_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": eng_prompt}],
                max_tokens=100,
                temperature=0.7
            )
        
        translated_sentence = translation_response.choices[0].message['content'].strip()
        
        # 영문과 국문 문장 설정
        if kor_sentence:
            eng_sentence = translated_sentence
        else:
            kor_sentence = translated_sentence

        # 사다리 문장 생성
        forms_prompt = (
            f"Generate 4 forms for this English sentence: '{eng_sentence}'\n"
            f"1. Declarative\n2. Interrogative\n3. Negative\n4. Negative Interrogative"
        )
        
        with st.spinner("사다리 문장을 생성하는 중입니다..."):
            forms_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": forms_prompt}],
                max_tokens=1000,
                temperature=0.7
            )
        
        # 형식 목록 생성 (번호 제거)
        forms = [form.split(": ", 1)[-1].strip() for form in forms_response.choices[0].message['content'].strip().split("\n") if form]

        # 번호 패턴 제거
        cleaned_forms = []
        for form in forms:
            # 숫자와 마침표가 있는 경우 제거
            cleaned_forms.append(form.split(". ", 1)[-1].strip() if form[0].isdigit() and form[1] == "." else form)

        return eng_sentence, kor_sentence, cleaned_forms
    
    except Exception as e:
        st.error("번역 중 오류가 발생했습니다. 다시 시도해 주세요.")
        return "", "", ["", "", "", ""]

# Streamlit UI
st.title("PSE 사다리 만들기")
st.write("문장을 번역하고, 사다리 연습 문장들을 제공합니다.")

# 사용자 문장 입력
sentences = st.text_area("한 줄에 한 문장씩 입력하세요. (국문 또는 영문, 한 번에 최대 10문장)", height=200).splitlines()
sentences = [sentence.strip() for sentence in sentences if sentence.strip()][:10]

# 사다리 생성
if st.button("사다리 만들기"):
    if not sentences:  # 문장이 입력되지 않았을 때 경고 메시지
        st.warning("최소 한 문장을 입력하세요.")
    else:
        results = []
        for sentence in sentences:
            eng_sentence, kor_sentence, forms = process_sentence(sentence)
            results.append({
                "영문": eng_sentence,
                "국문": kor_sentence,
                "평서문": forms[0] if len(forms) > 0 else "",
                "의문문": forms[1] if len(forms) > 1 else "",
                "부정문": forms[2] if len(forms) > 2 else "",
                "부정의문문": forms[3] if len(forms) > 3 else ""
            })

        # 결과표 출력
        df = pd.DataFrame(results)
        df.index = range(1, len(df) + 1)  # 행번호 1부터 시작

        st.write("### 사다리 연습 문장")
        st.table(df)

        # CSV 다운로드 (UTF-8 with BOM)
        csv = df.to_csv(index=True, encoding="utf-8-sig")
        b = io.BytesIO()
        b.write(csv.encode())
        b.seek(0)
        st.download_button(
            label="결과표 다운로드",
            data=b,
            file_name="translation_results.csv",
            mime="text/csv"
        )
