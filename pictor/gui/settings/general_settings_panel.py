"""
General Settings Panel for Pictor Settings Window
"""
import tkinter as tk
from tkinter import ttk

class GeneralSettingsPanel(tk.Frame):
    """A frame that contains the general settings controls."""
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg='#f0f0f0', **kwargs)
        self.app = app
        self.build_ui()

    def build_ui(self):
        """Create the general settings UI."""
        # Create title
        title_label = tk.Label(
            self,
            text="General Settings",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0'
        )
        title_label.pack(pady=(20, 10))

        # Description
        desc_label = tk.Label(
            self,
            text="Configure general application settings",
            font=('Arial', 10),
            bg='#f0f0f0',
            fg='#666666'
        )
        desc_label.pack(pady=(0, 20))

        # Settings container
        settings_container = tk.Frame(self, bg='#f0f0f0')
        settings_container.pack(fill='both', expand=True, padx=20)

        # Always on Top setting
        always_on_top_frame = tk.Frame(settings_container, bg='#f0f0f0')
        always_on_top_frame.pack(fill='x', pady=10)

        always_on_top_cb = tk.Checkbutton(
            always_on_top_frame,
            text="Always on Top",
            variable=self.app.always_on_top_var,
            command=self.on_always_on_top_changed,
            font=('Arial', 11),
            bg='#f0f0f0'
        )
        always_on_top_cb.pack(anchor='w')

        # Description for always on top
        tk.Label(
            always_on_top_frame,
            text="Keep the application window above all other windows",
            font=('Arial', 9),
            bg='#f0f0f0',
            fg='#666666'
        ).pack(anchor='w', padx=(25, 0))

    def on_always_on_top_changed(self):
        """Handle always on top checkbox changes."""
        if hasattr(self.app, 'root'):
            self.app.root.attributes('-topmost', self.app.always_on_top_var.get())
