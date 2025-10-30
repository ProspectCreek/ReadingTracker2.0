import tkinter as tk
from tkinter import ttk, font
from utils.tooltips import Tooltip


class TextToolbar(ttk.Frame):
    """
    A reusable text formatting toolbar.
    It applies tags (like 'bold', 'italic') to a target tk.Text widget.
    """

    def __init__(self, parent, target_text_widget):
        super().__init__(parent)
        self.text_widget = target_text_widget
        self.fonts = {}  # Cache for fonts

        # --- FIX: We will not pre-configure tags here ---
        # Instead, we will create them dynamically

        # We still need to configure non-font tags
        self.text_widget.tag_configure("highlight", background="yellow")
        self.text_widget.tag_configure(
            "indent",
            lmargin1=30,
            lmargin2=30
        )
        self.indent_active = False  # State tracker

        # --- Create Buttons (Now with Tooltips) ---
        btn_bold = ttk.Button(self, text="B", width=3, command=lambda: self.toggle_tag("bold"))
        btn_bold.pack(side="left", padx=2, pady=2)
        Tooltip(btn_bold, "Bold (Ctrl+B)")

        btn_italic = ttk.Button(self, text="I", width=3, command=lambda: self.toggle_tag("italic"))
        btn_italic.pack(side="left", padx=2, pady=2)
        Tooltip(btn_italic, "Italic (Ctrl+I)")

        btn_underline = ttk.Button(self, text="U", width=3, command=lambda: self.toggle_tag("underline"))
        btn_underline.pack(side="left", padx=2, pady=2)
        Tooltip(btn_underline, "Underline (Ctrl+U)")

        btn_highlight = ttk.Button(self, text="H", width=3, command=lambda: self.toggle_tag("highlight"))
        btn_highlight.pack(side="left", padx=2, pady=2)
        Tooltip(btn_highlight, "Highlight")

        btn_bullet = ttk.Button(self, text="•", width=3, command=self.add_bullet)
        btn_bullet.pack(side="left", padx=2, pady=2)
        Tooltip(btn_bullet, "Bullet Point")

        btn_num = ttk.Button(self, text="1.", width=3, command=self.add_number)
        btn_num.pack(side="left", padx=2, pady=2)
        Tooltip(btn_num, "Numbered List (Simple)")

        btn_quote = ttk.Button(self, text=">", width=3, command=self.toggle_indent)
        btn_quote.pack(side="left", padx=2, pady=2)
        Tooltip(btn_quote, "Indent/Quote Block")

        btn_size_down = ttk.Button(self, text="A-", width=3, command=lambda: self.change_font_size(-1))
        btn_size_down.pack(side="left", padx=2, pady=2)
        Tooltip(btn_size_down, "Decrease Font Size")

        btn_size_up = ttk.Button(self, text="A+", width=3, command=lambda: self.change_font_size(1))
        btn_size_up.pack(side="left", padx=2, pady=2)
        Tooltip(btn_size_up, "Increase Font Size")

    def _get_font_at_selection(self):
        """Helper to get the font.Font object at the current selection."""
        try:
            # Get font from the first character of the selection
            font_str = self.text_widget.cget("font")  # Default

            # Check tags at the selection start
            tags_at_sel = self.text_widget.tag_names("sel.first")

            # Find the highest-priority font tag
            for tag in tags_at_sel:
                font_option = self.text_widget.tag_cget(tag, "font")
                if font_option:
                    font_str = font_option

            return font.Font(font=font_str)

        except tk.TclError:
            # No selection, return widget's default font
            return font.Font(font=self.text_widget.cget("font"))

    def _apply_dynamic_tag(self, new_font_config):
        """Applies a dynamically named tag with the new font."""
        # Create a unique tag name, e.g., f_Helvetica_12_bold_italic_underline
        tag_name = (
            f"f_{new_font_config['family'].replace(' ', '_')}"
            f"_{new_font_config['size']}"
            f"_{new_font_config['weight']}"
            f"_{new_font_config['slant']}"
            f"_{new_font_config['underline']}"
        )

        # --- FIX: Remove all other font tags from the selection first ---
        all_tags = self.text_widget.tag_names()
        for tag in all_tags:
            if tag.startswith("f_"):
                self.text_widget.tag_remove(tag, "sel.first", "sel.last")
        # --- END FIX ---

        if tag_name not in self.fonts:
            # Create and cache the font
            self.fonts[tag_name] = font.Font(**new_font_config)
            self.text_widget.tag_configure(tag_name, font=self.fonts[tag_name])

        # Apply the tag
        self.text_widget.tag_add(tag_name, "sel.first", "sel.last")

    def toggle_tag(self, tag_name):
        """Toggles a given style tag on the selected text."""
        # This is for non-font tags
        if tag_name == "highlight":
            try:
                current_tags = self.text_widget.tag_names("sel.first")
                if tag_name in current_tags:
                    self.text_widget.tag_remove(tag_name, "sel.first", "sel.last")
                else:
                    self.text_widget.tag_add(tag_name, "sel.first", "sel.last")
            except tk.TclError:
                pass  # No text selected
            return

        # --- This is for font-style tags (bold, italic, underline) ---
        try:
            sel_ranges = self.text_widget.tag_ranges("sel")
            if not sel_ranges:
                return  # No selection

            current_font = self._get_font_at_selection()
            new_config = current_font.actual()  # Get all properties as a dict

            # Toggle the desired property
            if tag_name == "bold":
                new_config["weight"] = "normal" if new_config["weight"] == "bold" else "bold"
            elif tag_name == "italic":
                new_config["slant"] = "roman" if new_config["slant"] == "italic" else "italic"
            elif tag_name == "underline":
                new_config["underline"] = 0 if new_config["underline"] == 1 else 1

            self._apply_dynamic_tag(new_config)

        except tk.TclError as e:
            print(f"Error toggling tag: {e}")
            pass  # No text selected or other error

    def add_bullet(self):
        """Adds a bullet point at the start of the current line, matching current style."""
        # --- UPDATED METHOD ---
        try:
            line_start = self.text_widget.index("insert linestart")
            current_tags = self.text_widget.tag_names(line_start)

            self.text_widget.insert(line_start, "• ")

            # Re-apply all tags from the start of the line to the new bullet
            for tag in current_tags:
                self.text_widget.tag_add(tag, line_start, f"{line_start} +2c")

        except tk.TclError:
            pass  # No insertion cursor

    def toggle_indent(self):
        """Toggles the 'indent' tag on the current line."""
        try:
            current_tags = self.text_widget.tag_names("insert linestart")
            if "indent" in current_tags:
                self.text_widget.tag_remove("indent", "insert linestart", "insert lineend")
            else:
                self.text_widget.tag_add("indent", "insert linestart", "insert lineend")
        except tk.TclError:
            pass  # No text selected

    def add_number(self):
        """Adds a simple number to the start of the line, matching current style."""
        # --- UPDATED METHOD ---
        try:
            line_start = self.text_widget.index("insert linestart")
            current_tags = self.text_widget.tag_names(line_start)

            self.text_widget.insert(line_start, "1. ")

            # Re-apply all tags from the start of the line to the new number
            for tag in current_tags:
                self.text_widget.tag_add(tag, line_start, f"{line_start} +3c")

        except tk.TclError:
            pass

    # --- UPDATED FONT SIZE FUNCTION ---
    def change_font_size(self, delta):
        """Changes the font size of the selected text, preserving other styles."""
        try:
            sel_ranges = self.text_widget.tag_ranges("sel")
            if not sel_ranges:
                print("Please select text to change font size.")
                return

            current_font = self._get_font_at_selection()
            new_config = current_font.actual()

            # Change the size
            new_size = new_config["size"] + delta
            if new_size < 8: new_size = 8  # Min size
            if new_size > 72: new_size = 72  # Max size
            new_config["size"] = new_size

            self._apply_dynamic_tag(new_config)

        except tk.TclError as e:
            print(f"Error changing font size: {e}")
            pass

    def placeholder(self):
        print("This toolbar button is not yet implemented.")






