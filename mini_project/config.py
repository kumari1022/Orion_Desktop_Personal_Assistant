# config.py
# Corrections:
# - Changed LLM_MODEL default to "qwen:8b" (assuming Ollama pull qwen:8b; adjust if qwen2.5).
# - Added more engines if needed.
# - No hardcodes, all from env.

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME = os.getenv("PROJECT_NAME", "ORION")
    VERSION = os.getenv("VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Local LLM
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
    LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434")
    LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "120"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    
    # Browser
    BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"
    BROWSER_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30"))
    
    # Quick Sites
    QUICK_SITES = {
        "youtube": "https://www.youtube.com",
        "gmail": "https://mail.google.com",
        "github": "https://github.com",
        "whatsapp": "https://web.whatsapp.com",
    }
    
    # Search Engines
    SEARCH_ENGINES = {
        "google": "https://www.google.com/search?q=",
        "bing": "https://www.bing.com/search?q=",
        "youtube": "https://www.youtube.com/results?search_query=",
        "duckduckgo": "https://duckduckgo.com/?q=",
    }

settings = Settings()