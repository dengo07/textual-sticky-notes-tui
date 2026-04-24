import json
import os
import uuid
from pathlib import Path
from typing import List
from models import Note
from platformdirs import user_data_dir
from datetime import datetime

class NoteStorage:    
    def __init__(self, filename: str = "notes.json"):
        # Allow override via environment variable for easier syncing (e.g. to a cloud-synced folder)
        env_dir = os.environ.get('STICKY_NOTES_DIR')
        if env_dir:
            self.storage_dir = Path(env_dir)
        else:
            self.storage_dir = Path(user_data_dir("sticky-notes-tui", "sticky-notes"))
        
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.filepath = self.storage_dir / filename
    
    def save_notes(self, notes_with_colors: List[tuple], custom_path: Path = None) -> bool:
        try:
            notes_data = []
            for note, color in notes_with_colors:
                notes_data.append({
                    'noteTitle': note.noteTitle,
                    'content': note.content,
                    'tags': note.tags,
                    'priority': note.priority,
                    'pinned': note.pinned,
                    'note_id': note.note_id,
                    'last_updated': note.last_updated,
                    'color': color
                })
            
            target_path = custom_path if custom_path else self.filepath
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(notes_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving notes: {e}")
            return False
    
    def load_notes(self, custom_path: Path = None) -> List[tuple]:
        try:
            target_path = custom_path if custom_path else self.filepath
            if not target_path.exists():
                return []
            
            with open(target_path, 'r', encoding='utf-8') as f:
                notes_data = json.load(f)
            
            notes_with_colors = []
            for data in notes_data:
                note = Note(
                    noteTitle=data.get('noteTitle', ''),
                    content=data.get('content', ''),
                    tags=data.get('tags', ''),
                    priority=data.get('priority', 0),
                    pinned=data.get('pinned', False),
                    note_id=data.get('note_id', str(uuid.uuid4())),
                    last_updated=data.get('last_updated', datetime.now().strftime("%Y-%m-%d %H:%M"))
                )
                color = data.get('color', 'white')
                notes_with_colors.append((note, color))
            
            return notes_with_colors
        except Exception as e:
            print(f"Error loading notes: {e}")
            return []
