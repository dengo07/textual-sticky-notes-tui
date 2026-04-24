from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal

class AboutModal(ModalScreen):
    """A modal showing app information and credits."""
    
    BINDINGS = [("escape", "dismiss", "Close")]

    ABOUT_TEXT = """
# Sticky Notes TUI

**Version:** 1.0.0 (Build 2026.04.23)
**Engine:** Textual (Python)

---

A modern, keyboard-centric terminal application for managing thoughts and tasks with Markdown support.

**Author: Elevation75** [Elevation75]
**GitHub:https://github.com/elevation75/sticky-notes-tui** 

---
*Created with ❤️ for Linux/Mac community*
*Inspired by Dengo07's Textual Sticky Notes app - https://github.com/dengo07/textual-sticky-notes-tui*

"""

    def compose(self) -> ComposeResult:
        with Vertical(id="about-container"):
            yield Static(self.ABOUT_TEXT, id="about-text")
            with Horizontal(id="about-buttons"):
                yield Button("Close", variant="primary", id="close-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-btn":
            self.dismiss()

    def action_dismiss(self):
        self.dismiss()
