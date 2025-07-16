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
        self.root.geometry("600x450")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize word filter
        self.word_filter = WordFilter()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the main UI elements"""
        
        # Top frame with buttons
        top_frame = tk.Frame(self.root, bg='#f0f0f0')
        top_frame.pack(fill='x', padx=10, pady=5)
        
        # Left side buttons
        left_buttons_frame = tk.Frame(top_frame, bg='#f0f0f0')
        left_buttons_frame.pack(side='left')
        
        self.word_lists_btn = tk.Button(
            left_buttons_frame, 
            text="Select Word Lists",
            command=self.on_select_word_lists,
            relief='raised',
            padx=15, pady=5
        )
        self.word_lists_btn.pack(side='left', padx=(0, 5))
        
        self.recent_changes_btn = tk.Button(
            left_buttons_frame,
            text="Recent Changes", 
            command=self.on_recent_changes,
            relief='raised',
            padx=15, pady=5
        )
        self.recent_changes_btn.pack(side='left', padx=5)
        
        # Right side controls
        right_frame = tk.Frame(top_frame, bg='#f0f0f0')
        right_frame.pack(side='right')
        
        self.always_on_top_var = tk.BooleanVar()
        self.always_on_top_cb = tk.Checkbutton(
            right_frame,
            text="Always on Top",
            variable=self.always_on_top_var,
            command=self.on_always_on_top,
            bg='#f0f0f0'
        )
        self.always_on_top_cb.pack(side='left', padx=5)
        
        # Settings gear button
        self.settings_btn = tk.Button(
            right_frame,
            text="⚙",
            command=self.on_open_settings,
            font=('Arial', 12),
            width=3,
            relief='raised'
        )
        self.settings_btn.pack(side='right', padx=(10, 0))
        
        # Word input frame
        input_frame = tk.Frame(self.root, bg='#f0f0f0')
        input_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(
            input_frame, 
            text="Enter obfuscated word:",
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
        results_frame = tk.Frame(self.root, bg='#f0f0f0')
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
            self.root,
            text=f"Ready - {self.word_filter.get_word_count()} words loaded",
            relief='sunken',
            anchor='w',
            bg='#f0f0f0',
            font=('Arial', 9)
        )
        self.status_bar.pack(side='bottom', fill='x')
        # Populate initial results (show all words)
        self.filter_words('')
        
    def on_select_word_lists(self):
        """Handle word lists button click - show enhanced selection window"""
        WordListSelectionWindow(self.root, self.word_filter, self._on_wordlists_updated)
        
    def on_recent_changes(self):
        """Handle recent changes button click"""
        messagebox.showinfo("Recent Changes", "Recent Changes clicked (not implemented yet)")
        
    def on_always_on_top(self):
        """Handle always on top checkbox"""
        self.root.attributes('-topmost', self.always_on_top_var.get())
        
    def on_open_settings(self):
        """Open the capture settings window"""
        from .capture_settings import CaptureSettingsWindow
        capture_window = CaptureSettingsWindow(self.root)
        
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
    
    def run(self):
        """Start the application"""
        self.root.mainloop()
