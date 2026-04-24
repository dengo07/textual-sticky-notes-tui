from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal

class HelpModal(ModalScreen):
    BINDINGS = [("escape,q", "close", "Close")]

    HELP_TEXT = """
# Sticky Notes TUI - Help

## Navigation
- **Arrows / hjkl**: Move focus between notes
- **Tab / Shift+Tab**: Cycle focus

## Actions
- **a**: Add a new note
- **e**: Edit selected note
- **r**: Delete selected note
- **f**: Focus View (Fullscreen Markdown)
- **t**: Toggle Tag Sidebar
- **c**: Copy note content to system clipboard
- **v**: Paste clipboard as a new note
- **s**: Search notes
- **o**: Sort notes (pinned first, then priority)
- **1-9**: Change note color

## Storage
- **Ctrl+s**: Save notes manually
- **Ctrl+l**: Load notes manually
- **Ctrl+e**: Export notes to a specific file
- **Ctrl+g**: Import notes from a specific file (Smart Merge)

## System
- **d**: Toggle dark mode
- **Ctrl+c**: Quit
- **?**: Show this help
- **F1**: Show About info
"""

    def compose(self) -> ComposeResult:
        with Vertical(id="help-container"):
            yield Static(self.HELP_TEXT, id="help-text")
            with Horizontal(id="help-buttons"):
                yield Button("Close", variant="primary", id="close-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-btn":
            self.dismiss()

    def action_close(self):
        self.dismiss()
