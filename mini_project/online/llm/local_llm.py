# online/llm/local_llm.py
# Corrections:
# - Removed analyze_web_command since not used (general_chat handles parsing via prompt).
# - Cleaned imports, no sys.path.
# - Added stream=False explicitly.
# - Made chat use generate.

import logging
import httpx
from config import settings

logger = logging.getLogger("JARVIS_LLM")

class LocalLLM:
    def __init__(self):
        self.base_url = settings.LLM_BASE_URL
        self.model = settings.LLM_MODEL
        self.timeout = settings.LLM_TIMEOUT
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def _list_models(self) -> str:
        """List available models from Ollama"""
        try:
            resp = await self.client.get(f"{self.base_url}/api/tags")
            resp.raise_for_status()
            models = resp.json().get("models", [])
            return ", ".join([model.get("name", "unknown") for model in models])
        except Exception:
            return "Unable to fetch model list"

    async def generate(self, prompt: str, max_tokens: int = 500) -> str:
        # Sanitize prompt to avoid broken encoding issues
        prompt = prompt.encode("utf-8", "ignore").decode("utf-8")
        
        payload = {
            "model": self.model, 
            "prompt": prompt, 
            "stream": False, 
            "options": {"num_predict": max_tokens}
        }
        
        logger.debug(f"Sending payload to Ollama: {payload}")
        
        try:
            resp = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            
            if resp.status_code == 500:
                logger.error(f"Ollama returned HTTP 500. Raw response: {resp.text}")
                return "The local AI is currently overloaded or encountered an internal error. Please try again."
                
            resp.raise_for_status()
            return resp.json().get("response", "").strip()
            
        except httpx.TimeoutException as e:
            logger.error(f"LLM Request timed out after {self.timeout}s: {e}")
            return "The AI took too long to respond. Please try a simpler request."
        except httpx.ConnectError:
            logger.error("LLM server not available. Make sure Ollama is running.")
            return "LLM server not available. Make sure Ollama is running."
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.error(f"Model '{self.model}' not found. Available models: {await self._list_models()}")
                return f"Model '{self.model}' not found. Check Ollama installation."
            else:
                logger.error(f"HTTP Error {e.response.status_code}: {e.response.text}")
                return "The AI encountered an HTTP error while generating the response."
        except Exception as e:
            logger.exception("Unexpected LLM Error occurred")
            return "An unexpected error occurred while communicating with the AI."

    async def chat(self, messages: list) -> str:
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages]) + "\nassistant:"
        return await self.generate(prompt)

    async def close(self):
        await self.client.aclose()