import tkinter as tk
from tkinter import ttk, Toplevel, font


class EditInstructionsDialog(Toplevel):
    def __init__(self, parent, current_instructions):
        # ... (existing code) ...
        self.instructions = current_instructions
        self.result = None  # To store the new values

        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        self.text_widgets = {}
        fields = [
            # ... (existing code) ...
            ("unresolved_instr", "Unresolved Questions")
        ]

        for i, (field_key, field_label) in enumerate(fields):
            label = ttk.Label(main_frame, text=field_label)
            label.grid(row=i * 2, column=0, sticky="w", padx=5, pady=(5, 0))

            # --- Enable undo and bind shortcuts ---
            text_widget = tk.Text(main_frame, height=3, width=60, wrap="word", undo=True)
            text_widget.grid(row=i * 2 + 1, column=0, sticky="ew", padx=5, pady=5)
            text_widget.insert("1.0", self.instructions[field_key] or "")  # Handle None
            self.text_widgets[field_key] = text_widget

            # --- NEW: Setup and bind ---
            self.setup_manual_tags(text_widget)
            self.bind_text_shortcuts(text_widget)

        main_frame.columnconfigure(0, weight=1)

        # --- Button Frame ---
        # ... (existing code) ...

        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_btn.grid(row=0, column=1, padx=5, sticky="ew")

        self.center_window()
        self.transient(parent)
        self.grab_set()

    def on_save(self):
        # ... (existing code) ...
        self.destroy()

    def center_window(self):
        # ... (existing code) ...
        self.geometry(f'{width}x{height}+{x}+{y}')

    # --- NEW: Text formatting and shortcut functions ---

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

        text_widget.bind("<Control-b>", self.on_ctrl_b)
        text_widget.bind("<Control-i>", self.on_ctrl_i)
        text_widget.bind("<Control-u>", self.on_ctrl_u)

    def delete_word_backward(self, text_widget):
        """Deletes the word immediately behind the cursor."""
        try:
            delete_start = text_widget.index("insert wordstart")
            if delete_start == text_widget.index("insert"):
                delete_start = text_widget.index("insert-1c wordstart")
            text_widget.delete(delete_start, "insert")
        except tk.TclError:
            pass
        return "break"

    def delete_word_forward(self, text_widget):
        """Deletes the word immediately in front of the cursor."""
        try:
            delete_end = text_widget.index("insert wordend")
            if delete_end == text_widget.index("insert"):
                delete_end = text_widget.index("insert+1c wordend")
            text_widget.delete("insert", delete_end)
        except tk.TclError:
            pass
        return "break"

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

    # --- NEW: Dynamic font toggling functions ---

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

        # --- FIX: Remove all other font tags from the selection first ---
        all_tags = text_widget.tag_names()
        for tag in all_tags:
            if tag.startswith("f_"):
                text_widget.tag_remove(tag, "sel.first", "sel.last")
        # --- END FIX ---

        if not hasattr(text_widget, 'font_cache'):
            text_widget.font_cache = {}

        if tag_name not in text_widget.font_cache:
            text_widget.font_cache[tag_name] = font.Font(**new_font_config)
            text_widget.tag_configure(tag_name, font=text_widget.font_cache[tag_name])

        text_widget.tag_add(tag_name, "sel.first", "sel.last")

    def toggle_tag_manual(self, text_widget, tag_name):
        """Manually toggles a font style on a widget."""
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

    def on_ctrl_b(self, event):
        self.toggle_tag_manual(event.widget, "bold")
        return "break"

    def on_ctrl_i(self, event):
        self.toggle_tag_manual(event.widget, "italic")
        return "break"

    def on_ctrl_u(self, event):
        self.toggle_tag_manual(event.widget, "underline")
        return "break"
    # --- END NEW ---




