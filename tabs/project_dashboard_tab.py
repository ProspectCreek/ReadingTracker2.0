import tkinter as tk
from tkinter import ttk, font

# --- Add project root to sys.path ---
import sys
import os

file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(file_dir)
if project_root not in sys.path:
    sys.path.append(project_root)
# --- END FIX ---

from utils.text_toolbar import TextToolbar


class ProjectDashboardTab(ttk.Frame):
    """
    The main "Project Dashboard" tab, containing the
    Readings, Purpose, Goals, and the bottom text editor.
    """

    def __init__(self, parent, project_details, db_manager):
        super().__init__(parent)

        self.project_id = project_details['id']
        self.db = db_manager

        # --- FIX: Convert sqlite3.Row to a mutable dict ---
        # This allows us to update the dictionary in memory
        self.project_details = dict(project_details)

        self.instructions = self.db.get_or_create_instructions(self.project_id)

        self.tab_map = {
            "Key Questions": ("key_questions_text", "key_questions_instr"),
            "Thesis/Argument": ("thesis_text", "thesis_instr"),
            "Key Insights": ("insights_text", "insights_instr"),
            "Unresolved Questions": ("unresolved_text", "unresolved_instr")
        }

        # --- Get the keys from the dict ---
        self.project_keys = self.project_details.keys()

        # --- Main Layout (2 rows) ---
        self.grid_rowconfigure(0, weight=1)  # Top half
        self.grid_rowconfigure(1, weight=1)  # Bottom half
        self.grid_columnconfigure(0, weight=1)

        # --- (1) Top Half Container ---
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        top_frame.grid_rowconfigure(0, weight=1)
        # Use PanedWindow for resizable columns
        top_paned_window = ttk.PanedWindow(top_frame, orient='horizontal')
        top_paned_window.pack(fill="both", expand=True)

        # --- (1A) Reading Viewer ---
        readings_frame = ttk.LabelFrame(top_paned_window, text="Readings")
        top_paned_window.add(readings_frame, weight=1)  # 1/3 width

        self.reading_tree = ttk.Treeview(readings_frame, columns=("author",), height=5)
        self.reading_tree.heading("#0", text="Title")
        self.reading_tree.heading("author", text="Author")
        self.reading_tree.pack(fill="both", expand=True, padx=5, pady=5)
        # Add placeholder right-click menu
        self.reading_tree.bind("<Button-3>", self.show_reading_context_menu)

        # --- Right Half of Top Frame ---
        top_right_frame = ttk.Frame(top_paned_window)
        top_paned_window.add(top_right_frame, weight=2)  # 2/3 width
        top_right_frame.grid_rowconfigure(0, weight=1)  # Purpose (1/4 height)
        top_right_frame.grid_rowconfigure(1, weight=1)  # Goals (1/4 height)
        top_right_frame.grid_columnconfigure(0, weight=1)

        # --- (2) Project Purpose ---
        purpose_frame = ttk.LabelFrame(top_right_frame, text="Project Purpose")
        purpose_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=(0, 5))
        self.purpose_text = tk.Text(purpose_frame, height=5, wrap="word", undo=True)
        self.purpose_text.pack(fill="both", expand=True, padx=5, pady=5)

        purpose_content = self.project_details[
            "project_purpose_text"] if "project_purpose_text" in self.project_keys else ""
        if purpose_content is None: purpose_content = ""  # Handle NULL from DB
        self.purpose_text.insert("1.0", purpose_content)

        self.purpose_text.bind("<FocusOut>", lambda e: self.save_text_content(
            self.purpose_text, "project_purpose_text"
        ))
        # --- NEW: Setup tags and bind shortcuts ---
        self.setup_manual_tags(self.purpose_text)
        self.bind_text_shortcuts(self.purpose_text)

        # --- (3) My Goals ---
        goals_frame = ttk.LabelFrame(top_right_frame, text="My Goals")
        goals_frame.grid(row=1, column=0, sticky="nsew", padx=5)
        self.goals_text = tk.Text(goals_frame, height=5, wrap="word", undo=True)
        self.goals_text.pack(fill="both", expand=True, padx=5, pady=5)

        goals_content = self.project_details["project_goals_text"] if "project_goals_text" in self.project_keys else ""
        if goals_content is None: goals_content = ""  # Handle NULL from DB
        self.goals_text.insert("1.0", goals_content)

        self.goals_text.bind("<FocusOut>", lambda e: self.save_text_content(
            self.goals_text, "project_goals_text"
        ))
        # --- NEW: Setup tags and bind shortcuts ---
        self.setup_manual_tags(self.goals_text)
        self.bind_text_shortcuts(self.goals_text)

        # --- (4) Bottom Half Container ---
        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        bottom_frame.grid_rowconfigure(3, weight=1)  # Text editor (changed from 2 to 3)
        bottom_frame.grid_columnconfigure(0, weight=1)

        # --- (4A-D) Bottom Notebook ---
        self.bottom_notebook = ttk.Notebook(bottom_frame)
        self.bottom_notebook.grid(row=0, column=0, sticky="ew")

        for tab_name in self.tab_map.keys():
            tab_frame = ttk.Frame(self.bottom_notebook)  # Empty frame
            self.bottom_notebook.add(tab_frame, text=tab_name)

        # --- (5) Instruction Label ---
        self.instruction_label = ttk.Label(
            bottom_frame,
            text="Select a tab to see instructions.",
            wraplength=800,
            justify="center",
            style="TLabel"  # Use a base style
        )
        self.instruction_label.grid(row=1, column=0, sticky="ew", pady=5)

        # --- (6) Main Text Editor (bottom) ---
        self.main_text_editor = tk.Text(bottom_frame, height=10, wrap="word", undo=True)

        # --- (7) Text Toolbar ---
        self.toolbar = TextToolbar(bottom_frame, self.main_text_editor)
        self.toolbar.grid(row=2, column=0, sticky="ew", pady=(0, 5))

        # Grid the text editor *after* the toolbar
        self.main_text_editor.grid(row=3, column=0, sticky="nsew")
        self.main_text_editor.bind("<FocusOut>", self.save_current_tab_text)
        # --- This one uses the toolbar, so no manual setup needed ---
        self.bind_text_shortcuts(self.main_text_editor)

        # Bind tab change event
        self.bottom_notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Load initial tab
        self.on_tab_changed(None)

        # --- FIXED: Restored function body ---

    def on_tab_changed(self, event):
        """Called when the bottom notebook tab is changed."""
        try:
            current_tab_name = self.bottom_notebook.tab(self.bottom_notebook.select(), "text")
        except tk.TclError:
            return  # No tab selected

        if current_tab_name in self.tab_map:
            db_field, instr_field = self.tab_map[current_tab_name]

            # (5) Update instruction label
            self.instruction_label.config(text=self.instructions[instr_field])

            # Load text from database
            self.main_text_editor.delete("1.0", "end")

            tab_content = self.project_details[db_field] if db_field in self.project_keys else ""
            if tab_content is None: tab_content = ""  # Handle NULL from DB

            self.main_text_editor.insert("1.0", tab_content)

    # --- FIXED: Restored function body ---
    def save_current_tab_text(self, event=None):
        """Saves the content of the main text editor to the correct DB field."""
        try:
            current_tab_name = self.bottom_notebook.tab(self.bottom_notebook.select(), "text")
        except tk.TclError:
            return  # No tab selected

        if current_tab_name in self.tab_map:
            db_field, _ = self.tab_map[current_tab_name]
            content = self.main_text_editor.get("1.0", "end-1c")

            # Save to DB
            self.save_text_content(self.main_text_editor, db_field)

            # Update local details if key exists
            if db_field in self.project_keys:
                self.project_details[db_field] = content

    # --- FIXED: Restored function body ---
    def save_text_content(self, text_widget, db_field_name):
        """Helper to save content of a text widget to the DB."""
        if db_field_name not in self.project_keys:
            print(f"Warning: Column {db_field_name} not in database. Skipping save.")
            return

        content = text_widget.get("1.0", "end-1c")
        self.db.update_project_text_field(self.project_id, db_field_name, content)

        # Update local details
        self.project_details[db_field_name] = content
        print(f"Saved {db_field_name}")  # For debugging

    # --- FIXED: Restored function body ---
    def refresh_instructions(self):
        """Called from parent to reload instructions from DB."""
        self.instructions = self.db.get_or_create_instructions(self.project_id)
        # Trigger a tab change event to reload the label
        self.on_tab_changed(None)

    # --- FIXED: Restored function body ---
    def show_reading_context_menu(self, event):
        """Placeholder for reading viewer's right-click menu."""
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Add Reading (Placeholder)")
        menu.add_command(label="Delete Reading (Placeholder)")
        menu.add_command(label="Reorder (Placeholder)")

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    # --- UPDATED: Text Editor Shortcut Functions ---

    def setup_manual_tags(self, text_widget):
        """Configures non-font tags for a text widget."""
        # --- FIX: We only need to configure non-font tags now ---
        text_widget.tag_configure("highlight", background="yellow")
        text_widget.tag_configure(
            "indent",
            lmargin1=30,
            lmargin2=30
        )
        # We no longer need to store custom fonts
        # text_widget.custom_fonts = ...

    def bind_text_shortcuts(self, text_widget):
        """Binds all Ctrl+Key shortcuts to a given text widget."""
        text_widget.bind("<Control-BackSpace>", lambda e: self.delete_word_backward(e.widget))
        text_widget.bind("<Control-Delete>", lambda e: self.delete_word_forward(e.widget))
        text_widget.bind("<Control-x>", lambda e: self.cut(e.widget))
        text_widget.bind("<Control-c>", lambda e: self.copy(e.widget))
        text_widget.bind("<Control-v>", lambda e: self.paste(e.widget))

        # --- UPDATED: These bindings now call smart handlers ---
        text_widget.bind("<Control-b>", self.on_ctrl_b)
        text_widget.bind("<Control-i>", self.on_ctrl_i)
        text_widget.bind("<Control-u>", self.on_ctrl_u)

    # --- FIXED: Restored function body ---
    def delete_word_backward(self, text_widget):
        """Deletes the word immediately behind the cursor."""
        try:
            delete_start = text_widget.index("insert wordstart")
            if delete_start == text_widget.index("insert"):
                delete_start = text_widget.index("insert-1c wordstart")
            text_widget.delete(delete_start, "insert")
        except tk.TclError:
            pass
        return "break"  # Prevents default binding

    def delete_word_forward(self, text_widget):
        """Deletes the word immediately in front of the cursor."""
        try:
            delete_end = text_widget.index("insert wordend")
            if delete_end == text_widget.index("insert"):
                delete_end = text_widget.index("insert+1c wordend")
            text_widget.delete("insert", delete_end)
        except tk.TclError:
            pass
        return "break"  # Prevents default binding

    def cut(self, text_widget):
        try:
            text_widget.event_generate("<<Cut>>")
        except tk.TclError:
            pass
        return "break"

    def copy(self, text_widget):
        try:
            text_widget.event_generate("<<Copy>>")
        except tk.TclError:
            pass
        return "break"

    def paste(self, text_widget):
        try:
            text_widget.event_generate("<<Paste>>")
        except tk.TclError:
            pass
        return "break"

    # --- NEW: Manual tag toggler ---
    def _get_font_at_selection(self, text_widget):
        """Helper to get the font.Font object at the current selection."""
        try:
            font_str = text_widget.cget("font")  # Default
            tags_at_sel = text_widget.tag_names("sel.first")
            for tag in tags_at_sel:
                font_option = text_widget.tag_cget(tag, "font")
                if font_option:
                    font_str = font_option
            return font.Font(font=font_str)
        except tk.TclError:
            return font.Font(font=text_widget.cget("font"))

    def _apply_dynamic_tag(self, text_widget, new_font_config):
        """Applies a dynamically named tag with the new font."""
        tag_name = (
            f"f_{new_font_config['family'].replace(' ', '_')}"
            f"_{new_font_config['size']}"
            f"_{new_font_config['weight']}"
            f"_{new_font_config['slant']}"
            f"_{new_font_config['underline']}"
        )

        # We need to cache fonts on the widget itself or they get garbage-collected
        if not hasattr(text_widget, 'font_cache'):
            text_widget.font_cache = {}

        if tag_name not in text_widget.font_cache:
            text_widget.font_cache[tag_name] = font.Font(**new_font_config)
            text_widget.tag_configure(tag_name, font=text_widget.font_cache[tag_name])

        text_widget.tag_add(tag_name, "sel.first", "sel.last")

    def toggle_tag_manual(self, text_widget, tag_name):
        """Manually toggles a font style on a widget (one that has no toolbar)."""
        try:
            sel_ranges = text_widget.tag_ranges("sel")
            if not sel_ranges:
                return  # No selection

            current_font = self._get_font_at_selection(text_widget)
            new_config = current_font.actual()

            if tag_name == "bold":
                new_config["weight"] = "normal" if new_config["weight"] == "bold" else "bold"
            elif tag_name == "italic":
                new_config["slant"] = "roman" if new_config["slant"] == "italic" else "italic"
            elif tag_name == "underline":
                new_config["underline"] = 0 if new_config["underline"] == 1 else 1

            self._apply_dynamic_tag(text_widget, new_config)

        except tk.TclError:
            pass  # No text selected

    # --- UPDATED: Smart handlers for Ctrl+B/I/U ---

    def on_ctrl_b(self, event):
        """Handles Ctrl+B event and stops propagation."""
        if event.widget == self.main_text_editor:
            self.toolbar.toggle_tag("bold")
        else:
            self.toggle_tag_manual(event.widget, "bold")
        return "break"

    def on_ctrl_i(self, event):
        """Handles Ctrl+I event and stops propagation."""
        if event.widget == self.main_text_editor:
            self.toolbar.toggle_tag("italic")
        else:
            self.toggle_tag_manual(event.widget, "italic")
        return "break"

    def on_ctrl_u(self, event):
        """Handles Ctrl+U event and stops propagation."""
        if event.widget == self.main_text_editor:
            self.toolbar.toggle_tag("underline")
        else:
            self.toggle_tag_manual(event.widget, "underline")
        return "break"
    # --- END UPDATED ---



