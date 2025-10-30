import tkinter as tk
from tkinter import ttk, messagebox, Menu

# --- FIX: Add project root to sys.path ---
import sys
import os
# --- NEW IMPORTS ---
from PIL import Image, ImageTk

# Get the absolute path to this file (project_homepage.py)
file_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (the project root)
project_root = os.path.dirname(file_dir)
# Add the project root to the system path
if project_root not in sys.path:
    sys.path.append(project_root)
# --- END FIX ---

# Import the new tab classes (this will now work)
from tabs.project_dashboard_tab import ProjectDashboardTab
from tabs.mindmap_tab import MindmapTab
from tabs.assignment_tab import AssignmentTab
from database_manager import DatabaseManager
from dialogs.edit_instructions_dialog import EditInstructionsDialog


class ProjectWindow(tk.Toplevel):
    """
    Main Toplevel window for an individual project.
    It contains the tabbed notebook interface.
    """

    # --- UPDATED __init__ to accept db_manager and on_close_callback ---
    def __init__(self, parent, project_details, base_dir, db_manager, on_close_callback):
        super().__init__(parent)
        self.parent = parent
        self.project_details = project_details
        self.base_dir = base_dir
        self.db = db_manager  # Store the database manager instance
        self.logo_render = None  # To hold logo image reference

        # --- NEW: Store the callback function ---
        self.on_close_callback = on_close_callback

        # --- NEW: Handle window close (X button) ---
        self.protocol("WM_DELETE_WINDOW", self.on_return_to_dashboard)

        # --- (6) Settings Menu ---
        self.menubar = Menu(self)
        self.config(menu=self.menubar)

        settings_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(
            label="Edit Project Homepage Instructions",
            command=self.open_edit_instructions_dialog
        )
        # --- END Settings Menu ---

        self.title(f"Project: {self.project_details['name']}")

        # --- Maximize the window ---
        try:
            self.state('zoomed')
        except tk.TclError:
            width = self.winfo_screenwidth()
            height = self.winfo_screenheight()
            self.geometry(f"{width}x{height}+0+0")

        # --- Main Layout ---
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # --- (1) Top Button Bar ---
        # --- THIS IS THE FIX: Define button_bar_frame ---
        button_bar_frame = ttk.Frame(main_frame)
        button_bar_frame.grid(row=0, column=0, sticky="ew")

        # --- (1a) "Return to Main Dashboard" Button ---
        btn_return = ttk.Button(
            button_bar_frame,
            text="Return to Main Dashboard",
            command=self.on_return_to_dashboard  # --- UPDATED command
        )
        btn_return.pack(side="left", padx=10, pady=5)

        # --- (1b) "Add Reading" Button ---
        btn_add_reading = ttk.Button(
            button_bar_frame,
            text="Add Reading",
            command=self.add_reading_placeholder
        )
        btn_add_reading.pack(side="left", padx=10, pady=5)

        # --- Content Frame (Tabs + Logo) ---
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)  # Tabs expand
        content_frame.grid_columnconfigure(1, weight=0)  # Logo does not
        content_frame.grid_rowconfigure(0, weight=1)

        # --- (3) Tab Notebook ---
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # --- NEW: Style for wider tabs ---
        style = ttk.Style(self)
        style.configure("TNotebook.Tab", padding=[20, 5])
        # --- END NEW ---

        # --- (2) Logo on the right ---
        logo_frame = ttk.Frame(content_frame, width=150)
        logo_frame.grid(row=0, column=1, sticky="ns", pady=5)
        logo_frame.pack_propagate(False)  # Prevent frame from shrinking

        try:
            icon_path = os.path.join(self.base_dir, "logo.png")
            load = Image.open(icon_path)
            load = load.resize((128, 128), Image.Resampling.LANCZOS)
            self.logo_render = ImageTk.PhotoImage(load)
            img_label = ttk.Label(logo_frame, image=self.logo_render, anchor="n")
            img_label.pack(pady=20)
        except Exception as e:
            print(f"Error loading logo in project window: {e}")
            ttk.Label(logo_frame, text="Logo\nError", anchor="n").pack()

        # --- Tab 1: Project Dashboard (Permanent) ---
        # Pass the db manager to the tab
        self.dashboard_tab = ProjectDashboardTab(self.notebook, self.project_details, self.db)
        self.notebook.add(self.dashboard_tab, text="Project Dashboard")

        # --- Tab 2: Mindmaps (Permanent) ---
        self.mindmap_tab = MindmapTab(self.notebook, self.project_details)
        self.notebook.add(self.mindmap_tab, text="Mindmaps")

        # --- Tab 3: Assignment (Conditional) ---
        if self.project_details['is_assignment'] == 1:
            self.assignment_tab = AssignmentTab(self.notebook, self.project_details)
            self.notebook.add(self.assignment_tab, text="Assignment")

        # Make sure the window gets focus
        self.grab_set()
        self.focus_set()

    # --- UPDATED: This function now calls the callback ---
    def on_return_to_dashboard(self):
        """
        Saves any pending data (optional) and
        calls the callback to show the home screen.
        """
        # NOTE: Add any "auto-save" logic here if needed

        # Call the callback function provided by MainApplication
        self.on_close_callback()

        # Destroy this project window
        self.destroy()

    def add_reading_placeholder(self):
        """Placeholder for the 'Add Reading' button."""
        messagebox.showinfo(
            "Add Reading",
            "This will open the 'Add Reading' dialog for this project."
        )

    # --- NEW FUNCTION for Settings Menu ---
    def open_edit_instructions_dialog(self):
        """Opens the dialog to edit dashboard instructions."""
        project_id = self.project_details['id']
        current_instructions = self.db.get_or_create_instructions(project_id)

        dialog = EditInstructionsDialog(self, current_instructions)
        self.wait_window(dialog)

        if dialog.result:
            self.db.update_instructions(
                project_id,
                dialog.result['key_questions_instr'],
                dialog.result['thesis_instr'],
                dialog.result['insights_instr'],
                dialog.result['unresolved_instr']
            )
            # Notify the dashboard tab to update its instructions
            self.dashboard_tab.refresh_instructions()
            messagebox.showinfo("Success", "Instructions have been updated.")
    # --- END NEW FUNCTION ---


def open_project_window(parent, project_details, base_dir, db_manager, on_close_callback):
    """
    Opens the new, maximized Toplevel window for a specific project.

    :param parent: The parent window (MainApplication)
    :param project_details: A database row (dict-like) with all project info
    :param base_dir: The application's base directory
    :param db_manager: The shared DatabaseManager instance
    :param on_close_callback: The function to call when this window closes
    """

    # Create the main project window instance
    # --- UPDATED: Pass all required arguments ---
    project_win = ProjectWindow(
        parent,
        project_details,
        base_dir,
        db_manager,
        on_close_callback
    )

    # --- NEW: Return the window instance to the caller ---
    return project_win

