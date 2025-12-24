import tkinter as tk
from typing import Optional


class SearchInputFrame:
    """Search input frame component"""

    def __init__(self, parent, word_filter, filter_words_callback, status_bar, flash_entry_callback):
        self.parent = parent
        self.word_filter = word_filter
        self.filter_words_callback = filter_words_callback
        self.status_bar = status_bar
        self.flash_entry_callback = flash_entry_callback

        self.word_entry: Optional[tk.Entry] = None
        self.length_label: Optional[tk.Label] = None
        self.plus_btn: Optional[tk.Button] = None
        self.minus_btn: Optional[tk.Button] = None

        self.setup_input_frame()

    def setup_input_frame(self):
        """Create the word input frame"""
        input_frame = tk.Frame(self.parent, bg='#f0f0f0')
        input_frame.pack(side='bottom', fill='x', padx=10, pady=5)

        tk.Label(
            input_frame,
            text="Enter obfuscated word (e.g. dr_w_ng):",
            bg='#f0f0f0',
            font=('Arial', 10)
        ).pack(side='left')

        # Word input with length controls
        word_input_frame = tk.Frame(input_frame, bg='#f0f0f0')
        word_input_frame.pack(side='right')

        self.word_entry = tk.Entry(
            word_input_frame,
            font=('Arial', 12),
            width=17
        )
        self.word_entry.pack(side='left', padx=1)
        self.word_entry.bind('<KeyRelease>', self.on_word_changed)
        self.word_entry.bind('<FocusIn>', self.on_entry_focus_in)
        self.word_entry.bind('<Up>', self.on_entry_arrow_up)
        self.word_entry.bind('<Down>', self.on_entry_arrow_down)
        self.word_entry.bind('<Return>', self.on_entry_enter)

        # Length display as plain text
        self.length_label = tk.Label(
            word_input_frame,
            text="",
            bg='#f0f0f0',
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

    def on_entry_focus_in(self, event=None):
        """Handle input box gaining focus - select all text for easy replacement"""
        if self.word_entry.get():  # type: ignore  # Only select if there's text
            self.word_entry.select_range(0, tk.END)  # type: ignore

    def on_entry_arrow_up(self, event=None):
        """Handle up arrow in input - navigate results list"""
        # This will be handled by the main window or results frame
        return 'break'

    def on_entry_arrow_down(self, event=None):
        """Handle down arrow in input - navigate results list"""
        # This will be handled by the main window or results frame
        return 'break'

    def on_entry_enter(self, event=None):
        """Handle Enter key in input - copy selected word to clipboard or select first result"""
        # This will be handled by the main window or results frame
        return 'break'

    def on_word_changed(self, event=None):
        """Handle word input changes"""
        # Ignore arrow key releases to prevent interfering with navigation
        if event and event.keysym in ('Up', 'Down'):
            return

        word = self.word_entry.get()  # type: ignore
        # Calculate per-word lengths
        word_lengths = [str(len(w)) for w in word.split()]
        self.length_label.config(text=", ".join(word_lengths))  # type: ignore
        self.filter_words_callback(word)

    def on_length_plus(self):
        """Add current word to user wordlist"""
        word = self.word_entry.get().strip()  # type: ignore
        if word:
            if self.word_filter.add_user_word(word):
                self.status_bar.config(text=f"Added '{word}' to wordlist")
                self.filter_words_callback(word)  # Refresh results
                self.flash_entry_callback("green")
            else:
                self.status_bar.config(text=f"'{word}' already exists in wordlist")
                self.flash_entry_callback("red")

    def on_length_minus(self):
        """Remove current word from user wordlist"""
        word = self.word_entry.get().strip()  # type: ignore
        if word:
            if self.word_filter.remove_user_word(word):
                self.status_bar.config(text=f"Removed '{word}' from wordlist")
                self.filter_words_callback(word)  # Refresh results
                self.flash_entry_callback("orange")
            else:
                self.status_bar.config(text=f"'{word}' not found in user wordlist")
                self.flash_entry_callback("red")

    def get_word_entry(self):
        return self.word_entry