import tkinter as tk


class Tooltip:
    """
    Creates a tooltip (pop-up) for a given widget.
    """

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        """Create and show the tooltip window."""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            self.tooltip,
            text=self.text,
            background="#FFFFE0",
            relief="solid",
            borderwidth=1,
            font=("Arial", 9, "normal")
        )
        label.pack()

    def hide_tooltip(self, event):
        """Hide the tooltip window."""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
