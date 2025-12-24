import tkinter as tk
from ...utils.word_filtering import WordFilter  # type: ignore


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