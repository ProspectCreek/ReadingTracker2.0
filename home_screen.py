import tkinter as tk
from tkinter import ttk, simpledialog, Toplevel, Listbox, messagebox
from PIL import Image, ImageTk
import os

from database_manager import DatabaseManager
# --- UPDATED IMPORT ---
# We no longer call this directly, but we need the class for type hints (optional)
# from project_views.project_homepage import open_project_window
from dialogs.create_item_dialog import CreateItemDialog
from dialogs.reorder_dialog import ReorderDialog
from dialogs.move_project_dialog import MoveProjectDialog
from dialogs.rename_dialog import RenameDialog
from dialogs.edit_assignment_dialog import EditAssignmentDialog


class HomeScreen(ttk.Frame):
    # --- UPDATED __init__ ---
    # It now receives the db_manager from MainApplication
    def __init__(self, parent, base_dir, db_manager):
        super().__init__(parent)
        self.db = db_manager  # Use the passed-in db manager
        self.base_dir = base_dir
        self.selected_item_id = None
        self.expanded_ids = set()  # For restoring tree state

        # --- NEW: Store the app root ---
        self.app_root = parent

        self.create_widgets()
        self.load_data_to_tree()

    def create_widgets(self):
        # Configure grid
        self.grid_columnconfigure(0, weight=4)  # Treeview column
        self.grid_columnconfigure(1, weight=1)  # Icon column
        self.grid_rowconfigure(0, weight=1)

        # --- Left Side: Treeview ---
        left_frame = ttk.LabelFrame(self, text="My Projects and Classes")
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        left_frame.grid_rowconfigure(0, weight=1)  # Treeview
        left_frame.grid_rowconfigure(1, weight=0)  # Buttons
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_columnconfigure(1, weight=0)  # Scrollbar

        # The Treeview
        self.tree = ttk.Treeview(left_frame, columns=("db_id",), displaycolumns=())
        self.tree.heading("#0", text="Name")
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # --- Button Frame ---
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        btn_add_project = ttk.Button(
            button_frame,
            text="Add Project",
            command=lambda: self.handle_create_item('project', from_button=True)
        )
        btn_add_project.grid(row=0, column=0, padx=(0, 2), sticky="ew")

        btn_add_class = ttk.Button(
            button_frame,
            text="Add Class",
            command=lambda: self.handle_create_item('class', from_button=True)
        )
        btn_add_class.grid(row=0, column=1, padx=(2, 0), sticky="ew")

        # --- NEW Connections Button ---
        btn_connections = ttk.Button(
            button_frame,
            text="Connections",
            command=self.open_connections_window
        )
        # Place it on the row below the other buttons, spanning both columns
        btn_connections.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky="ew")
        # --- END NEW Button ---

        # --- Right Side: Icon ---
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        try:
            icon_path = os.path.join(self.base_dir, "logo.png")
            load = Image.open(icon_path)

            # --- Resize based on your uploaded file ---
            load = load.resize((500, 500), Image.Resampling.LANCZOS)

            self.render = ImageTk.PhotoImage(load)
            img_label = ttk.Label(right_frame, image=self.render, anchor="center")
            img_label.grid(row=0, column=0, sticky="nsew")

        except FileNotFoundError:
            error_msg = f"logo.png not found.\nAttempted path:\n{icon_path}"
            error_label = ttk.Label(right_frame, text=error_msg, anchor="center", justify='center')
            error_label.grid(row=0, column=0, sticky="nsew")
        except Exception as e:
            print(f"Error loading icon: {e}")
            error_label = ttk.Label(right_frame, text=f"Error loading icon:\n{e}", anchor="center")
            error_label.grid(row=0, column=0, sticky="nsew")

        # --- Bindings ---
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.on_double_click)

    def load_data_to_tree(self):
        """Clear and reload all items from the database into the tree."""
        # --- Save expanded state ---
        expanded_ids = set()
        if hasattr(self, 'tree'):  # Check if tree exists
            self._find_expanded_children(self.tree.get_children(), expanded_ids)

        for item in self.tree.get_children():
            self.tree.delete(item)

        self._load_children(parent_iid='', parent_db_id=None, expanded_ids=expanded_ids)

        # Restore expanded state
        for iid in self.tree.get_children():
            self._restore_expanded_state(iid, expanded_ids)

    def _find_expanded_children(self, iids, expanded_set):
        """Recursively find all expanded items and add their DB ID to the set."""
        for iid in iids:
            if self.tree.item(iid, 'open'):
                try:
                    db_id = self.tree.item(iid, 'values')[0]
                    # Ensure db_id is an integer for correct comparison
                    expanded_set.add(int(db_id))
                except (IndexError, TypeError, ValueError):
                    # This could happen if values are not set (e.g., mid-update)
                    pass
                    # Recurse even if parent isn't open, to find nested open items
            self._find_expanded_children(self.tree.get_children(iid), expanded_set)

    def _restore_expanded_state(self, iid, expanded_ids):
        """Recursively restore expanded state based on the set of DB IDs."""
        try:
            db_id = self.tree.item(iid, 'values')[0]
            if int(db_id) in expanded_ids:
                self.tree.item(iid, open=True)
        except (IndexError, TypeError, ValueError):
            pass  # Should not happen, but safeguard

        for child_iid in self.tree.get_children(iid):
            self._restore_expanded_state(child_iid, expanded_ids)

    def _load_children(self, parent_iid, parent_db_id, expanded_ids):  # Added expanded_ids
        """Recursive helper function to load items."""
        items = self.db.get_items(parent_db_id)
        for item in items:
            item_iid = self.tree.insert(
                parent_iid,
                'end',
                text=item['name'],
                values=(item['id'],),
                tags=(item['type'],)
            )
            if item['type'] == 'class':
                # Pass the set in the recursive call
                self._load_children(
                    parent_iid=item_iid,
                    parent_db_id=item['id'],
                    expanded_ids=expanded_ids  # Pass it down
                )

    def show_context_menu(self, event):
        """Display the right-click context menu."""
        self.selected_item_id = self.tree.identify_row(event.y)

        menu = tk.Menu(self.tree, tearoff=0)

        if self.selected_item_id:
            self.tree.selection_set(self.selected_item_id)
            # Get item details from DB
            db_id_val = self.tree.item(self.selected_item_id, 'values')
            if not db_id_val:
                return  # Clicked on an item that is somehow invalid

            try:
                db_id = int(db_id_val[0])
            except (ValueError, TypeError):
                return  # Invalid item ID

            item_details = self.db.get_item_details(db_id)
            if not item_details:
                return  # Item not in DB?

            item_type = item_details['type']
            is_root_item = item_details['parent_id'] is None

            menu.add_command(label="Rename", command=self.rename_item)
            menu.add_command(label="Delete", command=self.delete_item)
            menu.add_command(label="Duplicate", command=self.duplicate_item)
            menu.add_separator()

            if item_type == 'class':
                menu.add_command(label="Add New Project (in class)",
                                 command=lambda: self.handle_create_item('project', from_button=False))

            if item_type == 'project':
                menu.add_command(label="Move Project", command=self.move_project)
                menu.add_command(label="Edit Assignment Status", command=self.edit_assignment_status)

        else:
            # Clicked on blank space
            menu.add_command(label="Add New Project (Standalone)",
                             command=lambda: self.handle_create_item('project', from_button=True))
            menu.add_command(label="Add New Class (Standalone)",
                             command=lambda: self.handle_create_item('class', from_button=True))

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def on_double_click(self, event):
        """Handle double-click event to open a project."""
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        tags = self.tree.item(item_id, 'tags')
        if 'project' in tags:
            db_id = self.tree.item(item_id, 'values')[0]
            project_details = self.db.get_item_details(db_id)
            if project_details:
                # --- UPDATED: Tell the MainApplication to handle the window swap ---
                self.app_root.show_project_window(project_details)
            else:
                messagebox.showerror("Error", f"Could not load project with ID {db_id}")

    # --- UPDATED: Dialog Handler Methods ---

    def handle_create_item(self, item_type, from_button=False):
        """Central handler for creating a new project or class."""
        parent_db_id = None

        # If not from a button, it's from a right-click.
        # Check if a class is selected to be the parent.
        if not from_button and self.selected_item_id:
            db_id_val = self.tree.item(self.selected_item_id, 'values')
            if db_id_val:
                db_id = int(db_id_val[0])
                item_details = self.db.get_item_details(db_id)
                if item_details and item_details['type'] == 'class':
                    parent_db_id = item_details['id']

        # Open the custom dialog
        dialog = CreateItemDialog(self, item_type, parent_db_id=parent_db_id)
        # This blocks until the dialog is closed
        self.wait_window(dialog)

        # After dialog is closed, check if it has a 'result'
        if hasattr(dialog, 'result') and dialog.result:
            name = dialog.result['name']
            is_assignment = dialog.result['is_assignment']

            self.db.create_item(name, item_type, parent_db_id, is_assignment)
            self.load_data_to_tree()  # Refresh the tree

    def handle_create_item(self, item_type, from_button=False):
        # --- UPDATED: Call app's db ---
        item_details = self.db.get_item_details(db_id)
        current_status = item_details['is_assignment']

        db_id = self.tree.item(self.selected_item_id, 'values')[0]
        old_name = self.tree.item(self.selected_item_id, 'text')

        dialog = RenameDialog(self, old_name)
        self.wait_window(dialog)  # Wait for the dialog to close

        # The dialog sets its 'new_name' attribute if Save was clicked
        if hasattr(dialog, 'new_name') and dialog.new_name:
            if dialog.new_name != old_name:
                self.db.rename_item(db_id, dialog.new_name)
                self.load_data_to_tree()

    # --- NEW METHODS ---

    def delete_item(self):
        """Delete the selected item with confirmation."""
        if not self.selected_item_id:
            return

        db_id_val = self.tree.item(self.selected_item_id, 'values')
        if not db_id_val: return

        db_id = int(db_id_val[0])
        item_details = self.db.get_item_details(db_id)
        if not item_details:
            messagebox.showerror("Error", "Could not find item details.")
            return

        item_type = item_details['type']
        item_name = item_details['name']

        # --- Confirmation ---
        if item_type == 'class':
            msg = f"Are you sure you want to delete the class '{item_name}'?\n\n" \
                  "ALL projects inside this class will also be permanently deleted."
            if not messagebox.askyesno("Delete Class?", msg):
                return
        else:
            msg = f"Are you sure you want to delete the project '{item_name}'?"
            if not messagebox.askyesno("Delete Project?", msg):
                return

        self.db.delete_item(db_id)
        self.load_data_to_tree()

    def duplicate_item(self):
        """Duplicate the selected item."""
        if not self.selected_item_id:
            return

        db_id_val = self.tree.item(self.selected_item_id, 'values')
        if not db_id_val: return

        db_id = int(db_id_val[0])
        self.db.duplicate_item(db_id)
        self.load_data_to_tree()

    def move_project(self):
        """Move the selected project to a new parent (or root)."""
        if not self.selected_item_id:
            return

        db_id_val = self.tree.item(self.selected_item_id, 'values')
        if not db_id_val: return

        db_id = int(db_id_val[0])

        # Find all classes for the "Move" dialog
        all_classes = self.db.get_all_classes()

        dialog = MoveProjectDialog(self, all_classes)
        self.wait_window(dialog)

        # The dialog sets 'new_parent_id' (could be None for root)
        if hasattr(dialog, 'new_parent_id'):
            # Only move if the ID is different
            current_parent = self.db.get_item_details(db_id)['parent_id']
            if dialog.new_parent_id != current_parent:
                self.db.move_item(db_id, dialog.new_parent_id)
                self.load_data_to_tree()

    def edit_assignment_status(self):
        """Open the dialog to edit the 'is_assignment' status of a project."""
        if not self.selected_item_id:
            return

        db_id_val = self.tree.item(self.selected_item_id, 'values')
        if not db_id_val: return

        db_id = int(db_id_val[0])

        # Get the current status from the database
        item_details = self.db.get_item_details(db_id)
        if not item_details:
            messagebox.showerror("Error", "Could not find item details.")
            return

        # Default to 1 (Yes) if status is somehow missing
        current_status = item_details['is_assignment'] if item_details['is_assignment'] is not None else 1

        # Open the dialog
        dialog = EditAssignmentDialog(self, current_status)
        self.wait_window(dialog)

        # Check for a result and update the database if it's different
        if hasattr(dialog, 'new_status'):
            new_status_val = dialog.new_status.get()
            if new_status_val != current_status:
                # Show warning if changing from Yes to No
                if current_status == 1 and new_status_val == 0:
                    if not messagebox.askyesno("Warning",
                                               "By selecting no, the existing assignment in the project will be deleted permanently.\nAre you sure you want to continue?"):
                        return  # User cancelled

                # --- UPDATED: Call app's db ---
                self.db.update_assignment_status(db_id, new_status_val)
                print(f"Updated assignment status for item {db_id} to {new_status_val}")

    def connections_placeholder(self):
        self.db.update_assignment_status(db_id, new_status)
        # No tree reload is needed since this data isn't visible
        print(f"Updated assignment status for item {db_id} to {new_status}")

    # --- NEW PLACEHOLDER METHOD ---
    def open_connections_window(self):
        """Placeholder for opening the connections management window."""
        print("Opening connections window (placeholder)...")
        messagebox.showinfo(
            "Connections",
            "This feature is not yet implemented.\n\n"
            "This will open the connections management window."
        )





