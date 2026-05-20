import os
import subprocess
import logging

logger = logging.getLogger("JARVIS_Offline")

class AppOpener:
    @staticmethod
    def _normalize_command(app_name: str) -> str:
        # Sanitize common filler words
        app_name = app_name.lower().strip()
        fillers = ["open ", "start ", "launch ", "run ", "the ", "app ", "application ", "browser "]
        for filler in fillers:
            app_name = app_name.replace(filler, "")
            
        app_name = app_name.strip()
            
        # Map common misinterpretations or variations
        corrections = {
            "note pad": "notepad",
            "word pad": "wordpad",
            "chrome browser": "chrome",
            "google chrome": "chrome",
            "vs code": "code",
            "visual studio code": "code",
            "ms word": "word",
            "microsoft word": "word",
            "ms excel": "excel",
            "microsoft excel": "excel",
            "ms powerpoint": "powerpoint",
            "microsoft powerpoint": "powerpoint",
            "command prompt": "cmd",
            "task manager": "taskmgr",
            "control panel": "control",
        }
        
        return corrections.get(app_name, app_name)

    @staticmethod
    def open_app(app_name: str) -> str:
        app_name = AppOpener._normalize_command(app_name)
        
        # Common Windows apps with direct system aliases
        common_apps = {
            "notepad": "notepad",
            "calculator": "calc",
            "calc": "calc",
            "chrome": "chrome",
            "firefox": "firefox",
            "code": "code",
            "vscode": "code",
            "word": "winword",
            "excel": "excel",
            "powerpoint": "powerpnt",
            "paint": "mspaint",
            "cmd": "cmd",
            "taskmgr": "taskmgr",
            "task manager": "taskmgr",
            "settings": "ms-settings:",
            "control": "control"
        }
        
        # Prevent completely empty commands
        if not app_name:
            return "Could not understand which app to open."
            
        try:
            if app_name in common_apps:
                target = common_apps[app_name]
                # In Windows, 'start "" "target"' works well for items in PATH
                subprocess.Popen(f'start "" "{target}"', shell=True)
                return f"Opened {app_name.title()}"
            else:
                # Basic validation: ensure it doesn't contain dangerous operators
                if any(char in app_name for char in ["&", "|", ">", "<", ";"]):
                    logger.warning(f"Prevented potentially dangerous app name execution: {app_name}")
                    return "Invalid application name."
                    
                # Try generic open (for any installed app or command)
                subprocess.Popen(f'start "" "{app_name}"', shell=True)
                return f"Opened {app_name.title()}"
        except Exception as e:
            logger.error(f"App opener failed: {e}")
            return f"Could not open {app_name}. Error: {e}"