import cv2
import os
from speech.tts import speak

MODEL_PATH = "models/face_model.yml"
THRESHOLD = 60
REQUIRED_MATCHES = 5
ADMIN_ID = 1

def authenticate_admin_face():
    if not os.path.exists(MODEL_PATH):
        speak("Face model not found. Please register admin first.")
        return False
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(MODEL_PATH)

    detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    cam = cv2.VideoCapture(0)
    success_count = 0
    speak("Please look at the camera for face authentication.")
    try:
        while True:
            ret, frame = cam.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            if len(faces) > 1:
                speak("Only one person should be in front of the camera.")
                continue
            for (x, y, w, h) in faces:
                face = gray[y:y+h, x:x+w]
                face = cv2.resize(face, (200, 200))
                label, confidence = recognizer.predict(face)
                if label == ADMIN_ID and confidence < THRESHOLD:
                    success_count += 1
                    cv2.putText(frame, "Verifying...", (x, y-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
                else:
                    success_count = 0
                    cv2.putText(frame, "Unknown", (x, y-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)
                cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)
            cv2.imshow("Face Authentication", frame)
            if success_count >= REQUIRED_MATCHES or cv2.waitKey(1) == 27:
                break
    finally:
        cam.release()
        cv2.destroyAllWindows()
    if success_count >= REQUIRED_MATCHES:
        speak("Face authentication successful. Welcome admin.")
        return True
    else:
        speak("Face authentication failed. Access denied.")
        return False