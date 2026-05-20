# main.py
# Final version with Phase 3 (Offline) integration support

import sqlite3
import sys
import asyncio

# ---------------- SECURITY IMPORTS (UNCHANGED - Phase 1) ----------------
from security.database.db_manager import init_db
from speech.tts import speak
from security.face.capture_face import capture_admin_face
from security.face.train_face import train_face_from_db
from security.face.recognize_face import authenticate_admin_face
from security.voice.capture_voice import capture_admin_voice
from security.voice.recognize_voice import authenticate_admin_voice

# ---------------- SPEECH & ROUTING ----------------
from speech.listener import take_command
from core.command_router import route_command

# ---------------- ONLINE PHASE (Phase 2) ----------------
from online.web_agent.runner import WebAgentRunner

# ---------------- OFFLINE PHASE (Phase 3) ----------------
# Import OfflineHandler (optional - mostly handled in command_router)
try:
    from offline.offline_handler import OfflineHandler
    offline_handler = OfflineHandler()
except ImportError:
    offline_handler = None  # If folder/files not created yet
    print("Offline phase not loaded yet - create offline/ folder if needed.")

# ---------------- GLOBAL INSTANCES ----------------
DB_PATH = "security/database/users.db"
web_runner = WebAgentRunner()

# ==========================================================
# DATABASE HELPERS (UNCHANGED)
# ==========================================================

def get_admin():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE role='admin'")
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def create_admin():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    speak("No admin found. Initializing administrator setup.")
    cur.execute("INSERT INTO users (name, role) VALUES (?, ?)", ("admin", "admin"))
    admin_id = cur.lastrowid
    conn.commit()
    conn.close()

    # 🔐 SECURITY SETUP (UNCHANGED)
    capture_admin_face(admin_id)
    train_face_from_db(admin_id)
    capture_admin_voice(admin_id)

    speak("Administrator setup completed successfully.")
    return admin_id


# ==========================================================
# COMMAND LOOP
# ==========================================================

async def command_loop():
    speak("System is now listening. Online and offline modes active.")

    # Start web agent (Phase 2)
    await web_runner.start()

    # Optional: Initialize offline handler if available
    if offline_handler:
        print("Offline handler ready (app opening, file creation, code writing).")

    while True:
        command = take_command()

        if not command:
            continue

        if command == "__LOW_CONFIDENCE__":
            speak("I didn't catch that clearly. Please repeat.")
            continue

        print("COMMAND:", command)

        # Route the command (handles offline, web, general, time/date, exit)
        result = await route_command(command)

        if result == "EXIT":
            speak("System shutting down")
            await web_runner.stop()
            # Optional: any offline cleanup if needed
            sys.exit(0)

        if result:
            print("JARVIS:", result)
            speak(result)


# ==========================================================
# MAIN SYSTEM BOOT (SECURITY UNCHANGED)
# ==========================================================

def main():
    speak("System booting.")
    init_db()

    admin_id = get_admin()
    if admin_id is None:
        admin_id = create_admin()

    speak("Starting security verification.")

    # 🔐 FACE AUTHENTICATION (UNCHANGED)
    if not authenticate_admin_face():
        speak("Face authentication failed. System locked.")
        return

    """
    if not authenticate_admin_voice(admin_id):
        speak("Voice authentication failed. System locked.")
        return
    """

    speak("Authentication successful. System unlocked.")
    print("SYSTEM UNLOCKED")

    asyncio.run(command_loop())


if __name__ == "__main__":
    main()