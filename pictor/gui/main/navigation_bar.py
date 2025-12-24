import tkinter as tk
from typing import Optional


class NavigationBar:
    """Navigation bar component for the main window"""

    def __init__(self, parent, show_frame_callback, on_recent_changes, on_dev_tools, on_open_settings):
        self.parent = parent
        self.show_frame_callback = show_frame_callback
        self.on_recent_changes = on_recent_changes
        self.on_dev_tools = on_dev_tools
        self.on_open_settings = on_open_settings

        self.nav_frame: Optional[tk.Frame] = None
        self.main_nav_btn: Optional[tk.Button] = None
        self.recent_changes_btn: Optional[tk.Button] = None
        self.dev_tools_btn: Optional[tk.Button] = None
        self.settings_btn: Optional[tk.Button] = None

        self.setup_navigation()

    def setup_navigation(self):
        """Create the navigation bar at the top"""
        self.nav_frame = tk.Frame(self.parent, bg='#d0d0d0', height=40)
        self.nav_frame.pack(fill='x', side='top')
        self.nav_frame.pack_propagate(False)

        # Navigation buttons
        nav_buttons_frame = tk.Frame(self.nav_frame, bg='#d0d0d0')
        nav_buttons_frame.pack(side='left', padx=10, pady=5)

        self.main_nav_btn = tk.Button(
            nav_buttons_frame,
            text="Main",
            command=lambda: self.show_frame_callback('main'),
            relief='flat',
            bg='#4CAF50',
            fg='white',
            padx=15
        )
        self.main_nav_btn.pack(side='left', padx=2)

        # Recent Changes button next to Main
        self.recent_changes_btn = tk.Button(
            nav_buttons_frame,
            text="Recent Changes",
            command=self.on_recent_changes,
            relief='flat',
            bg='#e0e0e0',
            fg='black',
            padx=15
        )
        self.recent_changes_btn.pack(side='left', padx=2)

        # Dev Tools button next to Recent Changes
        self.dev_tools_btn = tk.Button(
            nav_buttons_frame,
            text="Dev Tools",
            command=self.on_dev_tools,
            relief='flat',
            bg='#e0e0e0',
            fg='black',
            padx=15
        )
        self.dev_tools_btn.pack(side='left', padx=2)

        # Right side controls (settings)
        right_nav_frame = tk.Frame(self.nav_frame, bg='#d0d0d0')
        right_nav_frame.pack(side='right', padx=10, pady=5)

        # Settings button (wrench icon opens settings)
        self.settings_btn = tk.Button(
            right_nav_frame,
            text="🔧",
            command=self.on_open_settings,
            font=('Arial', 12),
            width=3,
            relief='raised'
        )
        self.settings_btn.pack(side='right', padx=5)

    def update_nav_buttons(self, active_frame):
        """Update navigation button visual states"""
        # Only 'main' frame has a navigation button now
        if active_frame == 'main':
            self.main_nav_btn.config(bg='#4CAF50', fg='white')  # type: ignore
        else:
            self.main_nav_btn.config(bg='#e0e0e0', fg='black')  # type: ignore