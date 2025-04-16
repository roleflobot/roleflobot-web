import speech_recognition as sr

recognizer = sr.Recognizer()
with sr.Microphone() as source:
    print("말씀하세요 🎤:")
    audio = recognizer.listen(source)

try:
    text = recognizer.recognize_google(audio)
    print("인식된 음성:", text)
except sr.UnknownValueError:
    print("음성을 이해할 수 없습니다.")
except sr.RequestError as e:
    print("API 요청 에러:", e)
