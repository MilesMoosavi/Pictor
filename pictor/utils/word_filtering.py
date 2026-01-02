import re
import os
import json


class WordFilter:
    """Handles word filtering and pattern matching with persistent user wordlists"""
    
    def __init__(self, wordlists_folder=None, user_words_file=None):
        self.wordlists_folder = wordlists_folder or self._get_wordlists_folder()
        self.user_words_file = user_words_file or os.path.join(self.wordlists_folder, "user_added_words.txt")
        self.settings_file = os.path.join(os.path.dirname(self.wordlists_folder), "settings.json")
        
        # Initialize available wordlist files
        self.available_files = self._get_available_wordlists()
        self.selected_files = self._load_selected_files()
        
        # Load combined word list
        self.word_dict = {}  # lower: original
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
        self.word_dict = {}
        
        for filename in self.selected_files:
            file_path = os.path.join(self.wordlists_folder, filename)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            word = line.strip()
                            if word:
                                self.word_dict[word.lower()] = word
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        # Convert to sorted list of originals
        self.word_list = sorted(self.word_dict.values())
    
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
    
    def filter_words(self, pattern, exact_length=False):
        """
        Filter word list based on pattern with underscores
        
        Args:
            pattern (str): Pattern like "d___i" where _ represents unknown letters
            exact_length (bool): If True, match exact length; if False, allow longer matches
            
        Returns:
            list: Matching words
        """
        if not pattern:
            return []
            
        # If pattern contains no wildcards, do prefix matching
        if '_' not in pattern:
            try:
                # Escape pattern and match continuation based on exact_length
                if exact_length:
                    regex = re.compile(f"^{re.escape(pattern)}$", re.IGNORECASE)
                else:
                    regex = re.compile(f"^{re.escape(pattern)}.*$", re.IGNORECASE)
                return [word for word in self.word_list if regex.match(word)]
            except re.error:
                return []
        # Otherwise treat _ as single-character wildcard
        regex_pattern = pattern.replace('_', '.')
        try:
            # Match words based on exact_length
            if exact_length:
                regex = re.compile(f"^{regex_pattern}$", re.IGNORECASE)
            else:
                regex = re.compile(f"^{regex_pattern}.*$", re.IGNORECASE)
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
        original_word = word.strip()
        word_lower = original_word.lower()
        if not original_word:
            return False
            
        if word_lower in self.word_dict:
            return False  # Word already exists
            
        # Add to in-memory dict
        self.word_dict[word_lower] = original_word
        self.word_list = sorted(self.word_dict.values())
        
        # Rewrite the entire file sorted
        try:
            with open(self.user_words_file, 'w', encoding='utf-8') as f:
                for w in self.word_list:
                    f.write(w + '\n')
            return True
            
        except Exception as e:
            print(f"Error adding word: {e}")
            return False
    
    def remove_user_word(self, word):
        """Remove a word from the user's custom wordlist"""
        word = word.strip().lower()
        if not word or word not in self.word_dict:
            return False
            
        try:
            # Remove from dict
            del self.word_dict[word]
            self.word_list = sorted(self.word_dict.values())
            
            # Rewrite the file
            with open(self.user_words_file, 'w', encoding='utf-8') as f:
                for w in self.word_list:
                    f.write(w + '\n')
            return True
            
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
    
    def get_words_from_file(self, filename):
        """Get all words from a specific wordlist file"""
        file_path = os.path.join(self.wordlists_folder, filename)
        words = []
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    words = [line.strip().lower() for line in f if line.strip()]
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                
        return words
