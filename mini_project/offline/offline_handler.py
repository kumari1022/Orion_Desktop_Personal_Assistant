from .app_opener import AppOpener
from .file_manager import FileManager
from .system_settings import SystemSettings
import logging 
logger = logging.getLogger("orion_Offline")
class OfflineHandler:
    def __init__(self):
        self.app_opener = AppOpener()
        self.file_manager = FileManager()

    async def process(self, command: str) -> str:
        cmd = command.lower().strip()

        # 1. Open App
        if cmd.startswith("open ") or cmd.startswith("launch ") or cmd.startswith("start "):
            app_name = cmd.split(" ", 1)[1].strip()
            return self.app_opener.open_app(app_name)

        # 2. Create Folder (more flexible matching)
        if any(kw in cmd for kw in ["create folder", "make folder", "new folder"]):
            # Example: create folder projects in d drive
            parts = cmd.split("folder")[-1].strip().split(" in ")
            folder_name = parts[0].strip()
            location = parts[1].strip() if len(parts) > 1 else "desktop"
            return self.file_manager.create_folder(folder_name, location)

        # 3. Create File (catch "create filename" or "create file filename")
        if any(kw in cmd for kw in ["create file", "make file", "new file", "create "]) and "." in cmd:
            # Extract filename and location
            # Simple parsing: look for last "in"/"on" as location
            if " in " in cmd or " on " in cmd:
                splitter = " in " if " in " in cmd else " on "
                parts = cmd.split(splitter)
                file_part = parts[0].replace("create file", "").replace("make file", "").replace("new file", "").replace("create ", "").strip()
                location = parts[1].strip()
            else:
                file_part = cmd.replace("create file", "").replace("make file", "").replace("new file", "").replace("create ", "").strip()
                location = "desktop"

            # Assume last word is filename if no extension specified
            if " " in file_part:
                file_name = file_part.split()[-1]
            else:
                file_name = file_part

            if not "." in file_name:
                file_name += ".txt"  # default extension

            return self.file_manager.create_file(file_name, location)

        # 4. Write Code to File (most powerful)
            # 4. Write Code to File – very flexible for natural speech
        if "write" in cmd and ("program" in cmd or "code" in cmd or "java" in cmd or "python" in cmd or "c " in cmd or "c++" in cmd):
            try:
                # Default values
                file_name = "program.java"  # fallback
                location = "desktop"
                description = cmd.replace("write", "").strip()

                # Try to extract filename if present (e.g. "in java.java", "in code.java")
                if " in " in cmd or " on " in cmd:
                    splitter = " in " if " in " in cmd else " on "
                    parts = cmd.split(splitter, 1)
                    description = parts[0].replace("write", "").strip()
                    file_location = parts[1].strip()

                    # Filename is often the last word with .java/.c/etc.
                    words = file_location.split()
                    for word in reversed(words):
                        if "." in word and any(ext in word for ext in [".java", ".c", ".cpp", ".py", ".txt"]):
                            file_name = word
                            location = " ".join(words[:words.index(word)]).strip() or "desktop"
                            break
                    else:
                        location = file_location or "desktop"

                # If no filename found, guess from language
                if file_name == "program.java":
                    if "java" in description.lower():
                        file_name = "java.java"
                    elif "c program" in description.lower():
                        file_name = "program.c"
                    elif "python" in description.lower():
                        file_name = "program.py"
                    else:
                        file_name = "program.txt"

                # Generate code using LLM
                return await self.file_manager.write_code_to_file(description, file_name, location)
        
            except Exception as parse_err:
                logger.error(f"Code write parse error: {parse_err}")
                return "Sorry, couldn't understand the code writing request. Try: 'write a C addition program in file add.c on desktop'"
            # 5. System Settings (volume, bluetooth, wifi, hotspot, restart, sleep, shutdown)
        if any(kw in cmd for kw in ["sound ", "volume ", "bluetooth ", "wifi ", "hotspot ", "restart", "sleep", "shutdown"]):
            settings_handler = SystemSettings()

            if "sound up" in cmd or "volume up" in cmd:
                amount = 10
                if any(word.isdigit() for word in cmd.split()):
                    amount = int(''.join(filter(str.isdigit, cmd))) or 10
                return settings_handler.volume_up(amount)

            elif "sound down" in cmd or "volume down" in cmd:
                amount = 10
                if any(word.isdigit() for word in cmd.split()):
                    amount = int(''.join(filter(str.isdigit, cmd))) or 10
                return settings_handler.volume_down(amount)

            elif "bluetooth" in cmd:
                state = "on" if any(w in cmd for w in ["on", "enable", "turn on"]) else "off"
                return settings_handler.bluetooth(state)

            elif "wifi" in cmd:
                state = "on" if any(w in cmd for w in ["on", "enable", "turn on"]) else "off"
                return settings_handler.wifi(state)

            elif "hotspot" in cmd:
                state = "on" if any(w in cmd for w in ["on", "start", "enable"]) else "off"
                return settings_handler.hotspot(state)

            elif "restart" in cmd:
                return settings_handler.restart()

            elif "sleep" in cmd:
                return settings_handler.sleep()

            elif "shutdown" in cmd:
                return settings_handler.shutdown()

        return "Offline command not recognized. Try: 'open notepad', 'create folder xyz on desktop', 'create file test.txt in documents', or 'write a C program in file code.c'"