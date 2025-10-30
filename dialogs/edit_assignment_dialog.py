import tkinter as tk
from tkinter import ttk, Toplevel


class EditAssignmentDialog(Toplevel):
    def __init__(self, parent, current_status):
        super().__init__(parent)
        self.title("Edit Assignment Status")
        self.parent = parent

        # This will store the result (1 for Yes, 0 for No)
        self.new_status = tk.IntVar(value=current_status)

        main_frame = ttk.Frame(self, padding="10 10 10 10")
        main_frame.pack(fill='both', expand=True)

        label = ttk.Label(main_frame, text="Is this project for an assignment?")
        label.pack(pady=5, anchor='w')

        # --- Radio Button Frame ---
        radio_frame = ttk.Frame(main_frame)
        radio_frame.pack(fill='x', padx=10, pady=5)

        yes_rb = ttk.Radiobutton(radio_frame, text="Yes", variable=self.new_status, value=1)
        yes_rb.pack(side='left', padx=5)

        no_rb = ttk.Radiobutton(radio_frame, text="No", variable=self.new_status, value=0)
        no_rb.pack(side='left', padx=5)

        # --- Button Frame ---
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        save_btn = ttk.Button(button_frame, text="Save", command=self.on_save)
        save_btn.grid(row=0, column=0, padx=5, sticky="ew")

        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_btn.grid(row=0, column=1, padx=5, sticky="ew")

        self.center_window()
        self.transient(parent)
        self.grab_set()

    def on_save(self):
        """Close the dialog (the value is already set by the tk.IntVar)."""
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
