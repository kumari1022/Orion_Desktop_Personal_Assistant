#!/usr/bin/env python3
"""
Admin Registration Script
This script helps you register your face and voice for the JARVIS system
"""

import sqlite3
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from security.database.db_manager import init_db
from security.face.capture_face import capture_admin_face
from security.face.train_face import train_face_from_db
from security.voice.capture_voice import capture_admin_voice
from speech.tts import speak

DB_PATH = "security/database/users.db"

def check_admin_exists():
    """Check if admin already exists"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE role='admin'")
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def create_admin():
    """Create admin user"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, role) VALUES (?, ?)", ("admin", "admin"))
    admin_id = cur.lastrowid
    conn.commit()
    conn.close()
    return admin_id

def main():
    print("=== JARVIS Admin Registration ===")
    
    # Initialize database
    print("Initializing database...")
    init_db()
    
    # Check if admin exists
    existing_admin = check_admin_exists()
    if existing_admin:
        print(f"Admin already exists with ID: {existing_admin}")
        choice = input("Do you want to re-register? (y/n): ").lower()
        if choice != 'y':
            print("Registration cancelled.")
            return
        admin_id = existing_admin
    else:
        print("Creating new admin account...")
        admin_id = create_admin()
        print(f"Admin created with ID: {admin_id}")
    
    print("\n=== FACE REGISTRATION ===")
    print("1. Make sure you're in a well-lit area")
    print("2. Position your face clearly in front of the camera")
    print("3. Only one face should be visible")
    print("4. The system will capture 30 face samples")
    print("5. Press ESC to stop early if needed")
    
    input("\nPress Enter to start face registration...")
    
    try:
        capture_admin_face(admin_id, samples=30)
        print("✅ Face registration completed!")
        
        # Train the face recognition model
        print("\nTraining face recognition model...")
        train_face_from_db(admin_id)
        print("✅ Face training completed!")
        
    except Exception as e:
        print(f"❌ Face registration failed: {e}")
        return
    
    print("\n=== VOICE REGISTRATION ===")
    print("1. Find a quiet environment")
    print("2. Speak clearly when prompted")
    print("3. The system will record 5 voice samples (3 seconds each)")
    
    input("\nPress Enter to start voice registration...")
    
    try:
        capture_admin_voice(admin_id)
        print("✅ Voice registration completed!")
        
    except Exception as e:
        print(f"❌ Voice registration failed: {e}")
        return
    
    print("\n🎉 REGISTRATION COMPLETED SUCCESSFULLY!")
    print("You can now run the main.py file and your face/voice will be authenticated.")
    print("\nTo run the main system:")
    print("python main.py")

if __name__ == "__main__":
    main()
