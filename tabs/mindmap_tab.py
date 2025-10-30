import tkinter as tk
from tkinter import ttk


class MindmapTab(ttk.Frame):
    """
    This is the placeholder frame for the "Mindmaps" tab.
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
            text="Mindmaps",
            font=("Arial", 18, "bold")
        )
        label_title.pack(pady=10)

        label_placeholder = ttk.Label(
            main_frame,
            text="This tab will contain tools for creating and viewing mindmaps."
        )
        label_placeholder.pack(pady=5)
