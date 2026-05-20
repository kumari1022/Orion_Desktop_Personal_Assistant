# online/web_agent/core/observer.py
# Corrections:
# - Integrated basic usage in actor.py (log interactions).
# - No major changes, but made it optional.

from typing import Dict, Any, List
from datetime import datetime
from enum import Enum

class PageState(Enum):
    IDLE = "idle"
    LOADING = "loading"
    READY = "ready"
    INTERACTING = "interacting"

class WebObserver:
    def __init__(self):
        self.state = PageState.IDLE
        self.tabs: Dict[str, dict] = {}
        self.current_tab = None
        self.history: List[dict] = []
        self.context: List[dict] = []
        
    def update_state(self, state: PageState):
        self.state = state
        
    def log_interaction(self, action: str, details: dict, success: bool):
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "success": success
        })
        
    def add_context(self, role: str, content: str):
        self.context.append({"role": role, "content": content, "timestamp": datetime.now().isoformat()})
        
    def get_summary(self) -> str:
        return f"State: {self.state.value}, Tabs: {len(self.tabs)}, History: {len(self.history)}"