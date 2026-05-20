import sqlite3
import numpy as np
import sounddevice as sd
import librosa
from speech.tts import speak

DB_PATH = "security/database/users.db"

SAMPLE_RATE = 16000
DURATION = 3
SAMPLES = 5

def capture_admin_voice(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    speak("Voice registration started. Please speak clearly.")
    for i in range(SAMPLES):
        speak(f"Recording voice sample {i + 1}")

        audio = sd.rec(int(DURATION * SAMPLE_RATE),
                        samplerate=SAMPLE_RATE,
                        channels=1,
                        dtype="float32")
        sd.wait()
        audio = audio.flatten()
        
        # Preprocessing: trim silence and normalize
        trimmed_audio, _ = librosa.effects.trim(audio, top_db=30)
        
        # If trimming removed everything (total silence), fallback to original
        if len(trimmed_audio) < SAMPLE_RATE * 0.5:
            print("[DEBUG] Audio too silent, using raw audio.")
            trimmed_audio = audio
            
        normalized_audio = librosa.util.normalize(trimmed_audio)
        
        print(f"[DEBUG] Registration Sample {i+1}: Original length={len(audio)}, Trimmed length={len(normalized_audio)}")
        
        mfcc = librosa.feature.mfcc(y=normalized_audio, sr=SAMPLE_RATE, n_mfcc=13)
        mfcc_mean = np.mean(mfcc.T, axis=0).astype(np.float32)
        cur.execute(
            "INSERT INTO voice_data (user_id, features) VALUES (?, ?)",
            (user_id, mfcc_mean.tobytes())
        )
    conn.commit()
    conn.close()
    speak("Voice registration completed successfully.")