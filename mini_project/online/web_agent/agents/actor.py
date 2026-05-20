# online/web_agent/agents/actor.py

from typing import Dict, Any
import logging

from online.llm.local_llm import LocalLLM
from online.web_agent.core.browser import BrowserEngine
from online.web_agent.core.whatsapp_handler import WhatsAppHandler
from online.web_agent.core.observer import WebObserver, PageState

logger = logging.getLogger("JARVIS_Actor")

class ActorAgent:
    def __init__(self, llm: LocalLLM):
        self.llm = llm
        self.browser = BrowserEngine()
        self.whatsapp = WhatsAppHandler(self.browser)
        self.observer = WebObserver()
        self._initialized = False

    async def initialize(self, headless: bool = False) -> Dict[str, Any]:
        if not self._initialized:
            self.browser.initialize(headless)
            self._initialized = True
            self.observer.update_state(PageState.READY)
        return {"status": "success"}

    async def process_action(self, action: dict) -> Dict[str, Any]:
        action_type = action.get("type", "")
        params = action.get("parameters", {})

        # Safety: Re-init if browser died somehow
        if not self.browser.driver or not self.browser.driver.session_id:
            logger.warning("Browser session invalid - reinitializing")
            await self.initialize()

        try:
            result = {"status": "error", "message": "No action matched"}

            if action_type == "open_site":
                url = params.get("url", "")
                result = await self.browser.open_site(url)

            elif action_type == "open_dynamic_site":
                name = params.get("name", "")
                result = await self.browser.open_dynamic_site(name)

            elif action_type == "search":
                query = params.get("query", "")
                engine = params.get("engine", "google")
                result = await self.browser.search(query, engine)

            elif action_type == "play_video":
                query = params.get("query", "")
                url = params.get("url", "")
                result = await self.browser.play_video(query=query, url=url)

            elif action_type == "navigate":
                instruction = params.get("instruction", "")
                result = await self.browser.navigate(instruction)

            elif action_type == "whatsapp_message":
                contact = params.get("contact", "")
                message = params.get("message", "")
                result = await self.whatsapp.send_message(message, contact)

            elif action_type == "whatsapp_contact":
                contact = params.get("contact", "")
                result = await self.whatsapp.search_contact(contact)

            elif action_type == "whatsapp_open":
                # This is the new action type for both web and desktop
                mode = params.get("mode", "web")  # default to web
                result = await self.whatsapp.open_whatsapp(mode)

            elif action_type in ("send_media",):
                result = {"status": "not_implemented", "message": "Media sending not yet implemented"}

            elif action_type == "get_info":
                result = await self.browser.get_info()

            elif action_type == "close":
                await self.close()
                result = {"status": "success", "message": "Browser closed"}

            else:
                result = {"status": "error", "message": f"Unknown action type: {action_type}"}

            success = result.get("status") == "success"
            self.observer.log_interaction(action_type, params, success)
            result["message"] = result.get("message", f"{action_type} completed")
            return result

        except Exception as e:
            logger.error(f"Action {action_type} failed: {e}")
            # Attempt recovery
            try:
                await self.close()
                await self.initialize()
            except:
                pass
            return {"status": "error", "message": f"Web action error (browser restarted): {str(e)}"}

    async def close(self):
        self.browser.close()
        self.observer.update_state(PageState.IDLE)
        self._initialized = False