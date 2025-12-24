import tkinter as tk
from tkinter import ttk, messagebox
from .capture_settings import CaptureSettingsWindow
from pictor.gui import WordMatcherWindow
from pictor.gui.settings.general_settings_panel import GeneralSettingsPanel
from pictor.gui.settings.wordbank_settings_panel import WordbankSettingsPanel
from pictor.gui.settings.capture_settings_panel import CaptureSettingsPanel

class SettingsWindow:
    """Consolidated settings window with tabbed interface"""
    
    def __init__(self, app, tk_parent, embedded=False):
        # app: main WordMatcher instance (for logic), tk_parent: Tk root for window or parent frame
        self.app = app
        self.tk_parent = tk_parent
        self.embedded = embedded
        
        if embedded:
            # Use the provided frame as the container
            self.window = tk_parent
        else:
            # Create a new window
            self.window = tk.Toplevel(tk_parent)
            self.window.title("Settings")
            self.window.geometry("600x500")
            self.window.minsize(600, 500)
            self.window.configure(bg='#f0f0f0')
            self.window.resizable(True, True)
            
            # Make it modal
            self.window.transient(self.tk_parent)
            self.window.grab_set()
            
            # Center the window
            self.center_window()
        
        # Current active panel
        self.active_panel = None
        
        # Initialize capture settings state variables (mirroring CaptureSettingsWindow)
        self.monitoring = False
        self.coordinates = None
        self.selection_history = []
        self.history_index = -1
        self._canvas_info = {}
        self.select_mode = False
        
        # UI state variables for capture settings
        self.window_var = tk.StringVar()
        self.window_dropdown = None
        self.priority_var = tk.StringVar(value="Match title")
        self.rate_var = tk.DoubleVar(value=1.0)
        self.monitor_btn = None
        self.select_area_btn = None
        self.coords_label = None
        self.preview_canvas = None
        self.refresh_btn = None
        self.rate_scale = None
        
        self.setup_ui()
        # Show general settings by default
        self.show_general_settings()
        # Bind Ctrl+R to restart app in settings window
        self.window.bind('<Control-r>', lambda e: self.on_restart_app())
        self.window.bind('<Control-R>', lambda e: self.on_restart_app())

    def on_restart_app(self, event=None):
        """Restart the application and close all windows (main and settings)"""
        import subprocess, sys, os
        # Start the new process first
        if getattr(sys, 'frozen', False):
            subprocess.Popen([sys.executable])
        else:
            subprocess.Popen([sys.executable] + sys.argv)
        # Then close windows
        self.window.destroy()
        if hasattr(self.app, 'root') and self.app.root.winfo_exists():
            self.app.root.destroy()
        
    def center_window(self):
        """Center the window on the parent (only for non-embedded mode)"""
        if not self.embedded:
            self.window.update_idletasks()
            self.tk_parent.update_idletasks()
            parent_x = self.tk_parent.winfo_x()
            parent_y = self.tk_parent.winfo_y()
            parent_width = self.tk_parent.winfo_width()
            parent_height = self.tk_parent.winfo_height()
            # Position slightly offset from parent's top-left to avoid being too far left/up
            x = parent_x + 50
            y = parent_y + 50
            self.window.geometry(f"600x400+{x}+{y}")
        
    def setup_ui(self):
        """Create the main settings UI with sidebar navigation"""
        
        # Add title for embedded mode
        if self.embedded:
            title_label = tk.Label(
                self.window,
                text="Settings",
                font=('Arial', 16, 'bold'),
                bg='#f0f0f0'
            )
            title_label.pack(pady=(20, 10))
        
        # Main container using grid layout
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        main_frame = tk.Frame(self.window, bg='#f0f0f0')
        main_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=(10,0))

        # Left sidebar for navigation
        sidebar_frame = tk.Frame(main_frame, bg='#e0e0e0', width=200)
        sidebar_frame.pack(side='left', fill='y', padx=(0, 10))
        sidebar_frame.pack_propagate(False)

        # Sidebar title
        sidebar_title = tk.Label(
            sidebar_frame,
            text="Categories" if self.embedded else "Settings",
            font=('Arial', 14, 'bold'),
            bg='#e0e0e0',
            pady=15
        )
        sidebar_title.pack(fill='x')

        # Navigation buttons
        self.nav_buttons = {}

        # General Settings (first in list)
        self.nav_buttons['general'] = tk.Button(
            sidebar_frame,
            text="⚙️ General",
            command=self.show_general_settings,
            font=('Arial', 11),
            bg='#d0d0d0',
            relief='flat',
            pady=10,
            anchor='w',
            padx=20
        )
        self.nav_buttons['general'].pack(fill='x', pady=2)

        # Wordbank Settings
        self.nav_buttons['wordbank'] = tk.Button(
            sidebar_frame,
            text="📚 Wordbank",
            command=self.show_wordbank_settings,
            font=('Arial', 11),
            bg='#d0d0d0',
            relief='flat',
            pady=10,
            anchor='w',
            padx=20
        )
        self.nav_buttons['wordbank'].pack(fill='x', pady=2)

        # Capture Settings
        self.nav_buttons['capture'] = tk.Button(
            sidebar_frame,
            text="🎯 Capture Settings",
            command=self.show_capture_settings,
            font=('Arial', 11),
            bg='#d0d0d0',
            relief='flat',
            pady=10,
            anchor='w',
            padx=20
        )
        self.nav_buttons['capture'].pack(fill='x', pady=2)

        # Right content area
        self.content_frame = tk.Frame(main_frame, bg='#f0f0f0')
        self.content_frame.pack(side='right', fill='both', expand=True)


        # No global bottom button frame; wordlists button will be added only on Wordbank tab

    def open_wordlists_folder(self):
        import os
        # Get absolute path to wordlists folder
        wordlists_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'wordlists'))
        os.startfile(wordlists_path)
        
    def clear_content(self):
        """Clear the content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def set_active_button(self, button_key):
        """Set the active navigation button styling"""
        for key, button in self.nav_buttons.items():
            if key == button_key:
                button.config(bg='#4CAF50', fg='white')
            else:
                button.config(bg='#d0d0d0', fg='black')
                
    def show_general_settings(self):
        """Show general application settings"""
        self.clear_content()
        self.set_active_button('general')
        
        # New implementation using the panel class
        general_panel = GeneralSettingsPanel(self.content_frame, self.app)
        general_panel.pack(fill='both', expand=True)

        # # Create title
        # title_label = tk.Label(
        #     self.content_frame,
        #     text="General Settings",
        #     font=('Arial', 16, 'bold'),
        #     bg='#f0f0f0'
        # )
        # title_label.pack(pady=(20, 10))
        
        # # Description
        # desc_label = tk.Label(
        #     self.content_frame,
        #     text="Configure general application settings",
        #     font=('Arial', 10),
        #     bg='#f0f0f0',
        #     fg='#666666'
        # )
        # desc_label.pack(pady=(0, 20))
        
        # # Settings container
        # settings_container = tk.Frame(self.content_frame, bg='#f0f0f0')
        # settings_container.pack(fill='both', expand=True, padx=20)
        
        # # Always on Top setting
        # always_on_top_frame = tk.Frame(settings_container, bg='#f0f0f0')
        # always_on_top_frame.pack(fill='x', pady=10)
        
        # always_on_top_cb = tk.Checkbutton(
        #     always_on_top_frame,
        #     text="Always on Top",
        #     variable=self.app.always_on_top_var,
        #     command=self.on_always_on_top_changed,
        #     font=('Arial', 11),
        #     bg='#f0f0f0'
        # )
        # always_on_top_cb.pack(anchor='w')
        
        # # Description for always on top
        # tk.Label(
        #     always_on_top_frame,
        #     text="Keep the application window above all other windows",
        #     font=('Arial', 9),
        #     bg='#f0f0f0',
        #     fg='#666666'
        # ).pack(anchor='w', padx=(25, 0))
                
    def show_wordbank_settings(self):
        """Show wordbank settings panel with embedded controls and Open Wordlists Folder button"""
        self.clear_content()
        self.set_active_button('wordbank')

        # New implementation using the panel class
        wordbank_panel = WordbankSettingsPanel(self.content_frame, self.app)
        wordbank_panel.pack(fill='both', expand=True)

        # # Create title
        # title_label = tk.Label(
        #     self.content_frame,
        #     text="Wordbank Settings",
        #     font=('Arial', 16, 'bold'),
        #     bg='#f0f0f0'
        # )
        # title_label.pack(pady=(20, 10))
        
        # # Description
        # desc_label = tk.Label(
        #     self.content_frame,
        #     text="Configure word lists and wordbank settings",
        #     font=('Arial', 10),
        #     bg='#f0f0f0',
        #     fg='#666666'
        # )
        # desc_label.pack(pady=(0, 20))
        
        # # Create scrollable frame for word list controls
        # canvas = tk.Canvas(self.content_frame, bg='#f0f0f0')
        # scrollbar = tk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        # scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        # scrollable_frame.bind(
        #     "<Configure>",
        #     lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        # )
        
        # canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        # canvas.configure(yscrollcommand=scrollbar.set)
        
        # canvas.pack(side="left", fill="both", expand=True)
        # scrollbar.pack(side="right", fill="y")
        
        # # Word list selection checkboxes (embedded here directly)
        # selection_label = tk.Label(
        #     scrollable_frame,
        #     text="Select Word Lists:",
        #     font=('Arial', 12, 'bold'),
        #     bg='#f0f0f0'
        # )
        # selection_label.pack(anchor='w', padx=20, pady=(10, 5))
        
        # # Get word filter from parent if available
        # if hasattr(self.app, 'word_filter'):
        #     wordlist_info = self.app.word_filter.get_wordlist_info()
        #     self.check_vars = {}
            
        #     checkbox_frame = tk.Frame(scrollable_frame, bg='#f0f0f0')
        #     checkbox_frame.pack(fill='x', padx=20, pady=5)
            
        #     for filename, info in wordlist_info.items():
        #         var = tk.BooleanVar(value=info['selected'])
        #         self.check_vars[filename] = var
                
        #         # Create checkbox with word count
        #         chk_text = f"{filename} ({info['count']} words)"
        #         # Need to use a function factory for proper lambda with filename binding
        #         def make_cmd_func(fname=filename):
        #             return lambda: self.on_wordlist_selection_changed(fname)
                    
        #         chk = tk.Checkbutton(
        #             checkbox_frame,
        #             text=chk_text,
        #             variable=var,
        #             command=make_cmd_func(),
        #             bg='#f0f0f0',
        #             anchor='w',
        #             font=('Arial', 10)
        #         )
        #         chk.pack(fill='x', pady=2)
            
        #     # Word count summary (track single label)
        #     total_words = sum(info['count'] for info in wordlist_info.values() if info['selected'])
        #     self.summary_label = tk.Label(
        #         scrollable_frame,
        #         text=f"Total selected words: {total_words}",
        #         font=('Arial', 10, 'bold'),
        #         bg='#f0f0f0',
        #         fg='#2196F3',
        #         name="summary_label"
        #     )
        #     self.summary_label.pack(anchor='w', padx=20, pady=10)
        # else:
        #     # No word filter available
        #     no_filter_label = tk.Label(
        #         scrollable_frame,
        #         text="Word filter not available",
        #         font=('Arial', 10),
        #         bg='#f0f0f0',
        #         fg='#666666'
        #     )
        #     no_filter_label.pack(anchor='w', padx=20, pady=10)
        
    def show_capture_settings(self):
        """Show capture settings panel"""
        self.clear_content()
        self.set_active_button('capture')
        
        # New implementation using the panel class
        capture_panel = CaptureSettingsPanel(self.content_frame, self.app)
        capture_panel.pack(fill='both', expand=True)

        # # Create title
        # title_label = tk.Label(
        #     self.content_frame,
        #     text="Capture Settings",
        #     font=('Arial', 16, 'bold'),
        #     bg='#f0f0f0'
        # )
        # title_label.pack(pady=(20, 10))
        
        # # Description
        # desc_label = tk.Label(
        #     self.content_frame,
        #     text="Configure screen capture and monitoring settings",
        #     font=('Arial', 10),
        #     bg='#f0f0f0',
        #     fg='#666666'
        # )
        # desc_label.pack(pady=(0, 20))
        
        # # --- Inline capture settings controls ---
        # # Window selection
        # window_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        # window_frame.pack(fill='x', padx=10, pady=5)
        
        # tk.Label(
        #     window_frame,
        #     text="Window:",
        #     bg='#f0f0f0',
        #     font=('Arial', 9)
        # ).pack(anchor='w')
        
        # # Window dropdown
        # dropdown_frame = tk.Frame(window_frame, bg='#f0f0f0')
        # dropdown_frame.pack(fill='x', pady=2)
        
        # self.window_var = tk.StringVar()
        # self.window_dropdown = ttk.Combobox(
        #     dropdown_frame,
        #     textvariable=self.window_var,
        #     state='readonly',
        #     width=50
        # )
        # self.window_dropdown.pack(side='left', fill='x', expand=True)
        
        # # Refresh button
        # self.refresh_btn = tk.Button(
        #     dropdown_frame,
        #     text="↻",
        #     command=self.on_refresh_windows,
        #     font=('Arial', 12),
        #     width=3
        # )
        # self.refresh_btn.pack(side='right', padx=(5, 0))
        
        # # Window match priority
        # priority_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        # priority_frame.pack(fill='x', padx=10, pady=5)
        
        # tk.Label(
        #     priority_frame,
        #     text="Window Match Priority:",
        #     bg='#f0f0f0',
        #     font=('Arial', 9)
        # ).pack(side='left')
        
        # self.priority_var = tk.StringVar(value="Match title")
        # priority_dropdown = ttk.Combobox(
        #     priority_frame,
        #     textvariable=self.priority_var,
        #     values=["Match title", "Match exact window", "Match any window"],
        #     state='readonly',
        #     width=20
        # )
        # priority_dropdown.pack(side='right')
        
        # # Preview area
        # preview_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        # preview_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # tk.Label(
        #     preview_frame,
        #     text="Preview:",
        #     bg='#f0f0f0',
        #     font=('Arial', 9)
        # ).pack(anchor='w')
        
        # # Preview canvas (shows scaled window rectangle)
        # self.preview_canvas = tk.Canvas(
        #     preview_frame,
        #     bg='#ccc',  # light gray background
        #     height=200,
        #     relief='flat',  # remove border
        #     borderwidth=0,  # no border
        #     highlightthickness=0  # remove focus highlight
        # )
        # self.preview_canvas.pack(fill='both', expand=True, pady=5)
        # # draw static gray placeholder and enable drag-select on canvas
        # self.preview_canvas.bind('<Configure>', self.draw_placeholder)
        # self.preview_canvas.bind('<ButtonPress-1>', self.on_canvas_press)
        # self.preview_canvas.bind('<B1-Motion>',    self.on_canvas_drag)
        # self.preview_canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
        # # initial draw
        # self.preview_canvas.event_generate('<Configure>')
        
        # # Configured Coordinates display (below preview)
        # coords_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        # coords_frame.pack(fill='x', padx=10, pady=(5,0))
        # tk.Label(
        #     coords_frame,
        #     text="Configured Coordinates:",
        #     bg='#f0f0f0',
        #     font=('Arial', 9)
        # ).pack(side='left')
        # self.coords_label = tk.Label(
        #     coords_frame,
        #     text="None",
        #     bg='#f0f0f0',
        #     font=('Arial', 9, 'bold')
        # )
        # self.coords_label.pack(side='left', padx=5)
        
        # # Bottom controls
        # bottom_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        # bottom_frame.pack(fill='x', padx=10, pady=5)
        
        # # Start/Stop monitoring
        # self.monitor_btn = tk.Button(
        #     bottom_frame,
        #     text="Start Monitoring",
        #     command=self.on_toggle_monitoring,
        #     bg='#4CAF50',
        #     fg='white',
        #     font=('Arial', 10),
        #     padx=20
        # )
        # self.monitor_btn.pack(side='left')
        
        # # Select Capture Area toggle button
        # self.select_area_btn = tk.Button(
        #     bottom_frame,
        #     text="Enable Selection Mode",
        #     command=self.on_select_area,
        #     font=('Arial', 10),
        #     padx=15
        # )
        # self.select_area_btn.pack(side='left', padx=(5,0))
        
        # # Capture rate
        # rate_frame = tk.Frame(bottom_frame, bg='#f0f0f0')
        # rate_frame.pack(side='right')
        
        # tk.Label(
        #     rate_frame,
        #     text="Capture Rate:",
        #     bg='#f0f0f0',
        #     font=('Arial', 9)
        # ).pack(side='left')
        
        # self.rate_var = tk.DoubleVar(value=1.0)
        # self.rate_scale = tk.Scale(
        #     rate_frame,
        #     variable=self.rate_var,
        #     from_=0.1,
        #     to=5.0,
        #     resolution=0.1,
        #     orient='horizontal',
        #     length=100,
        #     bg='#f0f0f0'
        # )
        # self.rate_scale.pack(side='left', padx=5)
        
        # tk.Label(
        #     rate_frame,
        #     text="FPS",
        #     bg='#f0f0f0',
        #     font=('Arial', 9)
        # ).pack(side='left')
        
        # # Populate window list and bind selection event
        # self.populate_windows()
        # self.window_dropdown.bind('<<ComboboxSelected>>', lambda e: (
        #     self.print_selected_window_dims(), 
        #     self.preview_canvas.event_generate('<Configure>') if self.preview_canvas else None,
        #     print("[DEBUG] Window selection changed - redrawing preview")
        # ))
        
    def open_word_list_selection(self):
        """Open the word list selection window"""
        if hasattr(self.app, 'on_select_word_lists'):
            self.app.on_select_word_lists()
        
    def open_capture_settings(self):
        """Open the capture settings window"""
        # Close this settings window first
        self.window.destroy()
        
        # Open capture settings
        from .capture_settings import CaptureSettingsWindow
        capture_window = CaptureSettingsWindow(self.tk_parent)
        
    # def on_wordlist_selection_changed(self, filename=None):
    #     """Handle wordlist selection changes"""
    #     if hasattr(self.app, 'word_filter') and hasattr(self, 'check_vars'):
    #         # Update word filter based on checkbox states
    #         selected_lists = []
    #         for fname, var in self.check_vars.items():
    #             if var.get():
    #                 selected_lists.append(fname)
            
    #         # Update the word filter
    #         self.app.word_filter.update_selected_wordlists(selected_lists)
            
    #         # Refresh the parent if callback exists
    #         if hasattr(self.app, '_on_wordlists_updated'):
    #             self.app._on_wordlists_updated()
                
    #         # Update word count display
    #         self.refresh_wordcount_display()
            
    # def refresh_wordcount_display(self):
    #     """Refresh the word count display"""
    #     # Update the tracked summary label text
    #     if hasattr(self, 'summary_label'):
    #         # Calculate updated total selected words
    #         wordlist_info = self.app.word_filter.get_wordlist_info()
    #         total_words = sum(info['count'] for info in wordlist_info.values() if info['selected'])
    #         self.summary_label.config(text=f"Total selected words: {total_words}")
            
    # ===============================
    
    # General Settings Handler Methods
    # ===============================
    
    def on_always_on_top_changed(self):
        """Handle always on top checkbox changes"""
        if hasattr(self.app, 'root'):
            self.app.root.attributes('-topmost', self.app.always_on_top_var.get())
    
    # Capture Settings Handler Methods
    # ===============================
    
    def on_refresh_windows(self):
        """Refresh the window list"""
        self.populate_windows()
        # debug dims after refresh
        self.print_selected_window_dims()
        # update preview placeholder
        if self.preview_canvas:
            self.preview_canvas.event_generate('<Configure>')
        
    def populate_windows(self):
        """Populate the window dropdown with all open window titles"""
        import pygetwindow as gw
        # Populate dropdown with all window titles
        try:
            windows = gw.getAllTitles()
            # filter out empty or whitespace-only titles
            filtered = [w for w in windows if w and w.strip()]
            # define keywords
            game_keywords = ['skribbl', 'draw', 'pictionary', 'quickdraw']
            browser_terms = ['chrome', 'firefox', 'edge']
            # define unconditional blacklist of system/IDE windows
            blacklist = [
                'visual studio code', 'file explorer', 'settings',
                'task manager', 'program manager', 'windows input experience',
                # exclude app windows and known helpers
                'word matcher', 'select capture area', 'grammarly', 'voicemod', 'wv_',
                # exclude refresh dialogs
                'refresh'
            ]
            windows = []
            for w in filtered:
                lw = w.lower()
                # skip unconditional blacklist
                if any(term in lw for term in blacklist):
                    continue
                # skip browsers unless they contain a game keyword
                if any(b in lw for b in browser_terms) and not any(g in lw for g in game_keywords):
                    continue
                windows.append(w)
            # remove duplicate titles while preserving order
            seen = set()
            unique = []
            for w in windows:
                if w not in seen:
                    seen.add(w)
                    unique.append(w)
            windows = unique
        except Exception:
            windows = []
        # Fallback if no valid windows found
        if not windows:
            windows = ["No sources detected"]
        
        # DEBUG: print retrieved window titles
        print("[DEBUG] populate_windows titles:", windows)
        if self.window_dropdown:
            self.window_dropdown['values'] = windows
            if windows and windows[0] != "No sources detected":
                # Select first entry by default only if it's a real window
                self.window_dropdown.set(windows[0])
                # debug dims for default selection
                self.print_selected_window_dims()
            else:
                # No valid sources, set the placeholder
                self.window_dropdown.set("No sources detected")
            
    def on_toggle_monitoring(self):
        """Toggle monitoring state"""
        self.monitoring = not self.monitoring
        
        if self.monitoring:
            # Turn off selection mode if it's active
            if self.select_mode:
                self.select_mode = False
                if self.select_area_btn:
                    self.select_area_btn.config(
                        text="Enable Selection Mode", 
                        bg=self.window.cget('bg'),
                        fg="black"
                    )
                if self.preview_canvas:
                    self.preview_canvas.config(cursor="")
            
            if self.monitor_btn:
                self.monitor_btn.config(text="Stop Monitoring", bg='#f44336')
            messagebox.showinfo("Monitoring", f"Monitoring started at {self.rate_var.get():.1f} FPS")
        else:
            if self.monitor_btn:
                self.monitor_btn.config(text="Start Monitoring", bg='#4CAF50')
            messagebox.showinfo("Monitoring", "Monitoring stopped")
    
    def on_select_area(self):
        """Toggle interactive selection mode on/off"""
        self.select_mode = not self.select_mode
        
        if self.select_mode:
            # Turn off monitoring if it's active
            if self.monitoring:
                self.monitoring = False
                if self.monitor_btn:
                    self.monitor_btn.config(text="Start Monitoring", bg='#4CAF50')
                
            if self.select_area_btn:
                self.select_area_btn.config(
                    text="Disable Selection Mode", 
                    bg='orange',
                    fg="white"
                )
            if self.preview_canvas:
                self.preview_canvas.config(cursor="crosshair")
            messagebox.showinfo("Selection Mode", "Click and drag on the preview to select capture area")
        else:
            if self.select_area_btn:
                self.select_area_btn.config(
                    text="Enable Selection Mode", 
                    bg=self.window.cget('bg'),
                    fg="black"
                )
            if self.preview_canvas:
                self.preview_canvas.config(cursor="")
                # clear any rectangle selection
                self.preview_canvas.delete('selrect')
    
    def print_selected_window_dims(self):
        """Prints debug info for selected window dimensions"""
        import pygetwindow as gw
        title = self.window_var.get()
        
        # Skip if no valid source is selected
        if not title or title == "No sources detected":
            print("[DEBUG] No valid window source selected")
            return
            
        try:
            # fresh enumerate all windows for updated dimensions
            all_windows = gw.getAllWindows()
            # match by title substring
            matches = [w for w in all_windows if title.lower() in w.title.lower()]
            win = matches[0] if matches else gw.getWindowsWithTitle(title)[0]
            print(f"[DEBUG] Selected window '{title}' dims: left={win.left}, top={win.top}, width={win.width}, height={win.height}")
            
            # Provide more detailed window geometry information for debugging
            print(f"[DEBUG] Window box: left={win.left}, top={win.top}, right={win.right}, bottom={win.bottom}")
            
            # Check for negative coordinates which often indicate window borders
            if win.left < 0 or win.top < 0:
                print(f"[DEBUG] Window has negative position - likely has borders of approximately {abs(min(win.left, 0))}px horizontal, {abs(min(win.top, 0))}px vertical")
        except Exception as e:
            print(f"[DEBUG] Failed to get dims for '{title}': {e}")
            
    def draw_placeholder(self, event=None):
        """Draw a gray rectangle proportional to the selected window in the preview canvas, centered."""
        import pygetwindow as gw
        canvas = self.preview_canvas
        
        # Check if canvas exists
        if not canvas:
            return
            
        # clear previous drawings
        canvas.delete('placeholder')
        canvas.delete('selection')
        canvas.delete('overlay')
        title = self.window_var.get()
        
        # Check if no valid source is selected
        if not title or title == "No sources detected":
            # Hide the preview by not drawing anything
            return
            
        # get window dims and position, fallback to canvas
        try:
            win = gw.getWindowsWithTitle(title)[0]
            ww, wh = win.width, win.height
            left, top = win.left, win.top
        except Exception:
            # If we can't get the window, also hide the preview
            print(f"[DEBUG] Could not find window '{title}', hiding preview")
            return
        # get canvas dimensions
        cw = canvas.winfo_width()
        ch = canvas.winfo_height()
        margin = 10
        # compute scale to fit with margin
        scale = min((cw - 2 * margin) / ww, (ch - 2 * margin) / wh)
        scale = max(scale, 0)
        # calculate drawn size and center
        rw, rh = ww * scale, wh * scale
        xoff = (cw - rw) / 2
        yoff = (ch - rh) / 2
        # store full mapping info
        self._canvas_info = {'scale': scale, 'xoff': xoff, 'yoff': yoff,
                              'rw': rw, 'rh': rh, 'left': left, 'top': top}
                              
        # draw gray rectangle base
        canvas.create_rectangle(xoff, yoff, xoff + rw, yoff + rh,
                                fill='#888', outline='', tags='placeholder')
                                
        # Add semi-transparent black overlay (75% opaque)
        # Note: Tkinter doesn't support true alpha transparency, so we use a stipple pattern
        # gray75 provides approximately 75% opacity (25% see-through)
        canvas.create_rectangle(xoff, yoff, xoff + rw, yoff + rh,
                              fill='#000000', outline='', stipple='gray75', tags='overlay')
                                
        # draw dimension labels
        # horizontal label above rectangle
        canvas.create_text(xoff + rw / 2, yoff - margin / 2,
                           text=f'{ww}px', fill='black', font=('Arial', 9),
                           tags='placeholder')
        # vertical label to the left of rectangle
        canvas.create_text(xoff - margin / 2, yoff + rh / 2,
                           text=f'{wh}px', fill='black', font=('Arial', 9),
                           angle=90, tags='placeholder')
        
        # overlay default text if no selection
        if not self.coordinates:
            canvas.create_text(cw/2, ch/2, text="No capture area selected",
                               fill='white', font=('Arial', 10, 'italic'), tags='selection')
        else:
            # persistent selection overlay
            info = self._canvas_info
            
            # Map real coords to canvas
            print(f"[DEBUG] draw_placeholder - coordinates={self.coordinates}, info={info}")
            # Calculate the position in the window relative to its top-left
            window_rel_x = self.coordinates[0] - info['left']
            window_rel_y = self.coordinates[1] - info['top']
            
            # Convert window-relative coordinates to canvas coordinates
            cx = info['xoff'] + window_rel_x * info['scale']
            cy = info['yoff'] + window_rel_y * info['scale']
            
            # Scale the width and height
            cw_sel = self.coordinates[2] * info['scale']
            ch_sel = self.coordinates[3] * info['scale']
            
            print(f"[DEBUG] draw_placeholder - window relative: ({window_rel_x}, {window_rel_y})")
            print(f"[DEBUG] draw_placeholder - canvas coords: ({cx}, {cy}) {cw_sel}x{ch_sel}")
            
            # Ensure selection stays within the placeholder bounds
            x0 = info['xoff']  # left edge of placeholder
            y0 = info['yoff']  # top edge of placeholder
            x1 = x0 + info['rw']  # right edge of placeholder
            y1 = y0 + info['rh']  # bottom edge of placeholder
            
            # Constrain selection rectangle to placeholder bounds
            cx = max(x0, min(x1, cx))
            cy = max(y0, min(y1, cy))
            cx_end = max(x0, min(x1, cx + cw_sel))
            cy_end = max(y0, min(y1, cy + ch_sel))
            
            print(f"[DEBUG] Drawing selection rectangle at: ({cx}, {cy}) to ({cx_end}, {cy_end})")
            
            # "Punch through" the black overlay by creating a clear rectangle in the selection area
            if canvas:
                canvas.create_rectangle(cx, cy, cx_end, cy_end,
                                      fill='#888', outline='', tags='selection')
                
                # Draw the selection rectangle outline with increased visibility
                canvas.create_rectangle(cx, cy, cx_end, cy_end,
                                       outline='red', dash=(4, 2), width=3, tags='selection')
    
    def on_canvas_press(self, event):
        """Start drag-select on preview canvas."""
        # clear any previous start coords
        self.start_x = None
        self.start_y = None
        if not self.select_mode:
            return
        # only start if inside gray placeholder
        info = self._canvas_info
        x0, y0 = info.get('xoff', 0), info.get('yoff', 0)
        x1, y1 = x0 + info.get('rw', 0), y0 + info.get('rh', 0)
        
        # Check if click is inside placeholder
        if not (x0 <= event.x <= x1 and y0 <= event.y <= y1):
            return
            
        # Constrain start point to gray rectangle bounds
        constrained_x = max(x0, min(x1, event.x))
        constrained_y = max(y0, min(y1, event.y))
        
        # valid start - use constrained coordinates
        self.start_x, self.start_y = constrained_x, constrained_y
        if self.preview_canvas:
            self.preview_canvas.delete('selrect')

    def on_canvas_drag(self, event):
        """Update drag-select rectangle."""
        if not self.select_mode or self.start_x is None or self.start_y is None:
            return
        canvas = self.preview_canvas
        if not canvas:
            return
        canvas.delete('selrect')
        # restrict drag within placeholder
        info = self._canvas_info
        x0 = info['xoff']  # left edge
        y0 = info['yoff']  # top edge
        x1 = info['xoff'] + info['rw']  # right edge
        y1 = info['yoff'] + info['rh']  # bottom edge
        
        # Constrain event point to gray rectangle bounds
        x2 = max(x0, min(x1, event.x))
        y2 = max(y0, min(y1, event.y))
        
        # Ensure start_x/y are integers before rectangle creation
        canvas.create_rectangle(int(self.start_x), int(self.start_y), x2, y2,
                                outline='red', dash=(4, 2), tags='selrect')

    def on_canvas_release(self, event):
        """Finalize selection and map to window coords."""
        import pygetwindow as gw
        print(f"[DEBUG] on_canvas_release triggered at canvas coords: ({event.x}, {event.y})")
        if not self.select_mode or self.start_x is None or self.start_y is None:
            return
        canvas = self.preview_canvas
        if not canvas:
            return
        canvas.delete('selrect')  # Remove the drag selection
        
        # Store the start values before we reset them
        if self.start_x is None or self.start_y is None:
            return
            
        # Ensure we're working with valid coordinates
        info = self._canvas_info
        x0 = info['xoff']  # left edge
        y0 = info['yoff']  # top edge
        x1 = info['xoff'] + info['rw']  # right edge
        y1 = info['yoff'] + info['rh']  # bottom edge
        
        # Get the event coordinates within bounds
        event_x = max(x0, min(x1, event.x))
        event_y = max(y0, min(y1, event.y))
        
        # Calculate selection rectangle in canvas coordinates
        left_canvas = min(self.start_x, event_x)
        top_canvas = min(self.start_y, event_y)
        width_canvas = abs(event_x - self.start_x)
        height_canvas = abs(event_y - self.start_y)
        
        # Convert to window coordinates
        scale = info['scale']
        window_left = info['left'] + (left_canvas - info['xoff']) / scale
        window_top = info['top'] + (top_canvas - info['yoff']) / scale
        window_width = width_canvas / scale
        window_height = height_canvas / scale
        
        # Handle Windows invisible borders by detecting and compensating
        title = self.window_var.get()
        try:
            win = gw.getWindowsWithTitle(title)[0]
            # Check for common browser windows that have invisible borders
            if any(browser in title.lower() for browser in ['chrome', 'firefox', 'edge']):
                # Windows typically adds ~6-8px invisible borders
                border_offset = 6
                if win.left < 0 or win.top < 0:
                    print(f"[DEBUG] Detected invisible borders, adjusting coordinates by {border_offset}px")
                    window_left += border_offset
                    window_top += border_offset
        except Exception as e:
            print(f"[DEBUG] Could not check for invisible borders: {e}")
        
        # Store as integers
        self.coordinates = (int(window_left), int(window_top), int(window_width), int(window_height))
        
        # Update coordinates display
        if self.coords_label:
            self.coords_label.config(text=f"({self.coordinates[0]}, {self.coordinates[1]}, {self.coordinates[2]}, {self.coordinates[3]})")
        
        # Save to selection history for undo/redo functionality
        self.selection_history.append(self.coordinates)
        self.history_index = len(self.selection_history) - 1
        
        print(f"[DEBUG] Final coordinates set to: {self.coordinates}")
        
        # Redraw placeholder to show persistent selection
        self.draw_placeholder()
        
        # Reset drag state
        self.start_x = None
        self.start_y = None
