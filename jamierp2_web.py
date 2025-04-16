# ✅ jamierp2_web.py – 웹배포용: 녹음 후 업로드 방식
import streamlit as st
from openai import OpenAI
import tempfile
import os
import re
import random
from num2words import num2words
from playsound import playsound

# ✅ 숫자 표현 정리 함수들
def convert_thousands_to_dollar_format(text):
    text = re.sub(r"(\d{2,3})\s*thousand\s*dollars", lambda m: f"${int(m.group(1)) * 1000:,}", text, flags=re.IGNORECASE)
    text = re.sub(r"(\d{1,3}),\s*(\d{3})", r"\1,\2", text)
    return text

def fix_number_spacing(text):
    text = re.sub(r"(\$\d{1,3},\d{3})(?=[a-zA-Z])", r"\1 ", text)
    text = re.sub(r"(\$\d{1,3},\d{3})(?=to)", r"\1 ", text)
    text = re.sub(r"(to)(\$\d{1,3},\d{3})", r"\1 \2", text)
    text = re.sub(r"(\d{1,3},\d{3})(?=[a-zA-Z])", r"\1 ", text)
    text = re.sub(r"(\d{1,3},\d{3})(?=to)", r"\1 ", text)
    text = re.sub(r"(to)(\d{1,3},\d{3})", r"\1 \2", text)
    return text

def ensure_final_period(text):
    return text.strip() + '.' if not text.strip().endswith(('.', '!', '?')) else text

def convert_dollar_amount_to_words(text):
    def replace_match(match):
        number = int(match.group(1).replace(',', ''))
        return num2words(number, to='cardinal', lang='en') + ' dollars'
    return re.sub(r"\$(\d{1,3}(?:,\d{3})*|\d+)", replace_match, text)

# ✅ OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# ✅ 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are Alex Carter, a hotel manager. Ask Jamie questions about work experience, schedule, salary, and benefits one at a time in a job interview."},
        {"role": "assistant", "content": "Hello Jamie, can you tell me about your work history, especially any experience related to front desk or reservations?"}
    ]
    st.session_state.user_turns = []

# ✅ 앱 시작
st.title("🤖 RoleFloBot™ – Web Mic Upload Version")
st.markdown("---")

# ✅ 사용자 .wav 업로드
uploaded_file = st.file_uploader("🎙️ Upload your recorded voice (WAV format)", type=["wav"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(uploaded_file.read())
        temp_path = temp_audio.name

    try:
        # ✅ Whisper STT
        with open(temp_path, "rb") as audio_file:
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en"
            )
        user_text = result.text
        user_text = convert_dollar_amount_to_words(user_text)
        user_text = fix_number_spacing(convert_thousands_to_dollar_format(user_text))
        user_text = ensure_final_period(user_text)

        st.markdown(f"🧑‍💼 You: {user_text}")
        st.session_state.user_turns.append(user_text)
        st.session_state.messages.append({"role": "user", "content": user_text})

        # ✅ GPT 응답
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=st.session_state.messages
        )
        bot_reply = response.choices[0].message.content
        bot_reply = convert_dollar_amount_to_words(bot_reply)
        bot_reply = fix_number_spacing(convert_thousands_to_dollar_format(bot_reply))
        bot_reply = ensure_final_period(bot_reply)
        bot_reply = re.sub(r"[*_]", "", bot_reply)

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        st.markdown(f"🧔‍♂️ Alex (Manager): {bot_reply}")

    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        os.remove(temp_path)

# ✅ 피드백 보기
if st.button("🧑‍🏫 Review My Sentences") and st.session_state.user_turns:
    st.markdown("---")
    st.markdown("### Feedback")
    feedback_samples = random.sample(st.session_state.user_turns, min(3, len(st.session_state.user_turns)))

    for i, sentence in enumerate(feedback_samples):
        revision = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a strict but helpful English teacher. Correct any grammar or fluency issues in this spoken sentence."},
                {"role": "user", "content": f"Evaluate this sentence: {sentence}"}
            ]
        )
        suggestion = revision.choices[0].message.content.strip()
        suggestion = fix_number_spacing(suggestion)
        st.markdown(f"**{i+1}. You said:** {sentence}")
        st.markdown(f"👉 Suggested: {suggestion}")
        st.markdown("---")