import tkinter as tk
from tkinter import ttk, messagebox
from ..utils.word_filtering import WordFilter


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
        self.root.geometry("900x700")  # Increased default size for full settings visibility
        self.root.configure(bg='#f0f0f0')

        # Initialize word filter
        self.word_filter = WordFilter()

        # Frame management
        self.current_frame = None
        self.frames = {}

        # Always on top variable (now managed through settings)
        self.always_on_top_var = tk.BooleanVar()

        # Track last key event for focus logic
        self._last_key_was_tab = False
        self.root.bind_all('<KeyPress>', self._on_any_keypress, add='+')

        self.setup_navigation()
        self.setup_frames()
        self.show_frame('main')

        # Set up focus events for auto-focus on input
        self.setup_focus_events()

        # Set up keyboard shortcuts
        self.setup_keyboard_shortcuts()

    def _on_any_keypress(self, event):
        # Track if Tab or Shift+Tab was pressed
        if event.keysym == 'Tab':
            self._last_key_was_tab = True
        else:
            self._last_key_was_tab = False
        
    def setup_keyboard_shortcuts(self):
        """Set up global keyboard shortcuts"""
        # Ctrl+R to restart app
        self.root.bind('<Control-r>', lambda e: self.on_restart_app())
        self.root.bind('<Control-R>', lambda e: self.on_restart_app())

        # Ctrl+C to copy selected word to clipboard
        self.root.bind('<Control-c>', lambda e: self.on_copy_selected())
        self.root.bind('<Control-C>', lambda e: self.on_copy_selected())

        # Ctrl+F to focus search input box
        self.root.bind('<Control-f>', lambda e: self.focus_search_input())
        self.root.bind('<Control-F>', lambda e: self.focus_search_input())

    def focus_search_input(self):
        """Focus the search input box (word_entry)"""
        if hasattr(self, 'word_entry') and self.word_entry.winfo_exists():
            self.word_entry.focus_set()
        
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
        
    def setup_focus_events(self):
        """Set up focus events for auto-focus functionality"""
        # Only bind click events for background auto-focus
        self.root.bind('<Button-1>', self.on_window_click)
        
    # Removed on_window_focus_in: no longer needed for auto-focus
            
    def on_window_click(self, event=None):
        """Handle window clicks - maintain focus on input for easy typing only if background is clicked"""
        # Only if we're on main frame and clicked outside the input area
        if (event and self.current_frame == 'main' and 
            hasattr(self, 'word_entry') and 
            self.word_entry.winfo_exists()):
            clicked_widget = event.widget
            # Only focus input if background (container or parent_frame) is clicked
            if clicked_widget == self.container or clicked_widget == self.frames['main']:
                self.root.after(10, lambda: self.word_entry.focus_set())
        
    def setup_frames(self):
        """Initialize all the main frames"""
        # Container for all frames
        self.container = tk.Frame(self.root, bg='#f0f0f0')
        self.container.pack(fill='both', expand=True)
        
        # Main frame (current functionality)
        self.frames['main'] = self.create_main_frame()
        
        # Settings frame (embedded settings)
        self.frames['settings'] = self.create_settings_frame()
        
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
        # Only 'main' frame has a navigation button now
        if active_frame == 'main':
            self.main_nav_btn.config(bg='#4CAF50', fg='white')
        else:
            self.main_nav_btn.config(bg='#e0e0e0', fg='black')
                
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
        
    def setup_main_ui(self, parent_frame):
        """Create the main UI elements"""
        
        # Results listbox (moved to top)
        results_frame = tk.Frame(parent_frame, bg='#f0f0f0')
        results_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
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
        
        # Word input frame (moved to bottom)
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
        self.word_entry.bind('<FocusIn>', self.on_entry_focus_in)
        self.word_entry.bind('<Up>', self.on_entry_arrow_up)
        self.word_entry.bind('<Down>', self.on_entry_arrow_down)
        self.word_entry.bind('<Return>', self.on_entry_enter)
        
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
        
        # Set initial focus to input box
        self.root.after(100, lambda: self.word_entry.focus_set())
        
    def on_entry_focus_in(self, event=None):
        """Handle input box gaining focus - select all text for easy replacement"""
        if self.word_entry.get():  # Only select if there's text
            self.word_entry.select_range(0, tk.END)
            
    def on_entry_arrow_up(self, event=None):
        """Handle up arrow in input - navigate results list"""
        if hasattr(self, 'results_listbox'):
            current_selection = self.results_listbox.curselection()
            if current_selection:
                current_index = current_selection[0]
                if current_index > 0:
                    self.results_listbox.selection_clear(0, tk.END)
                    self.results_listbox.selection_set(current_index - 1)
                    self.results_listbox.see(current_index - 1)
            else:
                # No selection, select last item
                last_index = self.results_listbox.size() - 1
                if last_index >= 0:
                    self.results_listbox.selection_set(last_index)
                    self.results_listbox.see(last_index)
        return 'break'  # Prevent default behavior
        
    def on_entry_arrow_down(self, event=None):
        """Handle down arrow in input - navigate results list"""
        if hasattr(self, 'results_listbox'):
            current_selection = self.results_listbox.curselection()
            if current_selection:
                current_index = current_selection[0]
                max_index = self.results_listbox.size() - 1
                if current_index < max_index:
                    self.results_listbox.selection_clear(0, tk.END)
                    self.results_listbox.selection_set(current_index + 1)
                    self.results_listbox.see(current_index + 1)
            else:
                # No selection, select first item
                if self.results_listbox.size() > 0:
                    self.results_listbox.selection_set(0)
                    self.results_listbox.see(0)
        return 'break'  # Prevent default behavior
        
    def on_entry_enter(self, event=None):
        """Handle Enter key in input - copy selected word to clipboard or select first result, with workaround for selection jumping bug"""
        if hasattr(self, 'results_listbox'):
            # Temporarily unbind KeyRelease to prevent interference
            self.word_entry.unbind('<KeyRelease>')

            current_selection = self.results_listbox.curselection()
            if current_selection:
                selected_word = self.results_listbox.get(current_selection[0])
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_word)
                self.status_bar.config(text=f"Copied '{selected_word}' to clipboard")
            else:
                if self.results_listbox.size() > 0:
                    self.results_listbox.selection_set(0)
                    self.results_listbox.see(0)

            # Re-bind KeyRelease after a delay, but only if input still exists
            def rebind_if_exists():
                if hasattr(self, 'word_entry') and self.word_entry.winfo_exists():
                    self.word_entry.bind('<KeyRelease>', self.on_word_changed)
            self.root.after(150, rebind_if_exists)
        return 'break'  # Prevent default behavior
        
    def on_copy_selected(self, event=None):
        """Handle Ctrl+C - copy selected word to clipboard, with workaround for selection jumping bug"""
        if (hasattr(self, 'results_listbox') and self.current_frame == 'main'):
            # Temporarily unbind KeyRelease to prevent interference
            self.word_entry.unbind('<KeyRelease>')

            current_selection = self.results_listbox.curselection()
            if current_selection:
                selected_word = self.results_listbox.get(current_selection[0])
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_word)
                self.status_bar.config(text=f"Copied '{selected_word}' to clipboard")
            else:
                if self.results_listbox.size() > 0:
                    self.results_listbox.selection_set(0)
                    self.results_listbox.see(0)
                    selected_word = self.results_listbox.get(0)
                    self.root.clipboard_clear()
                    self.root.clipboard_append(selected_word)
                    self.status_bar.config(text=f"Copied '{selected_word}' to clipboard")

            # Re-bind KeyRelease after a delay, but only if input still exists
            def rebind_if_exists():
                if hasattr(self, 'word_entry') and self.word_entry.winfo_exists():
                    self.word_entry.bind('<KeyRelease>', self.on_word_changed)
            self.root.after(150, rebind_if_exists)
            return 'break'  # Prevent default Ctrl+C behavior

        # If not on main frame or no results, allow default Ctrl+C behavior
        return None
            
    # TODO: Pin recent changes feature for future implementation (placeholder for LLM)
    def on_recent_changes(self):
        """Handle Recent Changes button click (to be implemented)"""
        messagebox.showinfo("Recent Changes", "Feature coming soon: recent changes log")
        
    def on_dev_tools(self):
        """Show developer tools menu"""
        # Create a popup menu
        dev_menu = tk.Menu(self.root, tearoff=0)
        
        # Add menu items
        dev_menu.add_command(label=" Restart App", command=self.on_restart_app)
        dev_menu.add_command(label="📋 Recent Changes", command=self.on_recent_changes)
        
        # Show the menu at the button location
        try:
            # Get button position
            x = self.dev_tools_btn.winfo_rootx()
            y = self.dev_tools_btn.winfo_rooty() + self.dev_tools_btn.winfo_height()
            dev_menu.post(x, y)
        except Exception as e:
            print(f"[DEBUG] Failed to show dev tools menu: {e}")
            # Fallback - just show recent changes
            self.on_recent_changes()
            
    def on_restart_app(self):
        """Restart the application (dev tool)"""
        try:
            import subprocess
            import sys
            import os
            
            # Close current window
            self.root.destroy()
            
            # Restart the application
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                subprocess.Popen([sys.executable])
            else:
                # Running as Python script
                subprocess.Popen([sys.executable] + sys.argv)
            
        except Exception as e:
            print(f"[DEBUG] Failed to restart application: {e}")
            messagebox.showerror("Error", f"Failed to restart application: {e}")
        
    def on_open_settings(self):
        """Navigate to settings frame instead of opening window"""
        self.show_frame('settings')
        
    def on_word_changed(self, event=None):
        """Handle word input changes"""
        # Ignore arrow key releases to prevent interfering with navigation
        if event and event.keysym in ('Up', 'Down'):
            return
            
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
    
    def run(self):
        """Start the application"""
        self.root.mainloop()
