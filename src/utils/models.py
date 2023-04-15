from dataclasses import dataclass

@dataclass
class User:
    username: str
    name: str|None
    bio: str|None
    followers: int|None
    following: int|None

@dataclass
class Message:
    sender: str
    receiver: str
    message: str
    
@dataclass
class Error:
    message: str