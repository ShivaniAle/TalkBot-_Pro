from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Message(BaseModel):
    """Model for a single message in a conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = datetime.now()

class Conversation(BaseModel):
    """Model for a conversation thread"""
    id: str
    messages: List[Message] = []
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    def add_message(self, role: str, content: str):
        """Add a new message to the conversation"""
        self.messages.append(Message(role=role, content=content))
        self.updated_at = datetime.now()
    
    def get_last_message(self) -> Optional[Message]:
        """Get the last message in the conversation"""
        return self.messages[-1] if self.messages else None 