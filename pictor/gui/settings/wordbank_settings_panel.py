"""
Wordbank Settings Panel for Pictor Settings Window
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
from pictor.utils.word_filtering import WordFilter

class WordbankSettingsPanel(tk.Frame):
    """A frame that contains the wordbank settings controls."""
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg='#f0f0f0', **kwargs)
        self.app = app
        self.check_vars = {}
        self.summary_label = None
        self.unsaved = False
        self.pending_selected = None
        self.pending_editable = None
        self.build_ui()

    def build_ui(self):
        """Create the wordbank settings UI."""
        # Create title
        title_label = tk.Label(
            self,
            text="Wordbank Settings",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0'
        )
        title_label.pack(pady=(20, 10))

        # Description
        desc_label = tk.Label(
            self,
            text="Configure word lists and wordbank settings",
            font=('Arial', 10),
            bg='#f0f0f0',
            fg='#666666'
        )
        desc_label.pack(pady=(0, 20))

        # Create scrollable frame for word list controls
        canvas = tk.Canvas(self, bg='#f0f0f0', highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=(20,0), pady=(0,10))
        scrollbar.pack(side="right", fill="y", pady=(0,10))

        # Word list selection checkboxes
        selection_label = tk.Label(
            scrollable_frame,
            text="Select Word Lists:",
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0'
        )
        selection_label.pack(anchor='w', padx=20, pady=(10, 5))

        # Get word filter from parent if available
        if hasattr(self.app, 'word_filter'):
            wordlist_info = self.app.word_filter.get_wordlist_info()

            checkbox_frame = tk.Frame(scrollable_frame, bg='#f0f0f0')
            checkbox_frame.pack(fill='x', padx=20, pady=5)

            # Initialize pending selections from current app state
            self.pending_selected = [fname for fname, info in wordlist_info.items() if info['selected']]
            self.pending_editable = self.app.settings.get('editable_wordlist', 'user_added_words.txt')

            for filename, info in wordlist_info.items():
                var = tk.BooleanVar(value=info['selected'])
                self.check_vars[filename] = var

                chk_text = f"{filename} ({info['count']} words)"

                def make_cmd_func(fname=filename):
                    return lambda: self.on_wordlist_selection_changed(fname)

                chk = tk.Checkbutton(
                    checkbox_frame,
                    text=chk_text,
                    variable=var,
                    command=make_cmd_func(),
                    bg='#f0f0f0',
                    anchor='w',
                    font=('Arial', 10)
                )
                chk.pack(fill='x', pady=2)

            # Word count summary
            self.summary_label = tk.Label(
                scrollable_frame,
                text="", # Will be updated by refresh_wordcount_display
                font=('Arial', 10, 'bold'),
                bg='#f0f0f0',
                fg='#2196F3',
                name="summary_label"
            )
            self.summary_label.pack(anchor='w', padx=20, pady=10)

            # Editable wordlist selection
            editable_label = tk.Label(
                scrollable_frame,
                text="Editable Wordlist (for + / - buttons):",
                font=('Arial', 12, 'bold'),
                bg='#f0f0f0'
            )
            editable_label.pack(anchor='w', padx=20, pady=(10, 5))

            self.editable_var = tk.StringVar(value=self.pending_editable)
            editable_options = self.app.word_filter.available_files
            self.editable_dropdown = ttk.Combobox(
                scrollable_frame,
                textvariable=self.editable_var,
                values=editable_options,
                state='readonly',
                width=30
            )
            self.editable_dropdown.pack(anchor='w', padx=20, pady=(0, 10))
            self.editable_dropdown.bind('<<ComboboxSelected>>', self.on_editable_wordlist_changed)

            # Add Open Wordlists Folder button directly after summary label
            open_wordlists_btn = tk.Button(
                scrollable_frame,
                text="Open Wordlists Folder",
                font=('Arial', 10),
                padx=10,
                pady=5,
                command=self.app.open_wordlists_folder if hasattr(self.app, 'open_wordlists_folder') else None
            )
            open_wordlists_btn.pack(anchor='e', padx=20, pady=(0, 10))
            self.refresh_wordcount_display()

            # Bottom save/cancel controls (per-tab)
            bottom_btn_frame = tk.Frame(self, bg='#f0f0f0')
            bottom_btn_frame.pack(fill='x', side='bottom', padx=10, pady=8)

            tk.Button(
                bottom_btn_frame,
                text="Cancel",
                command=self.discard_changes,
                padx=12
            ).pack(side='right', padx=6)

            tk.Button(
                bottom_btn_frame,
                text="Save",
                command=self.save_changes,
                bg='#4CAF50',
                fg='white',
                padx=12
            ).pack(side='right', padx=6)
            
    def on_wordlist_selection_changed(self, filename=None):
        """Handle wordlist selection changes."""
        # Mark pending changes and do not apply until Save
        selected_lists = [fname for fname, var in self.check_vars.items() if var.get()]
        self.pending_selected = selected_lists
        self.unsaved = True
        # Update preview using a temporary filter
        try:
            temp = WordFilter(self.app.word_filter.wordlists_folder)
            temp.update_selected_wordlists(self.pending_selected)
            total = len(temp.get_combined_wordlist())
        except Exception:
            total = 0
        if self.summary_label:
            self.summary_label.config(text=f"Total selected words: {total}")
            
    def on_editable_wordlist_changed(self, event=None):
        """Handle editable wordlist selection change."""
        selected = self.editable_var.get()
        self.pending_editable = selected
        self.unsaved = True
            
    def refresh_wordcount_display(self):
        """Refresh the word count display."""
        if self.summary_label and hasattr(self.app, 'word_filter'):
            try:
                if self.pending_selected is not None:
                    temp = WordFilter(self.app.word_filter.wordlists_folder)
                    temp.update_selected_wordlists(self.pending_selected)
                    total_words = len(temp.get_combined_wordlist())
                else:
                    wordlist_info = self.app.word_filter.get_wordlist_info()
                    total_words = sum(info['count'] for info in wordlist_info.values() if info['selected'])
            except Exception:
                total_words = 0
            self.summary_label.config(text=f"Total selected words: {total_words}")

    # --- Save / Discard helpers ---
    def has_unsaved_changes(self):
        return bool(self.unsaved)

    def save_changes(self):
        """Apply pending selections to the main app and persist settings."""
        try:
            if self.pending_selected is not None:
                self.app.word_filter.update_selected_wordlists(self.pending_selected)
                self.app.settings.set('selected_wordlists', self.pending_selected)
            if self.pending_editable is not None:
                self.app.settings.set('editable_wordlist', self.pending_editable)
                wordlists_folder = self.app.word_filter.wordlists_folder
                new_user_words_file = os.path.join(wordlists_folder, self.pending_editable)
                self.app.word_filter.user_words_file = new_user_words_file
            # Persist settings
            if hasattr(self.app, 'settings') and hasattr(self.app.settings, 'save_settings'):
                self.app.settings.save_settings()
            # Notify app
            if hasattr(self.app, '_on_wordlists_updated'):
                self.app._on_wordlists_updated()
            self.unsaved = False
            messagebox.showinfo("Saved", "Wordbank settings saved.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save wordbank settings:\n{e}")

    def discard_changes(self):
        """Discard pending changes and revert UI to current app state."""
        if hasattr(self.app, 'word_filter'):
            info = self.app.word_filter.get_wordlist_info()
            for fname, var in self.check_vars.items():
                var.set(info.get(fname, {}).get('selected', False))
            self.editable_var.set(self.app.settings.get('editable_wordlist', 'user_added_words.txt'))
        self.pending_selected = None
        self.pending_editable = None
        self.unsaved = False
        self.refresh_wordcount_display()
