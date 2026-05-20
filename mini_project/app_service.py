import os
import asyncio
import sqlite3
from typing import Optional
import pythoncom

from security.database.db_manager import init_db
from security.face.capture_face import capture_admin_face
from security.face.train_face import train_face_from_db
from security.face.recognize_face import authenticate_admin_face
from security.voice.capture_voice import capture_admin_voice
from security.voice.recognize_voice import authenticate_admin_voice
from core.command_router import route_command
from online.web_agent.runner import WebAgentRunner
from speech.tts import speak

DB_PATH = "security/database/users.db"
FACE_MODEL_PATH = "models/face_model.yml"


class OrionService:
    def __init__(self):
        self.web_runner = WebAgentRunner()
        self.initialized = False
    def _run_with_com(self, func, *args, **kwargs):
        pythoncom.CoInitialize()
        try:
            return func(*args, **kwargs)
        finally:
            pythoncom.CoUninitialize()

    def get_admin(self) -> Optional[int]:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE role='admin'")
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None

    async def startup(self):
        if self.initialized:
            return
        init_db()
        os.makedirs("models", exist_ok=True)
        await self.web_runner.start()
        self.initialized = True

    async def shutdown(self):
        if self.initialized:
            await self.web_runner.stop()
            self.initialized = False

    async def verify_face(self) -> dict:
        try:
            os.makedirs("models", exist_ok=True)

            admin_id = self.get_admin()
            if admin_id is None:
                return {
                    "success": False,
                    "status": "No admin found in database"
                }

            if not os.path.exists(FACE_MODEL_PATH):
                await asyncio.to_thread(self._run_with_com, capture_admin_face, admin_id)

                trained = await asyncio.to_thread(self._run_with_com, train_face_from_db, admin_id)
                if not trained:
                    return {
                        "success": False,
                        "status": "Face registration failed. Not enough face data collected."
                    }

            ok = await asyncio.to_thread(self._run_with_com, authenticate_admin_face)
            status = "Face authentication successful" if ok else "Face authentication failed"

            return {
                "success": ok,
                "status": status
            }

        except Exception as e:
            return {
                "success": False,
                "status": f"Face auth error: {str(e)}"
            }

    async def verify_voice(self) -> dict:
        try:
            admin_id = self.get_admin()
            if admin_id is None:
                return {"success": False, "status": "No admin found in database"}

            ok = await asyncio.to_thread(self._run_with_com, authenticate_admin_voice, admin_id)
            status = "Voice authentication successful" if ok else "Voice authentication failed"

            return {
                "success": ok,
                "status": status
            }
        except Exception as e:
            return {"success": False, "status": f"Voice auth error: {str(e)}"}

    async def listen_once(self) -> dict:
        try:
            from speech.listener import take_command
            text = await asyncio.to_thread(take_command)

            if not text:
                await asyncio.to_thread(speak, "No voice command detected")
                return {"success": True, "status": ""}

            if text == "__LOW_CONFIDENCE__":
                await asyncio.to_thread(speak, "I didn't catch that clearly. Please repeat.")
                return {"success": True, "status": ""}

            return {"success": True, "status": text}
        except FileNotFoundError as e:
            return {"success": False, "status": f"Voice listen error: missing dependency or file: {str(e)}"}
        except Exception as e:
            return {"success": False, "status": f"Voice listen error: {str(e)}"}

    async def run_command(self, command: str) -> dict:
        try:
            result = await route_command(command)

            if result == "EXIT":
                await asyncio.to_thread(speak, "System shutdown requested")
                return {"success": True, "response": "System shutdown requested"}

            final_response = result or "No response"
            await asyncio.to_thread(speak, final_response)

            return {"success": True, "response": final_response}
        except Exception as e:
            return {"success": False, "response": f"Command failed: {str(e)}"}