from dataclasses import dataclass, field
import uuid
from datetime import datetime

@dataclass
class Note:
    noteTitle:str
    content:str= " "
    tags: str = " "
    priority:int = 0
    pinned:bool = False
    note_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    last_updated: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))