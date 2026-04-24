import copy
import uuid
from storage import NoteStorage
from dataclasses import replace
from textual.app import App, ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Header, Footer,Static
from textual.containers import ScrollableContainer, Horizontal
from textual import work
from components.deleteModal import DeleteModal
from components.editModal import EditModal
from components.searchModal import SearchModal
from components.helpModal import HelpModal
from components.pathModal import PathModal
from components.focusScreen import FocusScreen
from components.sidebar import Sidebar
from components.aboutModal import AboutModal
from components.stickyNote import StickyNote
from models import Note
from pathlib import Path
import pyperclip
from datetime import datetime


class StickyNotesApp(App):
    column_count = 3;
    storage: NoteStorage = None
    default_note:Note = Note("New note", content="## Welcome\n- Write **Markdown**\n- Add #tags\n- Use emojis ✅")
    active_tag: str | None = None

    BINDINGS = [("d", "toggle_dark_mode", "toggle dark mode"),
                ("ctrl+c", "quit", "Force Quit"),
                ("right", "focus_next", "Next"),
                ("l", "focus_next", "Next"),
                ("left", "focus_previous", "Prev"),
                ("h", "focus_previous", "Prev"),
                ("up", "move_up", "Move Up"),
                ("k", "move_up", "Move Up"),
                ("down", "move_down", "Move Down"),
                ("j", "move_down", "Move Down"),
                ("a","add_note","add a new note"),
                ("r","delete_note","delete a note"),
                ("e","edit_note","edit a note"),
                ("f","focus_note","focus view"),
                ("t","toggle_sidebar","tags sidebar"),
                ("c","copy_note","copy note text"),
                ("v","paste_note","paste as new note"),
                ("1-9"," ","border color"),
                ("s","search_notes","search notes"),
                ("o", "sort_notes", "Sort notes"),
                ("?", "show_help", "Help"),
                ("f1", "show_about", "About"),
                ("ctrl+s", "save_notes", "Save notes"), 
                ("ctrl+l", "load_notes", "Load notes"),
                ("ctrl+e", "export_notes", "Export notes"),
                ("ctrl+g", "import_notes", "Import notes"),
                ]
    CSS_PATH = "style.css"

    COLORS = {
        "1": "#ffadad", "2": "#ffd6a5", "3": "#fdffb6",
        "4": "#caffbf", "5": "#9bf6ff", "6": "#a0c4ff",
        "7": "#bdb2ff", "8": "#ffc6ff", "9": "#fffffc"
    }

    def on_key(self, event) -> None:
        if isinstance(self.screen, ModalScreen):
            return  

        if event.key in self.COLORS:
            focused_widget = self.screen.focused
            if isinstance(focused_widget, StickyNote):
                focused_widget.user_color = self.COLORS[event.key]
                focused_widget.color = self.COLORS[event.key]
                self.action_save_notes()

    def action_move_up(self):
        for _ in range(self.column_count):
            self.action_focus_previous()
    def action_move_down(self):
        for _ in range(self.column_count):
            self.action_focus_next()

    def on_mount(self) -> None:
        self.storage = NoteStorage()
        self.load_saved_notes()
        self.refresh_sidebar()
        self.query_one("#notes").focus()

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Sidebar(id="sidebar")
            with ScrollableContainer(id="notes"):
                pass
        yield Footer()

    def action_toggle_dark_mode(self):
        self.action_toggle_dark()

    def action_show_help(self):
        self.push_screen(HelpModal())

    def action_show_about(self):
        self.push_screen(AboutModal())

    def action_toggle_sidebar(self):
        sidebar = self.query_one("#sidebar")
        sidebar.display = not sidebar.display
        if not sidebar.display:
            # If hiding sidebar, clear filter
            self.filter_by_tag(None)

    def refresh_sidebar(self):
        """Extract all unique tags and update sidebar."""
        all_tags = set()
        for note_widget in self.query(StickyNote):
            # Split tags by comma or space
            tags = note_widget.note.tags.replace(',', ' ').split()
            for t in tags:
                all_tags.add(t.strip())
        
        self.query_one("#sidebar", Sidebar).update_tags(list(all_tags))

    def on_sidebar_tag_selected(self, message: Sidebar.TagSelected):
        """Handle tag selection from sidebar."""
        self.filter_by_tag(message.tag)

    def filter_by_tag(self, tag: str | None):
        """Filter the displayed notes by the selected tag."""
        self.active_tag = tag
        for note_widget in self.query(StickyNote):
            if tag is None:
                note_widget.display = True
            else:
                # Check if tag is in the note's tags
                note_tags = note_widget.note.tags.replace(',', ' ').split()
                note_widget.display = any(t.strip().lower() == tag.lower() for t in note_tags)
        
        if tag:
            self.notify(f"Filtering by: #{tag}", severity="information")
        else:
            self.notify("Showing all notes", severity="information")
    
    @work
    async def action_add_note(self):
        new_note = copy.deepcopy(self.default_note)
        new_note.note_id = str(uuid.uuid4())
        stickyNote = StickyNote(note=new_note)
        container = self.query_one("#notes")
        container.mount(stickyNote)
        stickyNote.scroll_visible()
        self.refresh_sidebar()
        self.filter_by_tag(self.active_tag)
        self.action_save_notes()

    def action_copy_note(self):
        focused_widget = self.screen.focused
        if focused_widget is not None and isinstance(focused_widget, StickyNote):
            content = focused_widget.note.content
            try:
                pyperclip.copy(content)
                self.notify("Copied note content to clipboard!", severity="information")
            except Exception as e:
                self.notify(f"Clipboard error: {e}", severity="error")

    def action_focus_note(self):
        focused_widget = self.screen.focused
        if focused_widget is not None and isinstance(focused_widget, StickyNote):
            self.push_screen(FocusScreen(focused_widget.note))

    @work
    async def action_paste_note(self):
        try:
            clipboard_content = pyperclip.paste()
            if not clipboard_content:
                self.notify("Clipboard is empty", severity="warning")
                return
            
            new_note = Note(
                noteTitle="Pasted Note",
                content=clipboard_content,
                last_updated=datetime.now().strftime("%Y-%m-%d %H:%M")
            )
            stickyNote = StickyNote(note=new_note)
            container = self.query_one("#notes")
            container.mount(stickyNote)
            stickyNote.scroll_visible()
            self.action_save_notes()
            self.notify("Pasted content as new note", severity="success")
        except Exception as e:
            self.notify(f"Clipboard error: {e}", severity="error")

    def action_sort_notes(self):
        self.sort_notes()
        self.notify("Notes sorted!", severity="information")

    def sort_notes(self):
        """Sort notes: pinned first, then by priority"""
        container = self.query_one("#notes")
        notes = list(self.query(StickyNote))
        
        if not notes:
            return
        
        sorted_notes = sorted(notes, 
                            key=lambda n: (-n.is_pinned, -n.priority_level))
            
        for note in sorted_notes:
            container.move_child(note, after=container.children[-1])
        
        self.action_save_notes()

    @work
    async def action_delete_note(self):
        focused_widget = self.screen.focused

        if focused_widget is not None and isinstance(focused_widget, StickyNote):
            confirm = await self.push_screen_wait(DeleteModal())
            if confirm:
                # Gather notes EXCLUDING the one we are about to delete
                # to ensure the save is accurate regardless of DOM removal timing
                notes_to_keep = []
                for sn in self.query(StickyNote):
                    if sn != focused_widget:
                        notes_to_keep.append((sn.note, sn.color))
                
                # Perform removal
                focused_widget.remove()
                self.refresh_sidebar()
                
                # Save the new state
                if self.storage.save_notes(notes_to_keep):
                    self.notify(f"Deleted and saved ({len(notes_to_keep)} remaining)", severity="success")
                else:
                    self.notify("Failed to save changes after deletion", severity="error")

    @work
    async def action_edit_note(self):
        focused_widget = self.screen.focused
        if focused_widget is not None and isinstance(focused_widget, StickyNote):
            updatedNote = await self.push_screen_wait(EditModal(focused_widget.note))
            if updatedNote:
                focused_widget.note = updatedNote
                
                focused_widget.priority_level = updatedNote.priority
                focused_widget.is_pinned = updatedNote.pinned
                
                focused_widget.update_title()
                
                focused_widget.update_content()
                self.refresh_sidebar()
                self.filter_by_tag(self.active_tag)
                self.action_sort_notes()

    @work
    async def action_search_notes(self):
        """Search through all notes"""
        all_sticky_notes = list(self.query(StickyNote))
        all_notes = [sn.note for sn in all_sticky_notes]
        
        if not all_notes:
            self.notify("No notes to search!", severity="warning")
            return

        selected_note = await self.push_screen_wait(SearchModal(all_notes))
        
        if selected_note is not None:
            for sticky_note in all_sticky_notes:
                if sticky_note.note.note_id == selected_note.note_id:
                    sticky_note.focus()
                    sticky_note.scroll_visible()
                    self.notify(f"Found: {selected_note.noteTitle}", severity="information")
                    return
            
            self.notify("Could not find the note", severity="error")

    def load_saved_notes(self):
        notes_with_colors = self.storage.load_notes()
        
        if notes_with_colors:
            container = self.query_one("#notes")
            for widget in list(self.query(StickyNote)):
                widget.remove()
            
            for note, color in notes_with_colors:
                sticky_note = StickyNote(note=note)
                sticky_note.user_color = color
                sticky_note.color = color
                sticky_note.priority_level = note.priority
                sticky_note.is_pinned = note.pinned
                container.mount(sticky_note)
                
            self.refresh_sidebar()
            self.filter_by_tag(None)
            self.notify(f"Loaded {len(notes_with_colors)} notes!", severity="information")

    def action_save_notes(self):
        notes_with_colors = []
        for sticky_note in self.query(StickyNote):
            notes_with_colors.append((sticky_note.note, sticky_note.color))
        
        if self.storage.save_notes(notes_with_colors):
            self.notify(f"💾 Saved {len(notes_with_colors)} notes!", severity="success")
        else:
            self.notify("Failed to save notes", severity="error")

    def action_load_notes(self):
        self.load_saved_notes()

    @work
    async def action_export_notes(self):
        path_str = await self.push_screen_wait(PathModal("Export Notes To Path", "notes_export.json"))
        if path_str:
            export_path = Path(path_str)
            notes_with_colors = []
            for sticky_note in self.query(StickyNote):
                notes_with_colors.append((sticky_note.note, sticky_note.color))
            
            if self.storage.save_notes(notes_with_colors, custom_path=export_path):
                self.notify(f"Exported to {export_path.name}", severity="success")
            else:
                self.notify("Export failed", severity="error")

    @work
    async def action_import_notes(self):
        path_str = await self.push_screen_wait(PathModal("Import Notes From Path", "notes_export.json"))
        if path_str:
            import_path = Path(path_str)
            if not import_path.exists():
                self.notify("File not found", severity="error")
                return

            imported_data = self.storage.load_notes(custom_path=import_path)
            if not imported_data:
                self.notify("No notes found in file", severity="warning")
                return

            container = self.query_one("#notes")
            existing_notes = {sn.note.note_id: sn for sn in self.query(StickyNote)}
            
            new_count = 0
            updated_count = 0

            for note, color in imported_data:
                if note.note_id in existing_notes:
                    # Update existing note
                    sn = existing_notes[note.note_id]
                    sn.note = note
                    sn.user_color = color
                    sn.color = color
                    sn.priority_level = note.priority
                    sn.is_pinned = note.pinned
                    sn.update_title()
                    sn.query_one("#noteContent").update(note.content)
                    updated_count += 1
                else:
                    # Add new note
                    sticky_note = StickyNote(note=note)
                    sticky_note.user_color = color
                    sticky_note.color = color
                    sticky_note.priority_level = note.priority
                    sticky_note.is_pinned = note.pinned
                    container.mount(sticky_note)
                    new_count += 1
            
            self.refresh_sidebar()
            self.action_sort_notes()
            self.notify(f"Imported: {new_count} new, {updated_count} updated", severity="success")

    def _on_resize(self, event):
        notes_container = self.query_one("#notes")
        self.column_count = max(1,event.size.width//40)
        notes_container.styles.grid_size_columns = self.column_count
        return super()._on_resize(event)

