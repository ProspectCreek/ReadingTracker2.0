import tkinter as tk
from tkinter import ttk, Toplevel


class MoveProjectDialog(Toplevel):
    def __init__(self, parent, all_classes):
        super().__init__(parent)
        self.title("Move Project")
        self.parent = parent
        self.all_classes = all_classes
        self.new_parent_id = None  # This will store the result

        self.create_widgets()
        self.center_window()

        self.transient(parent)
        self.grab_set()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10 10 10 10")
        main_frame.pack(fill='both', expand=True)

        label = ttk.Label(main_frame, text="Move this project to:")
        label.pack(pady=5)

        # Create a list of class names and their IDs
        # We add "Standalone Project" as the first option
        self.class_options = {"Standalone Project (Root)": None}
        for class_item in self.all_classes:
            self.class_options[class_item['name']] = class_item['id']

        # Combobox for class selection
        self.class_combo = ttk.Combobox(
            main_frame,
            values=list(self.class_options.keys()),
            state="readonly",
            # --- UPDATED WIDTH ---
            width=40
        )
        self.class_combo.pack(padx=5, pady=5, fill='x', expand=True)
        self.class_combo.current(0)  # Default to "Standalone"

        # --- Button Frame ---
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        move_btn = ttk.Button(button_frame, text="Move", command=self.on_move)
        move_btn.grid(row=0, column=0, padx=5, sticky="ew")

        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_btn.grid(row=0, column=1, padx=5, sticky="ew")

    def on_move(self):
        """Set the resulting parent ID and close the dialog."""
        selected_name = self.class_combo.get()
        self.new_parent_id = self.class_options.get(selected_name)
        self.destroy()

    def center_window(self):
        """Centers the dialog on the parent window."""
        self.update_idletasks()

        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_w = self.parent.winfo_width()
        parent_h = self.parent.winfo_height()

        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()

        x = parent_x + (parent_w // 2) - (width // 2)
        y = parent_y + (parent_h // 2) - (height // 2)

        self.geometry(f'{width}x{height}+{x}+{y}')


