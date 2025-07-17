import tkinter as tk
from tkinter import ttk, messagebox
from ..utils.word_filtering import WordFilter
from .debug_window import DebugWindow


class WordListSelectionWindow:
    """Enhanced word list selection window with preview"""
    
    def __init__(self, parent, word_filter, callback):
        self.parent = parent
        self.word_filter = word_filter
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Select Word Lists")
        self.window.geometry("700x500")
        self.window.configure(bg='#f0f0f0')
        self.window.resizable(True, True)
        
        # Make it modal
        self.window.transient(parent)
        self.window.grab_set()
        
        self.check_vars = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Create the selection UI"""
        
        # Main container with two panes
        main_paned = tk.PanedWindow(self.window, orient=tk.HORIZONTAL, bg='#f0f0f0')
        main_paned.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left pane - checkboxes
        left_frame = tk.Frame(main_paned, bg='#f0f0f0')
        main_paned.add(left_frame, minsize=300)
        
        tk.Label(
            left_frame,
            text="Select Word Lists:",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0'
        ).pack(anchor='w', pady=(0, 10))
        
        # Scrollable checkbox area
        checkbox_frame = tk.Frame(left_frame, bg='#f0f0f0')
        checkbox_frame.pack(fill='both', expand=True)
        
        # Get wordlist info
        wordlist_info = self.word_filter.get_wordlist_info()
        
        for filename, info in wordlist_info.items():
            var = tk.BooleanVar(value=info['selected'])
            self.check_vars[filename] = var
            
            # Create checkbox with word count
            chk_text = f"{filename} ({info['count']} words)"
            chk = tk.Checkbutton(
                checkbox_frame,
                text=chk_text,
                variable=var,
                command=self.on_selection_changed,
                bg='#f0f0f0',
                anchor='w'
            )
            chk.pack(fill='x', pady=2, padx=5)
        
        # Right pane - word preview
        right_frame = tk.Frame(main_paned, bg='#f0f0f0')
        main_paned.add(right_frame, minsize=350)
        
        tk.Label(
            right_frame,
            text="Combined Word List Preview:",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0'
        ).pack(anchor='w', pady=(0, 5))
        
        # Word count label
        self.word_count_label = tk.Label(
            right_frame,
            text="Loading...",
            font=('Arial', 9),
            bg='#f0f0f0',
            fg='#666666'
        )
        self.word_count_label.pack(anchor='w', pady=(0, 5))
        
        # Scrollable word list
        list_frame = tk.Frame(right_frame)
        list_frame.pack(fill='both', expand=True)
        
        # Scrollbars
        v_scrollbar = tk.Scrollbar(list_frame, orient='vertical')
        h_scrollbar = tk.Scrollbar(list_frame, orient='horizontal')
        
        # Text widget for editable word list
        self.words_text = tk.Text(
            list_frame,
            font=('Arial', 9),
            wrap='none',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        v_scrollbar.config(command=self.words_text.yview)
        h_scrollbar.config(command=self.words_text.xview)
        
        # Pack scrollbars and text widget
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        self.words_text.pack(side='left', fill='both', expand=True)
        
        # Bottom buttons
        button_frame = tk.Frame(self.window, bg='#f0f0f0')
        button_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(
            button_frame,
            text="Cancel",
            command=self.window.destroy,
            padx=20
        ).pack(side='right', padx=5)
        
        tk.Button(
            button_frame,
            text="Confirm",
            command=self.on_confirm,
            bg='#4CAF50',
            fg='white',
            padx=20
        ).pack(side='right', padx=5)
        
        # Load initial preview
        self.update_preview()
        # Enable text widget editing bindings
        self.setup_text_bindings()
        
    def on_selection_changed(self):
        """Handle checkbox selection changes"""
        self.update_preview()
        
    def update_preview(self):
        """Update the word list preview"""
        # Get selected files
        selected_files = [
            filename for filename, var in self.check_vars.items()
            if var.get()
        ]
        
        # Create temporary word filter to get preview
        temp_filter = WordFilter(self.word_filter.wordlists_folder)
        temp_filter.update_selected_wordlists(selected_files)
        
        # Get combined wordlist
        combined_words = temp_filter.get_combined_wordlist()
        
        # Update word count
        self.word_count_label.config(text=f"Total: {len(combined_words)} words")
        
        # Update text editor with combined words
        self.words_text.delete('1.0', tk.END)
        for word in combined_words:
            self.words_text.insert(tk.END, word + '\n')
            
    def on_confirm(self):
        """Apply the selected wordlists"""
        selected_files = [
            filename for filename, var in self.check_vars.items()
            if var.get()
        ]
        
        # Update the main word filter
        self.word_filter.update_selected_wordlists(selected_files)
        
        # Call the callback to refresh the main window
        if self.callback:
            self.callback()
            
        # Close window
        self.window.destroy()

    # Text editing helpers
    def setup_text_bindings(self):
        """Bind keyboard shortcuts for the text editor."""
        # Select all
        self.words_text.bind('<Control-a>', self._select_all)
        self.words_text.bind('<Control-A>', self._select_all)
        # Delete selected lines or current line
        self.words_text.bind('<Delete>', self._delete_selected_lines)

    def _select_all(self, event=None):
        """Select all text in the editor."""
        self.words_text.tag_add('sel', '1.0', 'end')
        return 'break'

    def _delete_selected_lines(self, event=None):
        """Delete selected lines or the line at the cursor."""
        try:
            start = self.words_text.index('sel.first linestart')
            end = self.words_text.index('sel.last lineend +1c')
        except tk.TclError:
            # No selection, delete current line
            start = self.words_text.index('insert linestart')
            end = self.words_text.index('insert lineend +1c')
        self.words_text.delete(start, end)
        return 'break'

    def sort_editor_content(self):
        """Sort the lines in the editor alphabetically."""
        content = self.words_text.get('1.0', 'end').splitlines()
        lines = sorted([line for line in content if line.strip()])
        self.words_text.delete('1.0', 'end')
        for line in lines:
            self.words_text.insert('end', line + '\n')

class WordMatcherWindow:
    """Main window for word pattern matching"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Word Matcher")
        self.root.geometry("700x550")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize word filter
        self.word_filter = WordFilter()
        
        # Initialize debug window for development
        self.debug_window = None
        self.init_debug_window()
        
        # Frame management
        self.current_frame = None
        self.frames = {}
        
        self.setup_navigation()
        self.setup_frames()
        self.show_frame('main')
        
    def setup_navigation(self):
        """Create the navigation bar at the top"""
        self.nav_frame = tk.Frame(self.root, bg='#d0d0d0', height=40)
        self.nav_frame.pack(fill='x', side='top')
        self.nav_frame.pack_propagate(False)
        
        # Navigation buttons
        nav_buttons_frame = tk.Frame(self.nav_frame, bg='#d0d0d0')
        nav_buttons_frame.pack(side='left', padx=10, pady=5)
        
        self.main_nav_btn = tk.Button(
            nav_buttons_frame,
            text="Main",
            command=lambda: self.show_frame('main'),
            relief='flat',
            bg='#4CAF50',
            fg='white',
            padx=15
        )
        self.main_nav_btn.pack(side='left', padx=2)
        
        self.settings_nav_btn = tk.Button(
            nav_buttons_frame,
            text="Settings",
            command=lambda: self.show_frame('settings'),
            relief='flat',
            bg='#e0e0e0',
            padx=15
        )
        self.settings_nav_btn.pack(side='left', padx=2)
        
        self.wordlists_nav_btn = tk.Button(
            nav_buttons_frame,
            text="Word Lists",
            command=lambda: self.show_frame('wordlists'),
            relief='flat',
            bg='#e0e0e0',
            padx=15
        )
        self.wordlists_nav_btn.pack(side='left', padx=2)
        
        # Right side controls (always on top, debug)
        right_nav_frame = tk.Frame(self.nav_frame, bg='#d0d0d0')
        right_nav_frame.pack(side='right', padx=10, pady=5)
        
        self.always_on_top_var = tk.BooleanVar()
        self.always_on_top_cb = tk.Checkbutton(
            right_nav_frame,
            text="Always on Top",
            variable=self.always_on_top_var,
            command=self.on_always_on_top,
            bg='#d0d0d0'
        )
        self.always_on_top_cb.pack(side='right', padx=5)
        
        # Debug button (still opens separate window)
        self.debug_btn = tk.Button(
            right_nav_frame,
            text="🔧",
            command=self.on_open_debug,
            font=('Arial', 12),
            width=3,
            relief='raised'
        )
        self.debug_btn.pack(side='right', padx=5)
        
    def setup_frames(self):
        """Initialize all the main frames"""
        # Container for all frames
        self.container = tk.Frame(self.root, bg='#f0f0f0')
        self.container.pack(fill='both', expand=True)
        
        # Main frame (current functionality)
        self.frames['main'] = self.create_main_frame()
        
        # Settings frame (embedded settings)
        self.frames['settings'] = self.create_settings_frame()
        
        # Word lists frame (embedded word list selection)
        self.frames['wordlists'] = self.create_wordlists_frame()
        
    def show_frame(self, frame_name):
        """Show the specified frame and hide others"""
        # Hide current frame
        if self.current_frame:
            self.frames[self.current_frame].pack_forget()
            
        # Show new frame
        self.frames[frame_name].pack(fill='both', expand=True)
        self.current_frame = frame_name
        
        # Update navigation button states
        self.update_nav_buttons(frame_name)
        
    def update_nav_buttons(self, active_frame):
        """Update navigation button visual states"""
        buttons = {
            'main': self.main_nav_btn,
            'settings': self.settings_nav_btn, 
            'wordlists': self.wordlists_nav_btn
        }
        
        for name, btn in buttons.items():
            if name == active_frame:
                btn.config(bg='#4CAF50', fg='white')
            else:
                btn.config(bg='#e0e0e0', fg='black')
                
    def create_main_frame(self):
        """Create the main functionality frame"""
        main_frame = tk.Frame(self.container, bg='#f0f0f0')
        
        # Move the existing UI setup here
        self.setup_main_ui(main_frame)
        
        return main_frame
        
    def create_settings_frame(self):
        """Create the embedded settings frame"""
        settings_frame = tk.Frame(self.container, bg='#f0f0f0')
        
        # Import and create embedded settings
        from .settings_window import SettingsWindow
        self.embedded_settings = SettingsWindow(self, settings_frame, embedded=True)
        
        return settings_frame
        
    def create_wordlists_frame(self):
        """Create the embedded word lists frame"""
        wordlists_frame = tk.Frame(self.container, bg='#f0f0f0')
        
        # Create embedded word list selection UI
        self.setup_wordlists_ui(wordlists_frame)
        
        return wordlists_frame
        
    def setup_main_ui(self, parent_frame):
        """Create the main UI elements"""
        
        # Top frame with buttons
        top_frame = tk.Frame(parent_frame, bg='#f0f0f0')
        top_frame.pack(fill='x', padx=10, pady=5)
        
        # Left side buttons
        left_buttons_frame = tk.Frame(top_frame, bg='#f0f0f0')
        left_buttons_frame.pack(side='left')
        
        self.recent_changes_btn = tk.Button(
            left_buttons_frame,
            text="Recent Changes", 
            command=self.on_recent_changes,
            relief='raised',
            padx=15, pady=5
        )
        self.recent_changes_btn.pack(side='left', padx=5)
        
        # Remove the old separate navigation controls since they're now in nav bar
        # Word input frame
        input_frame = tk.Frame(parent_frame, bg='#f0f0f0')
        input_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(
            input_frame, 
            text="Enter obfuscated word (e.g. dr_w_ng, r__, _d):",
            bg='#f0f0f0',
            font=('Arial', 10)
        ).pack(side='left')
        
        # Word input with length controls
        word_input_frame = tk.Frame(input_frame, bg='#f0f0f0')
        word_input_frame.pack(side='right')
        
        self.word_entry = tk.Entry(
            word_input_frame,
            font=('Arial', 12),
            width=20
        )
        self.word_entry.pack(side='left', padx=5)
        self.word_entry.bind('<KeyRelease>', self.on_word_changed)
        
        # Length display
        self.length_label = tk.Label(
            word_input_frame,
            text="0",
            bg='white',
            relief='sunken',
            width=3,
            font=('Arial', 10)
        )
        self.length_label.pack(side='left', padx=5)
        
        # +/- buttons
        self.plus_btn = tk.Button(
            word_input_frame,
            text="+",
            command=self.on_length_plus,
            width=3
        )
        self.plus_btn.pack(side='left', padx=2)
        
        self.minus_btn = tk.Button(
            word_input_frame,
            text="-", 
            command=self.on_length_minus,
            width=3
        )
        self.minus_btn.pack(side='left', padx=2)
        
        # Results listbox
        results_frame = tk.Frame(parent_frame, bg='#f0f0f0')
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create listbox with scrollbar
        listbox_frame = tk.Frame(results_frame)
        listbox_frame.pack(fill='both', expand=True)
        
        self.results_listbox = tk.Listbox(
            listbox_frame,
            font=('Arial', 11),
            height=15
        )
        
        scrollbar = tk.Scrollbar(listbox_frame, orient='vertical')
        self.results_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.results_listbox.yview)
        
        self.results_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Status bar
        self.status_bar = tk.Label(
            parent_frame,
            text=f"Ready - {self.word_filter.get_word_count()} words loaded",
            relief='sunken',
            anchor='w',
            bg='#f0f0f0',
            font=('Arial', 9)
        )
        self.status_bar.pack(side='bottom', fill='x')
        # Populate initial results (show all words)
        self.filter_words('')
        
    # TODO: Pin recent changes feature for future implementation (placeholder for LLM)
    def on_recent_changes(self):
        """Handle Recent Changes button click (to be implemented)"""
        messagebox.showinfo("Recent Changes", "Feature coming soon: recent changes log")
        
    def on_always_on_top(self):
        """Handle always on top checkbox"""
        self.root.attributes('-topmost', self.always_on_top_var.get())
        
    def on_open_debug(self):
        """Open the debug window (still separate)"""
        if self.debug_window:
            self.debug_window.show()
            
    def on_open_settings(self):
        """Navigate to settings frame instead of opening window"""
        self.show_frame('settings')
        
    def on_select_word_lists(self):
        """Navigate to word lists frame instead of opening window"""
        self.show_frame('wordlists')
    
    def setup_wordlists_ui(self, parent_frame):
        """Create the embedded word lists selection UI"""
        # Title
        title_label = tk.Label(
            parent_frame,
            text="Word List Selection",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0'
        )
        title_label.pack(pady=20)
        
        # Main container with two panes
        main_paned = tk.PanedWindow(parent_frame, orient=tk.HORIZONTAL, bg='#f0f0f0')
        main_paned.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left pane - checkboxes
        left_frame = tk.Frame(main_paned, bg='#f0f0f0')
        main_paned.add(left_frame, minsize=300)
        
        tk.Label(
            left_frame,
            text="Select Word Lists:",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0'
        ).pack(anchor='w', pady=(0, 10))
        
        # Scrollable checkbox area
        checkbox_frame = tk.Frame(left_frame, bg='#f0f0f0')
        checkbox_frame.pack(fill='both', expand=True)
        
        # Get wordlist info
        wordlist_info = self.word_filter.get_wordlist_info()
        self.wordlist_check_vars = {}
        
        for filename, info in wordlist_info.items():
            var = tk.BooleanVar()
            var.set(info['selected'])
            self.wordlist_check_vars[filename] = var
            
            cb = tk.Checkbutton(
                checkbox_frame,
                text=f"{filename} ({info['count']} words)",
                variable=var,
                command=self.on_wordlist_selection_changed,
                bg='#f0f0f0',
                anchor='w'
            )
            cb.pack(fill='x', pady=2)
        
        # Right pane - preview
        right_frame = tk.Frame(main_paned, bg='#f0f0f0')
        main_paned.add(right_frame, minsize=350)
        
        tk.Label(
            right_frame,
            text="Word Preview:",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0'
        ).pack(anchor='w', pady=(0, 10))
        
        # Scrollable text area for preview
        text_frame = tk.Frame(right_frame, bg='#f0f0f0')
        text_frame.pack(fill='both', expand=True)
        
        # Scrollbars
        v_scrollbar = tk.Scrollbar(text_frame, orient='vertical')
        h_scrollbar = tk.Scrollbar(text_frame, orient='horizontal')
        
        self.wordlist_preview_text = tk.Text(
            text_frame,
            font=('Arial', 9),
            wrap='none',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        v_scrollbar.config(command=self.wordlist_preview_text.yview)
        h_scrollbar.config(command=self.wordlist_preview_text.xview)
        
        # Pack scrollbars and text widget
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        self.wordlist_preview_text.pack(side='left', fill='both', expand=True)
        
        # Update initial preview
        self.update_wordlist_preview()
        
    def on_wordlist_selection_changed(self):
        """Handle wordlist checkbox selection changes"""
        # Get selected files
        selected_files = [
            filename for filename, var in self.wordlist_check_vars.items()
            if var.get()
        ]
        
        # Update word filter
        self.word_filter.update_selected_wordlists(selected_files)
        
        # Update preview
        self.update_wordlist_preview()
        
        # Update status bar in main view
        if hasattr(self, 'status_bar'):
            self.status_bar.config(text=f"Ready - {self.word_filter.get_word_count()} words loaded")
        
    def update_wordlist_preview(self):
        """Update the word list preview"""
        # Get selected files
        selected_files = [
            filename for filename, var in self.wordlist_check_vars.items()
            if var.get()
        ]
        
        if not selected_files:
            self.wordlist_preview_text.delete(1.0, tk.END)
            self.wordlist_preview_text.insert(1.0, "No word lists selected")
            return
            
        # Get words from selected lists
        words = []
        for filename in selected_files:
            file_words = self.word_filter.get_words_from_file(filename)
            words.extend(file_words)
        
        # Remove duplicates and sort
        words = sorted(list(set(words)))
        
        # Update text widget
        self.wordlist_preview_text.delete(1.0, tk.END)
        self.wordlist_preview_text.insert(1.0, '\n'.join(words[:1000]))  # Limit to first 1000 for performance
        
        if len(words) > 1000:
            self.wordlist_preview_text.insert(tk.END, f"\n\n... and {len(words) - 1000} more words")
            
    def on_word_changed(self, event=None):
        """Handle word input changes"""
        word = self.word_entry.get()
        self.length_label.config(text=str(len(word)))
        self.filter_words(word)
        
    def on_length_plus(self):
        """Add current word to user wordlist"""
        word = self.word_entry.get().strip()
        if word:
            if self.word_filter.add_user_word(word):
                self.status_bar.config(text=f"Added '{word}' to wordlist")
                self.filter_words(word)  # Refresh results
                self._flash_entry("green")
            else:
                self.status_bar.config(text=f"'{word}' already exists in wordlist")
                self._flash_entry("red")
        
    def on_length_minus(self):
        """Remove current word from user wordlist"""
        word = self.word_entry.get().strip()
        if word:
            if self.word_filter.remove_user_word(word):
                self.status_bar.config(text=f"Removed '{word}' from wordlist")
                self.filter_words(word)  # Refresh results
                self._flash_entry("orange")
            else:
                self.status_bar.config(text=f"'{word}' not found in user wordlist")
                self._flash_entry("red")
    
    def _flash_entry(self, color="red"):
        """Flash the entry field to provide visual feedback"""
        original_bg = self.word_entry.cget("bg")
        self.word_entry.config(bg=color)
        self.root.after(150, lambda: self.word_entry.config(bg="white"))
        self.root.after(300, lambda: self.word_entry.config(bg=color))
        self.root.after(450, lambda: self.word_entry.config(bg=original_bg))
    
    def filter_words(self, pattern):
        """Filter word list based on pattern"""
        self.results_listbox.delete(0, tk.END)
        
        # Determine matches: prefix or wildcard search, or show all if empty
        if pattern:
            matches = self.word_filter.filter_words(pattern)
            status_text = f"Selected 1 of {len(matches)} items" if matches else "No matches found"
        else:
            # Show all loaded words when no pattern entered
            matches = self.word_filter.get_combined_wordlist()
            status_text = f"Showing all {len(matches)} words loaded"

        # Populate results
        for word in matches:
            self.results_listbox.insert(tk.END, word)
        if matches:
            self.results_listbox.selection_set(0)
        # Update status bar
        self.status_bar.config(text=status_text)
            
    def _on_wordlists_updated(self):
        """Callback when wordlists are updated"""
        # Refresh the current search results
        current_pattern = self.word_entry.get()
        self.filter_words(current_pattern)
        self.status_bar.config(text=f"Wordlists updated - {self.word_filter.get_word_count()} words loaded")
    
    def init_debug_window(self):
        """Initialize the debug window for development"""
        try:
            self.debug_window = DebugWindow()
            print("[DEBUG] Debug window initialized")
        except Exception as e:
            print(f"[DEBUG] Failed to initialize debug window: {e}")
            self.debug_window = None
    
    def run(self):
        """Start the application"""
        self.root.mainloop()
