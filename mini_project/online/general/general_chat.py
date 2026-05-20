# online/general/general_chat.py
# Corrections:
# - Made fully async (removed asyncio.run, assume caller handles async).
# - Added local quick checks for time/date inside process (redundant with router but safe).
# - Cleaned imports, no need for sys.path if structure is correct.
# - Stripped response better.

import asyncio
from datetime import datetime
from online.llm.local_llm import LocalLLM
from online.llm.prompt_builder import PromptBuilder

class GeneralChat:
    def __init__(self, llm: LocalLLM = None):
        self.llm = llm or LocalLLM()
        self.prompt_builder = PromptBuilder()

    async def process(self, user_input: str) -> dict:
        user_input_lower = user_input.strip().lower()
        
        # Quick local handles
        if "time" in user_input_lower:
            return {"type": "general", "response": datetime.now().strftime("%I:%M %p")}
        elif "date" in user_input_lower:
            return {"type": "general", "response": datetime.now().strftime("%A, %B %d, %Y")}
        
        prompt = self.prompt_builder.build_web_command_prompt(user_input)
        response = await self.llm.generate(prompt, max_tokens=300)
        
        response = response.strip()
        
        if response.startswith("GENERAL:"):
            return {
                "type": "general",
                "response": response.replace("GENERAL:", "").strip()
            }
        
        elif response.startswith("WEB_TASK:"):
            task_part = response.replace("WEB_TASK:", "").strip()
            parts = task_part.split("|")
            
            task_type = parts[0].strip()
            params = {}
            
            for part in parts[1:]:
                if "=" in part:
                    key, value = part.split("=", 1)
                    params[key.strip()] = value.strip()
            
            return {
                "type": "web_task",
                "action": {
                    "type": task_type,
                    "parameters": params
                }
            }
        
        return {"type": "general", "response": response}