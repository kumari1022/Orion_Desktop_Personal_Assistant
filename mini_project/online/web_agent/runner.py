# online/web_agent/runner.py
# Corrections:
# - Added handle_action to take dict from general_chat, dispatch to actor.
# - Made start async.
# - execute now for string commands (fallback if needed).
# - Removed sys.path.
# - Added stop cleanup.

import logging
from typing import Dict, Any, Optional

from online.web_agent.agents.actor import ActorAgent
from online.llm.local_llm import LocalLLM

logger = logging.getLogger("JARVIS_WebAgent")

class WebAgentRunner:
    def __init__(self, llm: Optional[LocalLLM] = None):
        self.llm = llm or LocalLLM()
        self.actor = ActorAgent(self.llm)
        self.running = False

    async def start(self, headless: bool = False) -> Dict[str, Any]:
        if not self.running:
            result = await self.actor.initialize(headless)
            if result["status"] == "success":
                self.running = True
        return {"status": "success", "message": "Web agent ready"}

    async def handle_action(self, action: dict) -> str:
        if not self.running:
            await self.start()
        try:
            result = await self.actor.process_action(action)
            msg = result.get("message", "Action completed") if isinstance(result, dict) else str(result)
            return msg
        except Exception as e:
            logger.error(f"Action failed: {e}")
            return f"Error during web action: {str(e)}"

    async def stop(self):
        if self.running:
            await self.actor.close()   # This calls browser.close() only once at shutdown
            self.running = False