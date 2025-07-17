# TODO - Pictor Development Tasks

> **⚠️ PRIORITY NOTE**: This TODO file must ALWAYS be updated whenever changes are made to the codebase. It serves as the single source of truth for what needs to be worked on next. Do not track completed tasks here - only document remaining work and next steps.

## Current Priority: UI Refactor - Navigation & Settings Cleanup

### Current Issues Identified
- Wrench icon (🔧) at top right doesn't work, but "Settings" button does
- Redundant "Word Lists" tab (functionality already in Settings > Wordbank)
- "Always on Top" checkbox should be in Settings, not top navigation
- Placeholder text "More settings incoming soon..." needs removal

## Step-by-Step Implementation Plan

### ✅ Step 1: Fix wrench icon functionality and remove redundant settings button
- [ ] Remove the "Settings" button from the top navigation bar (currently between Main and Word Lists)
- [ ] Make the wrench icon (🔧) at the top right actually open the settings frame
- [ ] Update the `on_open_debug` method to `on_open_settings` and change its functionality

### ⏳ Step 2: Remove the "Word Lists" tab completely
- [ ] Remove the "Word Lists" button from the navigation bar
- [ ] Remove the `create_wordlists_frame()` method and related functionality
- [ ] Update the frame management to only handle 'main' and 'settings'

### ⏳ Step 3: Move "Always on Top" checkbox into Settings
- [ ] Remove the "Always on Top" checkbox from the top navigation bar
- [ ] Add it as a setting within the Settings frame (probably in a new "General" or "Application" settings category)
- [ ] This will make the wrench icon truly be at the top right

### ⏳ Step 4: Remove the "More settings incoming soon..." placeholder text
- [ ] Find and remove the placeholder text that appears in the settings sidebar

### ⏳ Step 5: Clean up navigation button states
- [ ] Update the `update_nav_buttons` method to only handle 'main' since settings won't be a navigation tab anymore
- [ ] Ensure proper visual feedback when switching between main view and settings

## Expected Final Result
- Clean navigation bar with only "Main" tab
- Wrench icon at top right opens settings (no more separate settings tab)
- "Always on Top" moved to settings
- No redundant Word Lists tab
- No placeholder text in settings

## Files to Modify
- `pictor/gui/word_matcher.py` - Main navigation and frame management
- `pictor/gui/settings_window.py` - Add general settings section for "Always on Top"

## Notes
- Debug window functionality should remain separate and accessible via a different method
- All existing settings functionality (Wordbank, Capture Settings) should remain intact
- Embedded settings approach should be maintained
