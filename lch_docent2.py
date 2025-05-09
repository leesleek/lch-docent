### 기본 정보 불러오기

import streamlit as st
from openai import OpenAI
import os
import io
import base64
from PIL import Image

st.set_page_config(page_title="LCH Docent", page_icon=":guardsman:", layout="wide")
st.title("LCH Docent")

### 기능 구현 함수 정리 ###
# GPT-4V
def describe(client, image_url):
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "이 이미지에 대해서 아주 자세히 묘사해줘"},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        max_tokens=1024,
    )
    return response.choices[0].message.content

## TTS
def TTS(client, response_text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=response_text
    )

    filename = "output.mp3"
    response.stream_to_file(filename)

    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true" controls>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

    os.remove(filename)

### 메인 함수 ###
def main():
    st.image('ai.png', width=200)
    st.title("💬 이미지를 해설해드립니다.")

    # ✅ 1. 사용자에게 OpenAI API Key 입력 받기
    api_key_input = st.text_input("🔑 OpenAI API 키를 입력하세요:", type="password")

    if api_key_input:
        client = OpenAI(api_key=api_key_input)

        # ✅ 2. 이미지 업로드
        img_file_buffer = st.file_uploader("이미지 파일을 업로드 해주세요.", type=["jpg", "jpeg", "png"])

        if img_file_buffer is not None:
            image = Image.open(img_file_buffer)
            st.image(image, caption="업로드한 이미지", use_column_width=True)
            st.write("")
            st.write("해설을 생성하는 중입니다...")

            # 이미지 → base64로 변환
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            image_data_url = f"data:image/png;base64,{img_base64}"

            # 설명 텍스트 생성
            description = describe(client, image_data_url)

            # ✅ 3. 설명 출력 및 음성 출력 버튼
            st.subheader("📝 이미지 설명")
            st.info(description)

            if st.button("🔊 음성 출력"):
                TTS(client, description)

if __name__ == "__main__":
    main()
