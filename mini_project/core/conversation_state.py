# core/conversation_state.py

class ConversationStateManager:
    def __init__(self):
        self.state = None
        
    def set_state(self, action: str, recipient: str = None, message_body: str = None, awaiting_email_body: bool = False, awaiting_send_confirmation: bool = False):
        self.state = {
            "action": action,
            "recipient": recipient,
            "message_body": message_body,
            "awaiting_email_body": awaiting_email_body,
            "awaiting_send_confirmation": awaiting_send_confirmation
        }
        
    def update_state(self, **kwargs):
        if self.state:
            self.state.update(kwargs)
            
    def get_state(self) -> dict:
        return self.state
        
    def clear_state(self):
        self.state = None

state_manager = ConversationStateManager()
