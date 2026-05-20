#!/usr/bin/env python3
"""
Voice Re-registration Script
This script allows you to re-record voice samples for the admin user,
using the updated preprocessing pipeline (normalization & trimming).
"""

import sqlite3
import sys
import os
import numpy as np
import sounddevice as sd
import librosa

# Add project root to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from speech.tts import speak

DB_PATH = "security/database/users.db"
SAMPLE_RATE = 16000
DURATION = 3
SAMPLES = 5

def get_admin_id():
    """Find the current admin user in the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE role='admin'")
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"[ERROR] Database error while finding admin: {e}")
        return None

def clear_old_voice_data(user_id):
    """Delete all old voice embeddings related to the admin."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("DELETE FROM voice_data WHERE user_id=?", (user_id,))
        deleted_count = cur.rowcount
        conn.commit()
        conn.close()
        print(f"[DEBUG] Cleared {deleted_count} old voice samples from database.")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to delete old voice data: {e}")
        return False

def re_register_voice():
    print("=== JARVIS Admin Voice Re-Registration ===")
    
    admin_id = get_admin_id()
    if not admin_id:
        print("[ERROR] No admin user found in database. Please run register_admin.py first.")
        return
        
    print(f"[DEBUG] Admin found with ID: {admin_id}")
    
    # Clear old data
    if not clear_old_voice_data(admin_id):
        return

    print("\nStarting fresh voice registration...")
    speak("Voice registration started. Please speak clearly.")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        for i in range(SAMPLES):
            print(f"\n--- Recording Sample {i + 1}/{SAMPLES} ---")
            speak(f"Recording voice sample {i + 1}")
            
            print(f"[DEBUG] Recording started for {DURATION} seconds at {SAMPLE_RATE} Hz...")
            
            try:
                audio = sd.rec(int(DURATION * SAMPLE_RATE),
                                samplerate=SAMPLE_RATE,
                                channels=1,
                                dtype="float32")
                sd.wait()
            except Exception as e:
                print(f"[ERROR] Microphone access failed: {e}")
                speak("Microphone access failed. Registration aborted.")
                conn.close()
                return
                
            audio = audio.flatten()
            
            # Check for empty or purely silent (zeros) recording
            if np.all(audio == 0) or len(audio) == 0:
                print("[ERROR] Empty or silent recording detected. Please check your microphone.")
                continue
                
            # Preprocessing: trim silence and normalize
            trimmed_audio, _ = librosa.effects.trim(audio, top_db=30)
            
            # Fallback handling
            if len(trimmed_audio) < SAMPLE_RATE * 0.5:
                print("[DEBUG] Trimmed audio too silent or short, using raw original audio.")
                trimmed_audio = audio
                
            normalized_audio = librosa.util.normalize(trimmed_audio)
            
            print(f"[DEBUG] Preprocessing applied: Trimmed silence (top_db=30), Normalized audio.")
            print(f"[DEBUG] Audio original length: {len(audio)} samples")
            print(f"[DEBUG] Audio trimmed length: {len(normalized_audio)} samples")
            
            mfcc = librosa.feature.mfcc(y=normalized_audio, sr=SAMPLE_RATE, n_mfcc=13)
            mfcc_mean = np.mean(mfcc.T, axis=0).astype(np.float32)
            
            print(f"[DEBUG] MFCC Embedding shape: {mfcc_mean.shape}")
            
            try:
                cur.execute(
                    "INSERT INTO voice_data (user_id, features) VALUES (?, ?)",
                    (admin_id, mfcc_mean.tobytes())
                )
                print(f"[DEBUG] Database save success for sample {i+1}")
            except Exception as e:
                print(f"[ERROR] Database save failed for sample {i+1}: {e}")
                
        conn.commit()
        conn.close()
        
        print("\n✅ Voice registration completed successfully!")
        speak("Voice registration completed successfully.")
        
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        speak("An unexpected error occurred during voice registration.")

if __name__ == "__main__":
    re_register_voice()
