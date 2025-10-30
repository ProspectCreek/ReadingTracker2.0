import tkinter as tk
from tkinter import ttk


class AssignmentTab(ttk.Frame):
    """
    This is the placeholder frame for the "Assignment" tab.
    It only appears if the project is marked as an assignment.
    """

    def __init__(self, parent, project_details):
        super().__init__(parent)

        self.project_details = project_details

        # Configure grid for this frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Placeholder Content ---
        main_frame = ttk.Frame(self)
        main_frame.grid(sticky="nsew", padx=10, pady=10)

        label_title = ttk.Label(
            main_frame,
            text="Assignment Details",
            font=("Arial", 18, "bold")
        )
        label_title.pack(pady=10)

        label_placeholder = ttk.Label(
            main_frame,
            text="This tab will hold assignment-specific details like due dates, "
                 "rubrics, and submission status."
        )
        label_placeholder.pack(pady=5)
