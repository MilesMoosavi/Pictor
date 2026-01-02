UI/Developer Guidelines

- Always design and test new UI elements against the application's minimum window geometry.
  - Current main window minimum: 550x200 (width x height). Assume users often start at this size.
  - Ensure critical controls (Save/Cancel, Open Folder, navigation) are visible without requiring the user to expand the window.

- Placement rules
  - Place per-tab Save/Cancel controls in a bottom toolbar that is outside scrollable content so it remains visible.
  - Avoid adding essential buttons inside deep scrollable panes; if they must be there, provide duplicates in a fixed footer.

- Sizing and layout
  - Use layout containers (grid/pack) with row/column weights so the footer stays docked.
  - Clamp dialog sizes relative to screen dimensions to avoid opening windows off-screen.

- Behavior
  - Each settings tab must track unsaved changes independently.
  - Prompt the user to Save/Discard/Cancel when switching tabs or closing a window if there are unsaved changes.

- Testing checklist before merging UI changes
  - Start app at minimum window size and verify all added controls are visible.
  - Test on at least two screen resolutions (small laptop and typical desktop).
  - Verify keyboard navigation and accessibility for newly-added controls.

- Where to add reminders
  - Add a short comment at the top of any new panel modules reminding maintainers to check the min geometry. Example:
    # IMPORTANT: Verify this panel renders correctly at the app min window size (550x200)

- Contact
  - For questions about UX expectations, ping the project owner in the repo.
