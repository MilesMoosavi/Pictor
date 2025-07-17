
# TODO - Pictor Development Tasks

> **⚠️ PRIORITY**: This TODO file must ALWAYS be updated whenever changes are made to the codebase. It serves as the single source of truth for what needs to be worked on next. Do not track completed tasks here - only document remaining work and next steps.
> **NOTE**: After each commit, reset this file to only the current actionable TODO items. Remove completed, historical, and archived sections to keep the file focused and maintainable.


# TODO - Pictor Development Tasks

> **⚠️ PRIORITY**: This TODO file must ALWAYS be updated whenever changes are made to the codebase. It serves as the single source of truth for what needs to be worked on next. Do not track completed tasks here - only document remaining work and next steps.

## Current TODOs

### Settings Persistence
[ ] Persist user settings and preferences across sessions
    - Wordlist selection (enabled/disabled wordlists)
    - Window state (size, position, always-on-top)
    - UI preferences (last search pattern, last selected result index)
    - Settings frame state (last open category)
    - User wordlist (added/removed words)
    - Developer/debug preferences (Dev Tools menu state)
    - General app preferences (theme, keyboard shortcuts)
[ ] Save and restore window position robustly
    - If previous position is off-screen (monitor config changed), reset to default visible position

### Window Size Improvement
[ ] Increase default window size to ensure all settings and buttons are visible on first launch
    - Especially for Capture Settings, ensure bottom buttons are not cut off

### Keyboard Shortcuts
[ ] Add Ctrl+F shortcut to focus search input box

## Long-Term / Future Enhancements
[ ] Enhanced search algorithms and word matching improvements
[ ] Additional wordlist sources and management features
[ ] Performance optimizations for large wordlists
[ ] Add more debugging utilities to Dev Tools menu
[ ] Implement better error logging and reporting
[ ] Add performance monitoring capabilities

### ✅ COMPLETED: Dev Tools Integration
- ✅ Added "Dev Tools" button with popup menu containing restart and recent changes
- ✅ Removed separate debug window (now integrated into Dev Tools menu)
- ✅ Proper menu positioning and error handling

### ✅ COMPLETED: Auto-Focus Functionality
- ✅ Auto-focus input box when tabbing back into app or clicking in empty areas
- ✅ Auto-select text in input box when focused for easy replacement/copying
- ✅ Arrow key navigation working with auto-focus without interference
- ✅ No "Close" button in embedded settings mode
- ✅ Removed obsolete methods (`on_select_word_lists`, old `on_always_on_top`)

### Additional Improvements Made:
- Created "General Settings" category as first option in settings
- Maintained all existing functionality (Wordbank, Capture Settings)
- Proper conditional UI elements for embedded vs popup mode
- Clean frame-based navigation system working perfectly
- **NEW**: Moved "Recent Changes" button to navigation bar next to "Main"
- **NEW**: Added "Dev Tools" button with popup menu containing:
  -  Restart App  
  - 📋 Recent Changes
  - Proper menu positioning and error handling
- **CLEANUP**: Removed separate debug window (now integrated into Dev Tools menu)

## Files to Modify
- `pictor/gui/word_matcher.py` - Main navigation and frame management
- `pictor/gui/settings_window.py` - Add general settings section for "Always on Top"

## Notes
- Debug window functionality should remain separate and accessible via a different method
- All existing settings functionality (Wordbank, Capture Settings) should remain intact
- Embedded settings approach should be maintained
