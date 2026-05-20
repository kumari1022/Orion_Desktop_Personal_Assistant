import cv2
import sqlite3
import numpy as np
from speech.tts import speak

DB_PATH = "security/database/users.db"
MODEL_PATH = "models/face_model.yml"

def train_face_from_db(user_id):
    speak("Training face recognition model. Please wait.")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT image FROM face_data WHERE user_id=?", (user_id,))
    rows = cur.fetchall()
    conn.close()

    if len(rows) < 10:
        speak("Insufficient face data. Please register again.")
        return False

    faces, labels = [], []

    for row in rows:
        img_array = np.frombuffer(row[0], dtype=np.uint8)
        gray = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
        gray = cv2.resize(gray, (200, 200))

        faces.append(gray)
        labels.append(user_id)

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(labels))
    recognizer.save(MODEL_PATH)

    speak("Face recognition model trained and secured.")
    return True