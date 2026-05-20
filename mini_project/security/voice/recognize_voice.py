import sqlite3
import numpy as np
import sounddevice as sd
import librosa
from speech.tts import speak

DB_PATH = "security/database/users.db"

SAMPLE_RATE = 16000
DURATION = 3
THRESHOLD = 55.0  # legacy threshold, keep if needed by other files
EUCLIDEAN_THRESHOLD = 60.0  # Tuned for normalized MFCCs (lower = stricter)
COSINE_THRESHOLD = 0.85     # Cosine similarity threshold (higher = stricter)

def authenticate_admin_voice(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT features FROM voice_data WHERE user_id=?", (user_id,))
        rows = cur.fetchall()
        conn.close()
        
        if not rows:
            speak("No voice data found. Skipping voice authentication.")
            return True
            
        stored_vectors = [
            np.frombuffer(row[0], dtype=np.float32) for row in rows
        ]
        stored_mean = np.mean(stored_vectors, axis=0)
        
        speak("Please speak for voice authentication.")
        print(f"[DEBUG] Recording audio for {DURATION} seconds at {SAMPLE_RATE} Hz")
        audio = sd.rec(int(DURATION * SAMPLE_RATE),
                        samplerate=SAMPLE_RATE,
                        channels=1,
                        dtype="float32")
        sd.wait()
        audio = audio.flatten()
        
        # Preprocessing: trim silence and normalize
        trimmed_audio, _ = librosa.effects.trim(audio, top_db=30)
        
        # Fallback handling
        if len(trimmed_audio) < SAMPLE_RATE * 0.5:
            print("[DEBUG] Trimmed audio too silent or short, using raw original audio.")
            trimmed_audio = audio
            
        normalized_audio = librosa.util.normalize(trimmed_audio)
        
        print(f"[DEBUG] Audio original length: {len(audio)} samples")
        print(f"[DEBUG] Audio trimmed length: {len(normalized_audio)} samples")
        print(f"[DEBUG] Sample rate: {SAMPLE_RATE} Hz")
        
        mfcc = librosa.feature.mfcc(y=normalized_audio, sr=SAMPLE_RATE, n_mfcc=13)
        print(f"[DEBUG] MFCC feature shape: {mfcc.shape}")
        
        input_vector = np.mean(mfcc.T, axis=0).astype(np.float32)
        
        # Euclidean similarity score
        euclidean_distance = np.linalg.norm(input_vector - stored_mean)
        
        # Cosine similarity score
        cos_sim = np.dot(input_vector, stored_mean) / (np.linalg.norm(input_vector) * np.linalg.norm(stored_mean))
        
        print(f"[DEBUG] Euclidean Distance: {euclidean_distance:.2f} (Threshold: <= {EUCLIDEAN_THRESHOLD})")
        print(f"[DEBUG] Cosine Similarity: {cos_sim:.2f} (Threshold: >= {COSINE_THRESHOLD})")
        
        # Combined threshold logic (more tolerant)
        is_authenticated = False
        if euclidean_distance < EUCLIDEAN_THRESHOLD or cos_sim > COSINE_THRESHOLD:
            is_authenticated = True
            
        print(f"[DEBUG] Final Authentication Decision: {'SUCCESS' if is_authenticated else 'FAILED'}")
        
        if is_authenticated:
            speak("Voice authentication successful.")
            return True
        else:
            speak("Voice authentication failed.")
            return False
            
    except Exception as e:
        print(f"[ERROR] Voice authentication encountered an error: {e}")
        speak("An error occurred during voice authentication.")
        return False