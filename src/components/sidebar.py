from textual.app import ComposeResult
from textual.widgets import Static, ListView, ListItem, Label
from textual.containers import Vertical
from textual.message import Message

class Sidebar(Vertical):
    """A sidebar that displays unique tags and allows filtering."""

    class TagSelected(Message):
        """Sent when a tag is selected."""
        def __init__(self, tag: str | None) -> None:
            self.tag = tag
            super().__init__()

    def compose(self) -> ComposeResult:
        yield Label("🏷️ Tags", id="sidebar-title")
        yield ListView(id="tag-list")

    def update_tags(self, tags: list[str]):
        """Update the list of tags displayed in the sidebar."""
        list_view = self.query_one("#tag-list", ListView)
        list_view.clear()
        
        # Add "Show All" option using 'name' for metadata instead of 'id'
        list_view.append(ListItem(Label("All Notes"), name="all"))
        
        # Add unique tags
        for tag in sorted(tags):
            tag_name = tag.strip()
            if tag_name:
                list_view.append(ListItem(Label(f"#{tag_name}"), name=tag_name))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle tag selection."""
        # Use the 'name' attribute we set during update_tags
        selected_tag = event.item.name
        
        if selected_tag == "all":
            self.post_message(self.TagSelected(None))
        else:
            self.post_message(self.TagSelected(selected_tag))
