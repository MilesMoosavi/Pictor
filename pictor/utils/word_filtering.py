import re
import os
import json


class WordFilter:
    """Handles word filtering and pattern matching with persistent user wordlists"""
    
    def __init__(self, wordlists_folder=None):
        self.wordlists_folder = wordlists_folder or self._get_wordlists_folder()
        self.user_words_file = os.path.join(self.wordlists_folder, "user_added_words.txt")
        self.settings_file = os.path.join(os.path.dirname(self.wordlists_folder), "settings.json")
        
        # Initialize available wordlist files
        self.available_files = self._get_available_wordlists()
        self.selected_files = self._load_selected_files()
        
        # Load combined word list
        self.word_set = set()
        self.word_list = []
        self._load_all_wordlists()
        
    def _get_wordlists_folder(self):
        """Get the wordlists folder path"""
        # Use wordlists folder inside the pictor package
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(script_dir, "wordlists")
    
    def _get_available_wordlists(self):
        """Get all available .txt wordlist files"""
        if not os.path.exists(self.wordlists_folder):
            os.makedirs(self.wordlists_folder, exist_ok=True)
            # Create default user words file
            with open(self.user_words_file, 'w') as f:
                f.write("")
            return ["user_added_words.txt"]
            
        return [f for f in os.listdir(self.wordlists_folder) if f.endswith('.txt')]
    
    def _load_selected_files(self):
        """Load previously selected wordlist files from settings"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get('selected_wordlists', self.available_files.copy())
            except:
                pass
        # Default: select all available files
        return self.available_files.copy()
    
    def _save_selected_files(self):
        """Save selected wordlist files to settings"""
        settings = {}
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
            except:
                pass
        
        settings['selected_wordlists'] = self.selected_files
        
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f)
    
    def _load_all_wordlists(self):
        """Load words from all selected wordlist files"""
        self.word_set = set()
        
        for filename in self.selected_files:
            file_path = os.path.join(self.wordlists_folder, filename)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        words = [line.strip().lower() for line in f if line.strip()]
                        self.word_set.update(words)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        # Convert to sorted list
        self.word_list = sorted(list(self.word_set))
    
    def get_wordlist_info(self):
        """Get information about available wordlists"""
        wordlist_info = {}
        
        for filename in self.available_files:
            file_path = os.path.join(self.wordlists_folder, filename)
            word_count = 0
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        word_count = len([line for line in f if line.strip()])
                except:
                    word_count = 0
            
            wordlist_info[filename] = {
                'count': word_count,
                'selected': filename in self.selected_files
            }
        
        return wordlist_info
    
    def filter_words(self, pattern):
        """
        Filter word list based on pattern with underscores
        
        Args:
            pattern (str): Pattern like "d___i" where _ represents unknown letters
            
        Returns:
            list: Matching words
        """
        if not pattern:
            return []
            
        # If pattern contains no wildcards, do prefix matching
        if '_' not in pattern:
            try:
                # Escape pattern and match any continuation
                regex = re.compile(f"^{re.escape(pattern)}.*$", re.IGNORECASE)
                return [word for word in self.word_list if regex.match(word)]
            except re.error:
                return []
        # Otherwise treat _ as single-character wildcard
        regex_pattern = pattern.replace('_', '.')
        try:
            regex = re.compile(f"^{regex_pattern}$", re.IGNORECASE)
            return [word for word in self.word_list if regex.match(word)]
        except re.error:
            return []
    
    def load_word_list(self, file_path):
        """Load words from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.word_list = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Warning: Word list file {file_path} not found, using default words")
    
    def add_words(self, words):
        """Add words to the current list"""
        if isinstance(words, str):
            words = [words]
        self.word_list.extend(words)
        
    def get_word_count(self):
        """Get total number of words in the list"""
        return len(self.word_list)
    
    def update_selected_wordlists(self, selected_files):
        """Update which wordlists are selected and reload"""
        self.selected_files = selected_files
        self._save_selected_files()
        self._load_all_wordlists()
    
    def add_user_word(self, word):
        """Add a word to the user's custom wordlist"""
        word = word.strip().lower()
        if not word:
            return False
            
        if word in self.word_set:
            return False  # Word already exists
            
        # Add to user words file
        try:
            with open(self.user_words_file, 'a', encoding='utf-8') as f:
                f.write(word + '\n')
            
            # Update in-memory sets
            self.word_set.add(word)
            self.word_list = sorted(list(self.word_set))
            return True
            
        except Exception as e:
            print(f"Error adding word: {e}")
            return False
    
    def remove_user_word(self, word):
        """Remove a word from the user's custom wordlist"""
        word = word.strip().lower()
        if not word or word not in self.word_set:
            return False
            
        try:
            # Read all user words
            user_words = set()
            if os.path.exists(self.user_words_file):
                with open(self.user_words_file, 'r', encoding='utf-8') as f:
                    user_words = {line.strip().lower() for line in f if line.strip()}
            
            # Remove the word if it exists in user words
            if word in user_words:
                user_words.discard(word)
                
                # Rewrite the file without the word
                with open(self.user_words_file, 'w', encoding='utf-8') as f:
                    for w in sorted(user_words):
                        f.write(w + '\n')
                
                # Reload all wordlists to update in-memory data
                self._load_all_wordlists()
                return True
            
            return False
            
        except Exception as e:
            print(f"Error removing word: {e}")
            return False
    
    def get_combined_wordlist(self):
        """Get all words from selected wordlists, sorted alphabetically then by length"""
        # Sort by length first, then alphabetically
        return sorted(self.word_list, key=lambda x: (len(x), x))
    
    def get_available_wordlists(self):
        """Get list of available wordlist filenames"""
        return self.available_files
    
    def get_selected_wordlists(self):
        """Get list of currently selected wordlist filenames"""
        return self.selected_files
