import tkinter as tk
from tkinter import messagebox
import os
from typing import Optional
from ...utils.word_filtering import WordFilter  # type: ignore
from ...settings import SettingsManager  # type: ignore
from .navigation_bar import NavigationBar
from .search_input_frame import SearchInputFrame
from .results_display_frame import ResultsDisplayFrame
from .wordlist_selector import WordListSelectionWindow


class WordMatcherWindow:
    """Main window for word pattern matching"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Word Matcher")
        self.root.geometry("550x200+0+0")  # Always open in top-left of primary monitor
        self.root.configure(bg='#f0f0f0')

        # Set a minimum window size to protect the query area
        self.root.minsize(550, 200)  # Set minimum width to 550px

        # Initialize settings
        self.settings = SettingsManager()

        # Initialize word filter
        editable_file = self.settings.get('editable_wordlist', 'user_added_words.txt') or 'user_added_words.txt'
        wordlists_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "wordlists")
        user_words_path = os.path.join(wordlists_folder, editable_file)
        self.word_filter = WordFilter(user_words_file=user_words_path)

        # Frame management
        self.current_frame = None
        self.frames = {}

        # Always on top variable (now managed through settings)
        self.always_on_top_var = tk.BooleanVar()

        # Exact length match toggle
        self.exact_length_match = False

        # Track last key event for focus logic
        self._last_key_was_tab = False
        self.root.bind_all('<KeyPress>', self._on_any_keypress, add='+')

        # Initialize components
        self.navigation_bar: Optional[NavigationBar] = None
        self.search_input_frame: Optional[SearchInputFrame] = None
        self.results_display_frame: Optional[ResultsDisplayFrame] = None
        self.status_bar: Optional[tk.Label] = None
        self.container: Optional[tk.Frame] = None

        self.navigation_bar = NavigationBar(
            self.root,
            self.show_frame,
            self.on_recent_changes,
            self.on_dev_tools,
            self.on_open_settings
        )

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

        # Ctrl+/ to toggle exact length matching
        self.root.bind('<Control-slash>', lambda e: self.toggle_exact_length_match())
        self.root.bind('<Control-question>', lambda e: self.toggle_exact_length_match())  # Shift+Ctrl+/

    def toggle_exact_length_match(self):
        """Toggle exact length matching mode"""
        self.exact_length_match = not self.exact_length_match
        # Refresh the current search results
        current_pattern = self.search_input_frame.get_word_entry().get()  # type: ignore
        self.results_display_frame.set_exact_length_match(self.exact_length_match)  # type: ignore
        self.results_display_frame.filter_words(current_pattern)  # type: ignore

    def open_wordlists_folder(self):
        """Open the wordlists folder in file explorer"""
        import os
        # Get absolute path to wordlists folder
        wordlists_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'wordlists'))
        os.startfile(wordlists_path)

    def focus_search_input(self):
        """Focus the search input box (word_entry)"""
        word_entry = self.search_input_frame.get_word_entry()  # type: ignore
        if word_entry and word_entry.winfo_exists():
            word_entry.focus_set()

    def setup_focus_events(self):
        """Set up focus events for auto-focus functionality"""
        # Only bind click events for background auto-focus
        self.root.bind('<Button-1>', self.on_window_click)

    def on_window_click(self, event=None):
        """Handle window clicks - maintain focus on input for easy typing only if background is clicked"""
        # Only if we're on main frame and clicked outside the input area
        if (event and self.current_frame == 'main' and
            self.search_input_frame.get_word_entry() and  # type: ignore
            self.search_input_frame.get_word_entry().winfo_exists()):  # type: ignore
            clicked_widget = event.widget
            # Only focus input if background (container or parent_frame) is clicked
            if clicked_widget == self.container or clicked_widget == self.frames['main']:
                self.root.after(10, lambda: self.search_input_frame.get_word_entry().focus_set())  # type: ignore

    def setup_frames(self):
        """Initialize all the main frames"""
        # Container for all frames
        self.container = tk.Frame(self.root, bg='#f0f0f0')
        self.container.pack(fill='both', expand=True)

        # Main frame (current functionality)
        self.frames['main'] = self.create_main_frame()

        # No embedded settings frame; settings will open as a popup

    def show_frame(self, frame_name):
        """Show the specified frame and hide others (settings frame removed)"""
        if frame_name not in self.frames:
            return
        if self.current_frame:
            self.frames[self.current_frame].pack_forget()
        self.frames[frame_name].pack(fill='both', expand=True)
        self.current_frame = frame_name
        self.navigation_bar.update_nav_buttons(frame_name)  # type: ignore

    def create_main_frame(self):
        """Create the main functionality frame"""
        main_frame = tk.Frame(self.container, bg='#f0f0f0')

        # Status bar (packed second from bottom)
        self.status_bar = tk.Label(
            main_frame,
            text="Ready",
            relief='sunken',
            anchor='w',
            bg='#f0f0f0',
            font=('Arial', 9)
        )
        self.status_bar.pack(side='bottom', fill='x')

        # Initialize components
        self.results_display_frame = ResultsDisplayFrame(main_frame, self.word_filter, self.status_bar, self.exact_length_match)
        self.search_input_frame = SearchInputFrame(
            main_frame,
            self.word_filter,
            self.results_display_frame.filter_words,
            self.status_bar,
            self._flash_entry
        )

        # Update status bar text
        self.status_bar.config(text=f"Ready - {self.word_filter.get_word_count()} words loaded")

        # Populate initial results (show all words)
        self.results_display_frame.filter_words('')

        # Set initial focus to input box
        self.root.after(100, lambda: self.search_input_frame.get_word_entry().focus_set())  # type: ignore

        return main_frame

    def on_entry_arrow_up(self, event=None):
        """Handle up arrow in input - navigate results list"""
        results_listbox = self.results_display_frame.get_results_listbox()  # type: ignore
        if results_listbox:
            current_selection = results_listbox.curselection()
            if current_selection:
                current_index = current_selection[0]
                if current_index > 0:
                    results_listbox.selection_clear(0, tk.END)
                    results_listbox.selection_set(current_index - 1)
                    results_listbox.see(current_index - 1)
            else:
                # No selection, select last item
                last_index = results_listbox.size() - 1
                if last_index >= 0:
                    results_listbox.selection_set(last_index)
                    results_listbox.see(last_index)
        return 'break'  # Prevent default behavior

    def on_entry_arrow_down(self, event=None):
        """Handle down arrow in input - navigate results list"""
        results_listbox = self.results_display_frame.get_results_listbox()  # type: ignore
        if results_listbox:
            current_selection = results_listbox.curselection()
            if current_selection:
                current_index = current_selection[0]
                max_index = results_listbox.size() - 1
                if current_index < max_index:
                    results_listbox.selection_clear(0, tk.END)
                    results_listbox.selection_set(current_index + 1)
                    results_listbox.see(current_index + 1)
            else:
                # No selection, select first item
                if results_listbox.size() > 0:
                    results_listbox.selection_set(0)
                    results_listbox.see(0)
        return 'break'  # Prevent default behavior

    def on_entry_enter(self, event=None):
        """Handle Enter key in input - copy selected word to clipboard or select first result, with workaround for selection jumping bug"""
        results_listbox = self.results_display_frame.get_results_listbox()  # type: ignore
        if results_listbox:
            # Temporarily unbind KeyRelease to prevent interference
            word_entry = self.search_input_frame.get_word_entry()  # type: ignore
            word_entry.unbind('<KeyRelease>')  # type: ignore

            current_selection = results_listbox.curselection()  # type: ignore
            if current_selection:
                selected_word = results_listbox.get(current_selection[0])  # type: ignore
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_word)
                self.status_bar.config(text=f"Copied '{selected_word}' to clipboard")  # type: ignore
            else:
                if results_listbox.size() > 0:  # type: ignore
                    results_listbox.selection_set(0)  # type: ignore
                    results_listbox.see(0)  # type: ignore

            # Re-bind KeyRelease after a delay, but only if input still exists
            def rebind_if_exists():
                if word_entry and word_entry.winfo_exists():
                    word_entry.bind('<KeyRelease>', self.search_input_frame.on_word_changed)  # type: ignore
            self.root.after(150, rebind_if_exists)
        return 'break'  # Prevent default behavior

    def on_copy_selected(self, event=None):
        """Handle Ctrl+C - copy selected word to clipboard, with workaround for selection jumping bug"""
        if (self.results_display_frame.get_results_listbox() and self.current_frame == 'main'):  # type: ignore
            # Temporarily unbind KeyRelease to prevent interference
            word_entry = self.search_input_frame.get_word_entry()  # type: ignore
            word_entry.unbind('<KeyRelease>')  # type: ignore

            results_listbox = self.results_display_frame.get_results_listbox()  # type: ignore
            current_selection = results_listbox.curselection()  # type: ignore
            if current_selection:
                selected_word = results_listbox.get(current_selection[0])  # type: ignore
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_word)
                self.status_bar.config(text=f"Copied '{selected_word}' to clipboard")  # type: ignore
            else:
                if results_listbox.size() > 0:  # type: ignore
                    results_listbox.selection_set(0)  # type: ignore
                    results_listbox.see(0)  # type: ignore
                    selected_word = results_listbox.get(0)  # type: ignore
                    self.root.clipboard_clear()
                    self.root.clipboard_append(selected_word)
                    self.status_bar.config(text=f"Copied '{selected_word}' to clipboard")  # type: ignore

            # Re-bind KeyRelease after a delay, but only if input still exists
            def rebind_if_exists():
                if word_entry and word_entry.winfo_exists():
                    word_entry.bind('<KeyRelease>', self.search_input_frame.on_word_changed)  # type: ignore
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
            x = self.navigation_bar.dev_tools_btn.winfo_rootx()  # type: ignore
            y = self.navigation_bar.dev_tools_btn.winfo_rooty() + self.navigation_bar.dev_tools_btn.winfo_height()  # type: ignore
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

            # Restart the application first
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                subprocess.Popen([sys.executable])
            else:
                # Running as Python script
                subprocess.Popen([sys.executable] + sys.argv)

            # Then close current window
            self.root.destroy()

        except Exception as e:
            print(f"[DEBUG] Failed to restart application: {e}")
            messagebox.showerror("Error", f"Failed to restart application: {e}")

    def on_open_settings(self):
        """Open the settings window as a popup"""
        from ..settings_window import SettingsWindow
        SettingsWindow(self, self.root, embedded=False)

    def _flash_entry(self, color="red"):
        """Flash the entry field to provide visual feedback"""
        word_entry = self.search_input_frame.get_word_entry()  # type: ignore
        original_bg = word_entry.cget("bg")  # type: ignore
        word_entry.config(bg=color)  # type: ignore
        self.root.after(150, lambda: word_entry.config(bg="white"))  # type: ignore
        self.root.after(300, lambda: word_entry.config(bg=color))  # type: ignore
        self.root.after(450, lambda: word_entry.config(bg=original_bg))  # type: ignore

    def _on_wordlists_updated(self):
        """Callback when wordlists are updated"""
        # Refresh the current search results
        current_pattern = self.search_input_frame.get_word_entry().get()  # type: ignore
        self.results_display_frame.filter_words(current_pattern)  # type: ignore
        self.status_bar.config(text=f"Wordlists updated - {self.word_filter.get_word_count()} words loaded")  # type: ignore

    def run(self):
        """Start the application"""
        self.root.mainloop()