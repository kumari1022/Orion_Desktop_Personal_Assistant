import os
import logging
from online.llm.local_llm import LocalLLM

logger = logging.getLogger("JARVIS_Offline")

class FileManager:
    def __init__(self):
        self.llm = LocalLLM()

    def create_folder(self, folder_name: str, location: str = "desktop") -> str:
        try:
            base_path = self._get_base_path(location)
            full_path = os.path.join(base_path, folder_name)
            os.makedirs(full_path, exist_ok=True)
            return f"Created folder '{folder_name}' at {full_path}"
        except Exception as e:
            return f"Failed to create folder: {str(e)}"

    def create_file(self, file_name: str, location: str = "desktop", content: str = "") -> str:
        try:
            base_path = self._get_base_path(location)
            full_path = os.path.join(base_path, file_name)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Created file '{file_name}' at {full_path}"
        except Exception as e:
            return f"Failed to create file: {str(e)}"

    def _get_base_path(self, location: str) -> str:
        location = location.lower()
        if "desktop" in location:
            return os.path.join(os.path.expanduser("~"), "Desktop")
        elif "documents" in location:
            return os.path.join(os.path.expanduser("~"), "Documents")
        elif "d:" in location or "d drive" in location:
            return "D:\\"
        elif "e:" in location or "e drive" in location:
            return "E:\\"
        else:
            return os.path.expanduser("~")  # default to user home

    async def write_code_to_file(self, description: str, file_name: str, location: str = "desktop") -> str:
        try:
            # Generate code using local LLM
            prompt = f"Write a complete {description}. Only give the code, no explanation."
            code = await self.llm.generate(prompt, max_tokens=800)
            
            # Clean code (remove markdown if present)
            if "```c" in code:
                code = code.split("```c")[1].split("```")[0]
            elif "```" in code:
                code = code.split("```")[1]
            
            return self.create_file(file_name, location, code.strip())
        except Exception as e:
            return f"Failed to generate/write code: {str(e)}"