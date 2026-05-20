import pyttsx3
import pythoncom
import threading

_tts_lock = threading.Lock()

def speak(text):
    with _tts_lock:
        pythoncom.CoInitialize()
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 150)
            engine.setProperty("volume", 1.0)
            engine.say(str(text))
            try:
                engine.runAndWait()
            except RuntimeError as e:
                if "run loop already started" not in str(e):
                    raise
            engine.stop()
        finally:
            pythoncom.CoUninitialize()