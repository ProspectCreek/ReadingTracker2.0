import tkinter as tk
from tkinter import ttk, Toplevel


class RenameDialog(Toplevel):
    def __init__(self, parent, old_name):
        super().__init__(parent)
        self.title("Rename Item")
        self.parent = parent
        self.new_name = None  # This will store the result

        main_frame = ttk.Frame(self, padding="10 10 10 10")
        main_frame.pack(fill='both', expand=True)

        label = ttk.Label(main_frame, text="Enter new name:")
        label.pack(pady=5)

        self.name_entry = ttk.Entry(main_frame, width=50)  # Wider entry box
        self.name_entry.pack(padx=5, pady=5, fill='x', expand=True)
        self.name_entry.insert(0, old_name)
        self.name_entry.focus_set()
        self.name_entry.select_range(0, 'end')

        # --- Button Frame ---
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        save_btn = ttk.Button(button_frame, text="Save", command=self.on_save)
        save_btn.grid(row=0, column=0, padx=5, sticky="ew")

        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_btn.grid(row=0, column=1, padx=5, sticky="ew")

        # Bind Enter key to save
        self.bind("<Return>", self.on_save)

        self.center_window()
        self.transient(parent)
        self.grab_set()

    def on_save(self, event=None):
        self.new_name = self.name_entry.get()
        if self.new_name:  # Only set if not empty
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
