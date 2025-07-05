from dataclasses import dataclass

@dataclass
class ChatGPTSettings:
    Key: str = ""
    Model: str = "gpt-4o"