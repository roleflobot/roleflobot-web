import pyttsx3

engine = pyttsx3.init()
engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0')
engine.say("Hello, Jamie. Thank you for coming to the interview.")
engine.runAndWait()
