import tkinter as tk
# --- FIX: Added Toplevel to the import statement ---
from tkinter import ttk, Listbox, Toplevel


class ReorderDialog(Toplevel):
    def __init__(self, parent, items_to_reorder, current_db_id):
        """
        Create the Toplevel window for reordering.
        :param parent: The parent window
        :param items_to_reorder: List of (text, db_id) tuples
        :param current_db_id: The db_id of the item to pre-select
        """
        super().__init__(parent)
        self.title("Reorder Items")

        self.items_to_reorder = items_to_reorder
        self.ordered_db_ids = None  # This will be set on save

        self.reorder_listbox = Listbox(self, height=10, width=40)
        self.reorder_listbox.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        for item in self.items_to_reorder:
            self.reorder_listbox.insert('end', item[0])  # Insert text

        # Select the item that was originally clicked
        for i, item in enumerate(self.items_to_reorder):
            if item[1] == current_db_id:
                self.reorder_listbox.selection_set(i)
                self.reorder_listbox.activate(i)
                break

        btn_up = ttk.Button(self, text="Move Up", command=self.move_up)
        btn_up.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        btn_down = ttk.Button(self, text="Move Down", command=self.move_down)
        btn_down.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        btn_save = ttk.Button(self, text="Save Order", command=self.on_save)
        btn_save.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.transient(parent)

        # --- ADDED: Center the window ---
        self.center_window()
        # --- END ADD ---

        self.grab_set()

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

    def move_up(self):
        """Move selected item up in the reorder listbox."""
        try:
            idx = self.reorder_listbox.curselection()[0]
            if idx == 0:
                return

            # Move in the listbox UI
            text = self.reorder_listbox.get(idx)
            self.reorder_listbox.delete(idx)
            self.reorder_listbox.insert(idx - 1, text)
            self.reorder_listbox.selection_set(idx - 1)

            # Move in the underlying data list
            item_data = self.items_to_reorder.pop(idx)
            self.items_to_reorder.insert(idx - 1, item_data)
        except IndexError:
            pass  # No item selected

    def move_down(self):
        """Move selected item down in the reorder listbox."""
        try:
            idx = self.reorder_listbox.curselection()[0]
            if idx == self.reorder_listbox.size() - 1:
                return

            # Move in the listbox UI
            text = self.reorder_listbox.get(idx)
            self.reorder_listbox.delete(idx)
            self.reorder_listbox.insert(idx + 1, text)
            self.reorder_listbox.selection_set(idx + 1)

            # Move in the underlying data list
            item_data = self.items_to_reorder.pop(idx)
            self.items_to_reorder.insert(idx + 1, item_data)
        except IndexError:
            pass  # No item selected

    def on_save(self):
        """Save the new order to an attribute and close."""
        self.ordered_db_ids = [item[1] for item in self.items_to_reorder]
        self.destroy()

