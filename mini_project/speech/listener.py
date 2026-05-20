import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile
import librosa
import os
import logging

logger = logging.getLogger("JARVIS_Listener")

# Load model globally to avoid loading delay every time
model = whisper.load_model("small")

def take_command():
    print("🎤 Listening...")

    duration = 4
    fs = 16000
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="float32")
    sd.wait()
    
    audio = recording.flatten()
    
    # Preprocessing to reduce background noise sensitivity
    # 1. Trim silence from ends
    trimmed_audio, _ = librosa.effects.trim(audio, top_db=30)
    
    # Fallback to original if completely silent
    if len(trimmed_audio) < fs * 0.5:
        trimmed_audio = audio
        
    # 2. Normalize audio volume
    normalized_audio = librosa.util.normalize(trimmed_audio)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_filename = f.name
        
    try:
        wav.write(temp_filename, fs, normalized_audio)
        
        # Optimize inference and force English
        result = model.transcribe(
            temp_filename, 
            language="en", 
            fp16=False, 
            condition_on_previous_text=False
        )
        
        segments = result.get("segments", [])
        raw_text = result.get("text", "").strip().lower()
        
        if not raw_text:
            return ""
            
        valid_segments = []
        for seg in segments:
            no_speech = seg.get("no_speech_prob", 0.0)
            avg_log = seg.get("avg_logprob", 0.0)
            seg_text = seg.get("text", "").strip()
            
            print(f"[DEBUG] Segment: '{seg_text}' | avg_logprob: {avg_log:.3f} | no_speech_prob: {no_speech:.3f}")
            
            # Strict filtering to suppress quiet sounds, mic pops, or random hallucinations
            if no_speech > 0.60:
                print(f"[DEBUG] Rejected segment '{seg_text}' due to high no_speech_prob.")
                continue
            if avg_log < -1.15:
                print(f"[DEBUG] Rejected segment '{seg_text}' due to low confidence logprob.")
                continue
                
            valid_segments.append(seg_text)
            
        if not valid_segments:
            print("[DEBUG] All segments rejected as background noise / voice hallucination.")
            return "__LOW_CONFIDENCE__"
            
        filtered_text = " ".join(valid_segments).strip().lower()
        print("📝 Command:", filtered_text)
        print(f"[DEBUG] Whisper Language Forced: en")
        return filtered_text
    finally:
        # Cleanup temp file
        if os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
            except Exception as e:
                logger.error(f"Failed to remove temp file {temp_filename}: {e}")
