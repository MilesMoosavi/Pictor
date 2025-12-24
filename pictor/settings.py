import json
import os

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")
DEFAULT_SETTINGS = {
    "window_geometry": None,
    "always_on_top": False,
    "last_open_category": None,
    "last_search_pattern": "",
    "last_selected_result_index": 0,
    "selected_wordlists": ["user_added_words.txt"],
    "editable_wordlist": "user_added_words.txt",
    "theme": "light",
    "keyboard_shortcuts": {},
}

class SettingsManager:
    def __init__(self, path=SETTINGS_PATH):
        self.path = path
        self.settings = DEFAULT_SETTINGS.copy()
        self.load_settings()

    def load_settings(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.settings.update(json.load(f))
            except Exception as e:
                print(f"Failed to load settings: {e}")

    def save_settings(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value

    def reset_to_defaults(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.save_settings()

"""

Rough structure:

On app load:
 - Check the last saved window geometry if any (use default otherwise)
    - This includes checking as to whether the previous app window was loaded on a different monitor, 
    and if that old monitor is still currently active or not.
    If still active, load on that monitor with that exact geometry.
    If not, load on the monitor in which the app was lauched with adjusted geometry according to the active monitor's screen resolution.

Load wordbank:
 - Load any previously saved user selected word options from `pictor/wordlists/*`
    - Load `user_added_words.txt` from `pictor/wordlists/user_added_words.txt` by default if nothing else is selected

Load the main page

 Future Settings
 - Will update soon with more info

"""