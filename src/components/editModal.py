import copy
from textual.screen import ModalScreen
from textual.widgets import TextArea, OptionList, Checkbox, Label, Button,Input
from textual.containers import HorizontalGroup, ScrollableContainer, Horizontal
from textual.widgets.option_list import Option

from models import Note
from datetime import datetime

class EditModal(ModalScreen[Note]):
    BINDINGS = [("escape", "dismiss", "Close")] 

    note: Note
    oldNote: Note
    COMMON_EMOJIS = ["✅", "❌", "⚠️", "🚀", "💡", "📌", "⭐", "🔥", "📅", "📝"]

    def __init__(self, note: Note, **kwargs):
        self.note = note
        self.oldNote = copy.deepcopy(note)
        super().__init__(**kwargs)
    
    def compose(self):
        with ScrollableContainer(id="editModalContainer"):
            yield Label("Enter title")
            yield TextArea(text=self.note.noteTitle, id="title")

            yield Label("Enter Content")
            yield TextArea(text=self.note.content, id="content")

            yield Label("Quick Emojis")
            with Horizontal(id="emoji-bar"):
                for i, emoji in enumerate(self.COMMON_EMOJIS):
                    yield Button(emoji, variant="default", classes="emoji-btn", id=f"emoji-{i}")

            yield Label("Enter tags")
            yield Input(value=self.note.tags, id="tags")

            yield Label("Priority")
            option_list = OptionList(
                Option("⚪ Trivial", id="0"),
                Option("🔵 Low", id="1"),
                Option("🟡 Medium", id="2"),
                Option("🟠 High", id="3"),
                Option("🔴 Critical", id="4"),
                id="priority"
            )
            if 0 <= self.note.priority <= 4:
                option_list.highlighted = self.note.priority
            yield option_list

            yield Checkbox("📌 Pinned", value=self.note.pinned, id="pinned")

            with HorizontalGroup():
                yield Button("Save", variant="success", id="save")
                yield Button("Cancel", variant="primary", id="cancel")

        return super().compose()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.has_class("emoji-btn"):
            emoji = event.button.label.plain
            content_textarea = self.query_one("#content", TextArea)
            content_textarea.insert(emoji)
            content_textarea.focus()
            return

        if event.button.id == "save":   
            self.note.noteTitle = self.query_one("#title", TextArea).text
            self.note.content = self.query_one("#content", TextArea).text
            self.note.tags = self.query_one("#tags", Input).value
            self.note.pinned = self.query_one("#pinned", Checkbox).value
            
            priority_list = self.query_one("#priority", OptionList)
            if priority_list.highlighted is not None:
                self.note.priority = int(priority_list.get_option_at_index(priority_list.highlighted).id)
            
            self.note.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.dismiss(self.note)  
        else:
            self.dismiss(self.oldNote)
    
    def action_dismiss(self):
        self.dismiss()