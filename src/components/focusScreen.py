from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Markdown, Header, Footer
from textual.containers import ScrollableContainer
from models import Note

class FocusScreen(ModalScreen):
    """A full-screen view for reading a single note in detail."""
    
    BINDINGS = [("escape", "dismiss", "Exit Focus Mode"), ("f", "dismiss", "Exit Focus Mode")]

    def __init__(self, note: Note, **kwargs):
        self.note = note
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        yield Header()
        with ScrollableContainer(id="focus-container"):
            yield Markdown(self.note.content, id="focus-markdown")
        yield Footer()

    def action_dismiss(self) -> None:
        self.dismiss()
