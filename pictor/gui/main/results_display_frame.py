import tkinter as tk
from typing import Optional


class ResultsDisplayFrame:
    """Results display frame component"""

    def __init__(self, parent, word_filter, status_bar, exact_length_match=False):
        self.parent = parent
        self.word_filter = word_filter
        self.status_bar = status_bar
        self.exact_length_match = exact_length_match

        self.results_listbox: Optional[tk.Listbox] = None
        self.setup_results_frame()

    def setup_results_frame(self):
        """Create the results listbox frame"""
        results_frame = tk.Frame(self.parent, bg='#f0f0f0')
        results_frame.pack(side='top', fill='both', expand=False, padx=10, pady=5)

        # Create listbox with scrollbar
        listbox_frame = tk.Frame(results_frame)
        listbox_frame.pack(fill='both', expand=True)

        self.results_listbox = tk.Listbox(
            listbox_frame,
            font=('Arial', 11),
            height=5
        )

        scrollbar = tk.Scrollbar(listbox_frame, orient='vertical')
        self.results_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.results_listbox.yview)

        self.results_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def filter_words(self, pattern):
        """Filter word list based on pattern and sort results by length (shortest to longest)"""
        # Remember the currently selected word before clearing
        selected_word = None
        selection = self.results_listbox.curselection()  # type: ignore
        if selection:
            selected_word = self.results_listbox.get(selection[0])  # type: ignore

        self.results_listbox.delete(0, tk.END)  # type: ignore

        # Determine matches: prefix or wildcard search, or show all if empty
        mode_text = ""
        if pattern:
            matches = self.word_filter.filter_words(pattern, exact_length=self.exact_length_match)
            mode_text = " (exact length)" if self.exact_length_match else ""
            status_text = f"Selected 1 of {len(matches)} items{mode_text}" if matches else f"No matches found{mode_text}"
        else:
            # Show all loaded words when no pattern entered
            matches = self.word_filter.get_combined_wordlist()
            status_text = f"Showing all {len(matches)} words loaded"

        # Sort matches by length (shortest to longest), then alphabetically for ties
        matches = sorted(matches, key=lambda w: (len(w), w.lower()))

        # Populate results
        for word in matches:
            self.results_listbox.insert(tk.END, word)  # type: ignore
        
        # Restore selection if the word is still in the list
        if selected_word and selected_word in matches:
            index = matches.index(selected_word)
            self.results_listbox.selection_set(index)  # type: ignore
            self.results_listbox.see(index)  # type: ignore
            status_text = f"Selected {index + 1} of {len(matches)} items{mode_text if pattern else ''}"
        elif matches:
            self.results_listbox.selection_set(0)  # type: ignore
            self.results_listbox.see(0)  # type: ignore

    def get_results_listbox(self):
        return self.results_listbox

    def set_exact_length_match(self, value):
        self.exact_length_match = value