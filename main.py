import tkinter as tk
from tkinter import ttk, PhotoImage
import os
from home_screen import HomeScreen
# --- NEW IMPORTS ---
from project_views.project_homepage import open_project_window
from database_manager import DatabaseManager


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Reading Tracker")
        self.geometry("950x600")

        # --- Store base_dir and db on the app itself ---
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db = DatabaseManager()  # One DB manager for the whole app

        self.current_frame = None
        self.current_project_window = None

        # Set the application icon
        icon_path = os.path.join(self.base_dir, "logo.png")
        try:
            img = PhotoImage(file=icon_path)
            # Use iconphoto for cross-platform compatibility
            self.iconphoto(True, img)
        except tk.TclError:
            print(f"Warning: Icon not found at '{icon_path}'. Using default icon.")

        self.center_window()

        # --- NEW: Start by showing the home screen ---
        self.show_home_screen()

    def center_window(self):
        """Centers the main window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    # --- NEW: Main window flow control functions ---

    def show_home_screen(self):
        """Destroys any current frame and shows the home screen."""
        if self.current_frame:
            self.current_frame.destroy()

        if self.current_project_window:
            self.current_project_window.destroy()
            self.current_project_window = None

        self.home_frame = HomeScreen(self, base_dir=self.base_dir, db_manager=self.db)
        self.home_frame.pack(fill="both", expand=True)
        self.current_frame = self.home_frame

        # Show the main window
        self.deiconify()

    def show_project_window(self, project_details):
        """Destroys the home screen and opens a project window."""
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None

        # Hide the root window while project is open
        self.withdraw()

        # open_project_window now creates the Toplevel and returns it
        self.current_project_window = open_project_window(
            self,  # Parent is the app
            project_details,  # Data
            self.base_dir,  # Path
            self.db,  # DB connection
            self.show_home_screen  # Callback function
        )


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()

