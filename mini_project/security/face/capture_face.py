import cv2
import sqlite3
from speech.tts import speak

DB_PATH = "security/database/users.db"

def capture_admin_face(user_id, samples=30):
    cam = cv2.VideoCapture(0)
    detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    count = 0
    speak("Face registration started. Please look at the camera.")
    try:
        while True:
            ret, frame = cam.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)

            if len(faces) > 1:
                speak("Only one face should be visible.")
                continue
            for (x, y, w, h) in faces:
                face_img = gray[y:y+h, x:x+w]
                face_img = cv2.resize(face_img, (200, 200))

                _, buffer = cv2.imencode(".jpg", face_img)
                cur.execute(
                    "INSERT INTO face_data (user_id, image) VALUES (?, ?)",
                    (user_id, buffer.tobytes())
                )

                count += 1
                cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

            cv2.imshow("Admin Face Registration", frame)

            if count >= samples or cv2.waitKey(1) == 27:
                break
    finally:
        conn.commit()
        conn.close()
        cam.release()
        cv2.destroyAllWindows()

    speak("Admin face registration completed successfully.")