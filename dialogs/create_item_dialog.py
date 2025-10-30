import tkinter as tk
# --- FIX: Added Toplevel to the import statement ---
from tkinter import ttk, Toplevel


class CreateItemDialog(Toplevel):
    def __init__(self, parent, item_type):
        super().__init__(parent)
        self.title(f"Create New {item_type.capitalize()}")

        self.item_type = item_type
        self.name = ""
        self.is_assignment = 1  # Default

        main_frame = ttk.Frame(self, padding="10 10 10 10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Name Entry
        name_label = ttk.Label(main_frame, text=f"Enter {item_type} name:")
        name_label.grid(row=0, column=0, columnspan=2, sticky="w")

        self.name_entry = ttk.Entry(main_frame, width=50)  # Wider entry
        self.name_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

        # --- Conditional Radio Buttons ---
        if self.item_type == 'project':
            # Assignment Radio Buttons
            self.assignment_var = tk.IntVar(value=1)  # Default to Yes (1)

            assign_label = ttk.Label(main_frame, text="For assignment:")
            assign_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))

            radio_frame = ttk.Frame(main_frame)
            radio_frame.grid(row=3, column=0, columnspan=2, sticky="w", padx=10)

            yes_radio = ttk.Radiobutton(
                radio_frame,
                text="Yes",
                variable=self.assignment_var,
                value=1
            )
            yes_radio.pack(side="left", padx=5)

            no_radio = ttk.Radiobutton(
                radio_frame,
                text="No",
                variable=self.assignment_var,
                value=0
            )
            no_radio.pack(side="left", padx=5)

            # Save Button
            save_btn = ttk.Button(
                main_frame,
                text="Save",
                command=self.on_save
            )
            save_btn.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(15, 0))

        else:  # item_type is 'class'
            self.is_assignment = 0  # Classes are not assignments
            # Save Button (no radio buttons)
            save_btn = ttk.Button(
                main_frame,
                text="Save",
                command=self.on_save
            )
            # Place button at row 2, since there are no radio buttons
            save_btn.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(15, 0))
        # --- End of update ---

        self.transient(parent)

        # --- ADDED: Center the window ---
        self.center_window()
        # --- END ADD ---

        self.grab_set()
        self.name_entry.focus_set()  # Focus the entry box

    def center_window(self):
        """Centers the Toplevel window on the screen."""
        self.update_idletasks()  # Wait for window to be drawn

        # Get window size
        width = self.winfo_width()
        height = self.winfo_height()

        # Get screen size
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate coordinates
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.geometry(f'{width}x{height}+{x}+{y}')

    def on_save(self):
        """Saves the data and closes the dialog."""
        name = self.name_entry.get()
        if not name:
            # You could show an error message here
            return

        self.name = name
        if self.item_type == 'project':
            self.is_assignment = self.assignment_var.get()

        self.destroy()  # Close the dialog

