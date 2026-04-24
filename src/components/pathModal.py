from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Button
from textual.containers import Vertical, Horizontal

class PathModal(ModalScreen[str]):
    """Modal to ask for a file path"""
    BINDINGS = [("enter", "submit", "Submit")]
    
    def __init__(self, title: str, default_path: str = "notes_export.json", **kwargs):
        self.modal_title = title
        self.default_path = default_path
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        with Vertical(id="path-modal-container"):
            yield Label(self.modal_title, id="path-modal-title")
            yield Input(value=self.default_path, placeholder="Enter file path...", id="path-input")
            with Horizontal(id="path-modal-buttons"):
                yield Button("Confirm", variant="success", id="confirm")
                yield Button("Cancel", variant="primary", id="cancel")

    def on_mount(self) -> None:
        self.query_one("#path-input").focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            path = self.query_one("#path-input", Input).value
            self.dismiss(path)
        else:
            self.dismiss(None)

    def action_submit(self):
        path = self.query_one("#path-input", Input).value
        self.dismiss(path)
