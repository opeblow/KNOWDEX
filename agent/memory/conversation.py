from typing import List
from agent.custom_types import Message

class ConversationMemory:
    def __init__(self):
        self.messages:List[Message]=[]

    def add(self,role:str,content:str,tool_calls=None,citations=None):
        self.messages.append(Message(
            role=role,
            content=content,
            tool_calls=tool_calls or [],
            citations=citations or []
        ))

    def get_openai_format(self):
        return [
            {"role":m.role,"content":m.content}
            for m in self.messages
        ]

        