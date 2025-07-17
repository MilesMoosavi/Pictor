import tkinter as tk
from tkinter import ttk, messagebox
import pygetwindow as gw


class CaptureSettingsWindow:
    """OBS-style capture settings window"""
    
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Select Capture Area")
        # dynamically size window to screen resolution
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        # use 60% of screen dimensions
        default_w = int(sw * 0.6)
        default_h = int(sh * 0.6)
        self.window.geometry(f"{default_w}x{default_h}")
        # enforce a reasonable minimum
        self.window.minsize(600, 400)
        self.window.configure(bg='#f0f0f0')
        self.window.resizable(True, True)
        
        # Make it modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # State variables
        self.monitoring = False
        self.coordinates = None
        # selection history for undo/redo
        self.selection_history = []
        self.history_index = -1
        # last draw parameters for mapping
        self._canvas_info = {}
        # only allow drag-select after button click
        self.select_mode = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the capture settings UI"""
        
        # Top section
        top_frame = tk.Frame(self.window, bg='#f0f0f0')
        top_frame.pack(fill='x', padx=10, pady=10)
        
        # (Removed: selection now via canvas drag)
        
        # ...existing top controls...
        
        # Window selection
        window_frame = tk.Frame(self.window, bg='#f0f0f0')
        window_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(
            window_frame,
            text="Window:",
            bg='#f0f0f0',
            font=('Arial', 9)
        ).pack(anchor='w')
        
        # Window dropdown
        dropdown_frame = tk.Frame(window_frame, bg='#f0f0f0')
        dropdown_frame.pack(fill='x', pady=2)
        
        self.window_var = tk.StringVar()
        self.window_dropdown = ttk.Combobox(
            dropdown_frame,
            textvariable=self.window_var,
            state='readonly',
            width=50
        )
        self.window_dropdown.pack(side='left', fill='x', expand=True)
        
        # Refresh button
        self.refresh_btn = tk.Button(
            dropdown_frame,
            text="↻",
            command=self.on_refresh_windows,
            font=('Arial', 12),
            width=3
        )
        self.refresh_btn.pack(side='right', padx=(5, 0))
        
        # Window match priority
        priority_frame = tk.Frame(self.window, bg='#f0f0f0')
        priority_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(
            priority_frame,
            text="Window Match Priority:",
            bg='#f0f0f0',
            font=('Arial', 9)
        ).pack(side='left')
        
        self.priority_var = tk.StringVar(value="Match title")
        priority_dropdown = ttk.Combobox(
            priority_frame,
            textvariable=self.priority_var,
            values=["Match title", "Match exact window", "Match any window"],
            state='readonly',
            width=20
        )
        priority_dropdown.pack(side='right')
        
        # Preview area
        preview_frame = tk.Frame(self.window, bg='#f0f0f0')
        preview_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(
            preview_frame,
            text="Preview:",
            bg='#f0f0f0',
            font=('Arial', 9)
        ).pack(anchor='w')
        
        # Preview canvas (black box like in screenshot)
        # Preview canvas (shows scaled window rectangle)
        self.preview_canvas = tk.Canvas(
            preview_frame,
            bg='#ccc',  # light gray background
            height=200,
            relief='flat',  # remove border
            borderwidth=0,  # no border
            highlightthickness=0  # remove focus highlight
        )
        self.preview_canvas.pack(fill='both', expand=True, pady=5)
        # draw static gray placeholder and enable drag-select on canvas
        self.preview_canvas.bind('<Configure>', self.draw_placeholder)
        self.preview_canvas.bind('<ButtonPress-1>', self.on_canvas_press)
        self.preview_canvas.bind('<B1-Motion>',    self.on_canvas_drag)
        self.preview_canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
        # initial draw
        self.preview_canvas.event_generate('<Configure>')
        # Configured Coordinates display (below preview)
        coords_frame = tk.Frame(self.window, bg='#f0f0f0')
        coords_frame.pack(fill='x', padx=10, pady=(5,0))
        tk.Label(
            coords_frame,
            text="Configured Coordinates:",
            bg='#f0f0f0',
            font=('Arial', 9)
        ).pack(side='left')
        self.coords_label = tk.Label(
            coords_frame,
            text="None",
            bg='#f0f0f0',
            font=('Arial', 9, 'bold')
        )
        self.coords_label.pack(side='left', padx=5)
        
        # Bottom controls
        bottom_frame = tk.Frame(self.window, bg='#f0f0f0')
        bottom_frame.pack(fill='x', padx=10, pady=5)
        
        # Start/Stop monitoring
        self.monitor_btn = tk.Button(
            bottom_frame,
            text="Start Monitoring",
            command=self.on_toggle_monitoring,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10),
            padx=20
        )
        self.monitor_btn.pack(side='left')
        # No longer using Undo/Redo buttons
        # Select Capture Area toggle button
        self.select_area_btn = tk.Button(
            bottom_frame,
            text="Enable Selection Mode",
            command=self.on_select_area,
            font=('Arial', 10),
            padx=15
        )
        self.select_area_btn.pack(side='left', padx=(5,0))
        
        # Capture rate
        rate_frame = tk.Frame(bottom_frame, bg='#f0f0f0')
        rate_frame.pack(side='right')
        
        tk.Label(
            rate_frame,
            text="Capture Rate:",
            bg='#f0f0f0',
            font=('Arial', 9)
        ).pack(side='left')
        
        self.rate_var = tk.DoubleVar(value=1.0)
        self.rate_scale = tk.Scale(
            rate_frame,
            variable=self.rate_var,
            from_=0.1,
            to=5.0,
            resolution=0.1,
            orient='horizontal',
            length=100,
            bg='#f0f0f0'
        )
        self.rate_scale.pack(side='left', padx=5)
        
        tk.Label(
            rate_frame,
            text="FPS",
            bg='#f0f0f0',
            font=('Arial', 9)
        ).pack(side='left')
        
        # Populate window list
        self.populate_windows()
        # Print dims and update preview when user selects a window
        self.window_dropdown.bind('<<ComboboxSelected>>', lambda e: (
            self.print_selected_window_dims(), 
            self.preview_canvas.event_generate('<Configure>'),
            print("[DEBUG] Window selection changed - redrawing preview")
        ))
        
    def on_select_area(self):
        """Toggle interactive selection mode on/off"""
        # Check if a valid source is selected
        title = self.window_var.get()
        if not title or title == "No sources detected":
            # Show a message and don't enable selection mode
            print("[DEBUG] Cannot enable selection mode - no valid source selected")
            return
            
        # Toggle selection mode
        self.select_mode = not self.select_mode
        
        if self.select_mode:
            # Entering selection mode
            self.select_area_btn.config(
                text="Disable Selection Mode",
                bg="#ff4d4d",  # Red background to indicate active state
                fg="white"
            )
            # Update the cursor to indicate select mode
            self.preview_canvas.config(cursor="crosshair")
        else:
            # Exiting selection mode
            self.select_area_btn.config(
                text="Enable Selection Mode",
                bg=self.window.cget('bg'),  # Reset to default background
                fg="black"
            )
            # Reset cursor
            self.preview_canvas.config(cursor="")
            # Clear temporary selection rectangle if any
            self.preview_canvas.delete('selrect')
        
    def on_refresh_windows(self):
        """Refresh the window list"""
        self.populate_windows()
        # debug dims after refresh
        self.print_selected_window_dims()
        # update preview placeholder
        self.preview_canvas.event_generate('<Configure>')
        
    def populate_windows(self):
        """Populate the window dropdown with all open window titles"""
        # Populate dropdown with all window titles
        try:
            windows = gw.getAllTitles()
            # filter out empty or whitespace-only titles
            filtered = [w for w in windows if w and w.strip()]
            # define keywords
            game_keywords = ['skribbl', 'draw', 'pictionary', 'quickdraw']
            browser_terms = ['chrome', 'firefox', 'edge']
            # define unconditional blacklist of system/IDE windows
            # define unconditional blacklist of non-game windows
            blacklist = [
                'visual studio code', 'file explorer', 'settings',
                'task manager', 'program manager', 'windows input experience',
                # exclude app windows and known helpers
                'word matcher', 'select capture area', 'grammarly', 'voicemod', 'wv_',
                # exclude refresh dialogs
                'refresh'
            ]
            windows = []
            for w in filtered:
                lw = w.lower()
                # skip unconditional blacklist
                if any(term in lw for term in blacklist):
                    continue
                # skip browsers unless they contain a game keyword
                if any(b in lw for b in browser_terms) and not any(g in lw for g in game_keywords):
                    continue
                windows.append(w)
            # remove duplicate titles while preserving order
            seen = set()
            unique = []
            for w in windows:
                if w not in seen:
                    seen.add(w)
                    unique.append(w)
            windows = unique
        except Exception:
            windows = []
        # Fallback if no valid windows found
        if not windows:
            windows = ["No sources detected"]
        
        # DEBUG: print retrieved window titles
        print("[DEBUG] populate_windows titles:", windows)
        # OPTIONAL: uncomment to show in a dialog
        # messagebox.showinfo("Debug Windows", "\n".join(windows) or "<none>")
        self.window_dropdown['values'] = windows
        if windows and windows[0] != "No sources detected":
            # Select first entry by default only if it's a real window
            self.window_dropdown.set(windows[0])
            # debug dims for default selection
            self.print_selected_window_dims()
        else:
            # No valid sources, set the placeholder
            self.window_dropdown.set("No sources detected")
            
    def on_toggle_monitoring(self):
        """Toggle monitoring state"""
        self.monitoring = not self.monitoring
        
        if self.monitoring:
            # Turn off selection mode if it's active
            if self.select_mode:
                self.select_mode = False
                self.select_area_btn.config(
                    text="Enable Selection Mode", 
                    bg=self.window.cget('bg'),
                    fg="black"
                )
                self.preview_canvas.config(cursor="")
            
            self.monitor_btn.config(text="Stop Monitoring", bg='#f44336')
            messagebox.showinfo("Monitoring", f"Monitoring started at {self.rate_var.get():.1f} FPS")
        else:
            self.monitor_btn.config(text="Start Monitoring", bg='#4CAF50')
            messagebox.showinfo("Monitoring", "Monitoring stopped")
    
    def print_selected_window_dims(self):
        """Prints debug info for selected window dimensions"""
        title = self.window_var.get()
        
        # Skip if no valid source is selected
        if not title or title == "No sources detected":
            print("[DEBUG] No valid window source selected")
            return
            
        try:
            # fresh enumerate all windows for updated dimensions
            all_windows = gw.getAllWindows()
            # match by title substring
            matches = [w for w in all_windows if title.lower() in w.title.lower()]
            win = matches[0] if matches else gw.getWindowsWithTitle(title)[0]
            print(f"[DEBUG] Selected window '{title}' dims: left={win.left}, top={win.top}, width={win.width}, height={win.height}")
            
            # Provide more detailed window geometry information for debugging
            print(f"[DEBUG] Window box: left={win.left}, top={win.top}, right={win.right}, bottom={win.bottom}")
            
            # Check for negative coordinates which often indicate window borders
            if win.left < 0 or win.top < 0:
                print(f"[DEBUG] Window has negative position - likely has borders of approximately {abs(min(win.left, 0))}px horizontal, {abs(min(win.top, 0))}px vertical")
        except Exception as e:
            print(f"[DEBUG] Failed to get dims for '{title}': {e}")
            
    def get_settings(self):
        """Get current capture settings"""
        return {
            'window': self.window_var.get(),
            'coordinates': self.coordinates,
            'priority': self.priority_var.get(),
            'capture_rate': self.rate_var.get(),
            'monitoring': self.monitoring
        }
    
    def draw_placeholder(self, event=None):
        """Draw a gray rectangle proportional to the selected window in the preview canvas, centered."""
        canvas = self.preview_canvas
        # clear previous drawings
        canvas.delete('placeholder')
        canvas.delete('selection')
        canvas.delete('overlay')
        title = self.window_var.get()
        
        # Check if no valid source is selected
        if not title or title == "No sources detected":
            # Hide the preview by not drawing anything
            return
            
        # get window dims and position, fallback to canvas
        try:
            win = gw.getWindowsWithTitle(title)[0]
            ww, wh = win.width, win.height
            left, top = win.left, win.top
        except Exception:
            # If we can't get the window, also hide the preview
            print(f"[DEBUG] Could not find window '{title}', hiding preview")
            return
        # get canvas dimensions
        cw = canvas.winfo_width()
        ch = canvas.winfo_height()
        margin = 10
        # compute scale to fit with margin
        scale = min((cw - 2 * margin) / ww, (ch - 2 * margin) / wh)
        scale = max(scale, 0)
        # calculate drawn size and center
        rw, rh = ww * scale, wh * scale
        xoff = (cw - rw) / 2
        yoff = (ch - rh) / 2
        # store full mapping info
        self._canvas_info = {'scale': scale, 'xoff': xoff, 'yoff': yoff,
                              'rw': rw, 'rh': rh, 'left': left, 'top': top}
                              
        # draw gray rectangle base
        canvas.create_rectangle(xoff, yoff, xoff + rw, yoff + rh,
                                fill='#888', outline='', tags='placeholder')
                                
        # Add semi-transparent black overlay (75% opaque)
        # Note: Tkinter doesn't support true alpha transparency, so we use a stipple pattern
        # gray75 provides approximately 75% opacity (25% see-through)
        canvas.create_rectangle(xoff, yoff, xoff + rw, yoff + rh,
                              fill='#000000', outline='', stipple='gray75', tags='overlay')
                                
        # draw dimension labels
        # horizontal label above rectangle
        canvas.create_text(xoff + rw / 2, yoff - margin / 2,
                           text=f'{ww}px', fill='black', font=('Arial', 9),
                           tags='placeholder')
        # vertical label to the left of rectangle
        canvas.create_text(xoff - margin / 2, yoff + rh / 2,
                           text=f'{wh}px', fill='black', font=('Arial', 9),
                           angle=90, tags='placeholder')
        
        # overlay default text if no selection
        if not self.coordinates:
            canvas.create_text(cw/2, ch/2, text="No capture area selected",
                               fill='white', font=('Arial', 10, 'italic'), tags='selection')
        else:
            # persistent selection overlay - ensure it's drawn inside the placeholder
            info = self._canvas_info
            
            # Map real coords to canvas
            print(f"[DEBUG] draw_placeholder - coordinates={self.coordinates}, info={info}")
            # Calculate the position in the window relative to its top-left
            window_rel_x = self.coordinates[0] - info['left']
            window_rel_y = self.coordinates[1] - info['top']
            
            # Convert window-relative coordinates to canvas coordinates
            cx = info['xoff'] + window_rel_x * info['scale']
            cy = info['yoff'] + window_rel_y * info['scale']
            
            # Scale the width and height
            cw_sel = self.coordinates[2] * info['scale']
            ch_sel = self.coordinates[3] * info['scale']
            
            print(f"[DEBUG] draw_placeholder - window relative: ({window_rel_x}, {window_rel_y})")
            print(f"[DEBUG] draw_placeholder - canvas coords: ({cx}, {cy}) {cw_sel}x{ch_sel}")
            
            # Ensure selection stays within the placeholder bounds
            x0 = info['xoff']  # left edge of placeholder
            y0 = info['yoff']  # top edge of placeholder
            x1 = x0 + info['rw']  # right edge of placeholder
            y1 = y0 + info['rh']  # bottom edge of placeholder
            
            # Constrain selection rectangle to placeholder bounds
            cx = max(x0, min(x1, cx))
            cy = max(y0, min(y1, cy))
            cx_end = max(x0, min(x1, cx + cw_sel))
            cy_end = max(y0, min(y1, cy + ch_sel))
            
            # Print detailed debug information about the selection coordinates
            print(f"[DEBUG] Drawing selection rectangle at: ({cx}, {cy}) to ({cx_end}, {cy_end})")
            
            # "Punch through" the black overlay by creating a clear rectangle in the selection area
            # We use a gray rectangle the same color as the base to "erase" the overlay
            canvas.create_rectangle(cx, cy, cx_end, cy_end,
                                  fill='#888', outline='', tags='selection')
            
            # Draw the selection rectangle outline with increased visibility
            canvas.create_rectangle(cx, cy, cx_end, cy_end,
                                   outline='red', dash=(4, 2), width=3, tags='selection')
        
    # Interactive selection handlers
    def on_canvas_press(self, event):
        """Start drag-select on preview canvas."""
        # clear any previous start coords
        self.start_x = None
        self.start_y = None
        if not self.select_mode:
            return
        # only start if inside gray placeholder
        info = self._canvas_info
        x0, y0 = info.get('xoff', 0), info.get('yoff', 0)
        x1, y1 = x0 + info.get('rw', 0), y0 + info.get('rh', 0)
        
        # Check if click is inside placeholder
        if not (x0 <= event.x <= x1 and y0 <= event.y <= y1):
            return
            
        # Constrain start point to gray rectangle bounds
        constrained_x = max(x0, min(x1, event.x))
        constrained_y = max(y0, min(y1, event.y))
        
        # valid start - use constrained coordinates
        self.start_x, self.start_y = constrained_x, constrained_y
        self.preview_canvas.delete('selrect')

    def on_canvas_drag(self, event):
        """Update drag-select rectangle."""
        if not self.select_mode or self.start_x is None or self.start_y is None:
            return
        canvas = self.preview_canvas
        canvas.delete('selrect')
        # restrict drag within placeholder
        info = self._canvas_info
        x0 = info['xoff']  # left edge
        y0 = info['yoff']  # top edge
        x1 = info['xoff'] + info['rw']  # right edge
        y1 = info['yoff'] + info['rh']  # bottom edge
        
        # Constrain event point to gray rectangle bounds
        x2 = max(x0, min(x1, event.x))
        y2 = max(y0, min(y1, event.y))
        
        # Ensure start_x/y are integers before rectangle creation
        canvas.create_rectangle(int(self.start_x), int(self.start_y), x2, y2,
                                outline='red', dash=(4, 2), tags='selrect')

    def on_canvas_release(self, event):
        """Finalize selection and map to window coords."""
        print(f"[DEBUG] on_canvas_release triggered at canvas coords: ({event.x}, {event.y})")
        if not self.select_mode or self.start_x is None or self.start_y is None:
            return
        canvas = self.preview_canvas
        canvas.delete('selrect')  # Remove the drag selection
        
        # Store the start values before we reset them
        if self.start_x is None or self.start_y is None:
            return
            
        # Ensure we're working with valid coordinates
        info = self._canvas_info
        x0 = info['xoff']  # left edge
        y0 = info['yoff']  # top edge
        x1 = info['xoff'] + info['rw']  # right edge
        y1 = info['yoff'] + info['rh']  # bottom edge
        
        # Get the event coordinates within bounds
        event_x = max(x0, min(x1, event.x))
        event_y = max(y0, min(y1, event.y))
        
        # Calculate the selection rectangle
        start_x, start_y = int(self.start_x), int(self.start_y)
        cx = min(start_x, event_x)
        cy = min(start_y, event_y)
        cw = abs(event_x - start_x)
        ch = abs(event_y - start_y)
        
        # Reset start position to allow new selections
        # (since we're in toggle mode, we want to be ready for the next selection)
        self.start_x = None
        self.start_y = None
        
        # Skip if selection is too small (likely an accidental click)
        if cw < 5 or ch < 5:
            print("[DEBUG] Selection too small, ignoring")
            # Keep the previous selection if there is one
            self.start_x = None
            self.start_y = None
            return
        info = self._canvas_info
        try:
            print(f"[DEBUG] Canvas selection: ({cx}, {cy}) {cw}x{ch}")
            print("[DEBUG] Mapping selection to window coords... info=", self._canvas_info)
            win = gw.getWindowsWithTitle(self.window_var.get())[0]
            
            # Map canvas coordinates back to window coordinates
            real_x = int((cx - info['xoff']) / info['scale'])
            real_y = int((cy - info['yoff']) / info['scale'])
            real_w = int(cw / info['scale'])
            real_h = int(ch / info['scale'])
            
            # Detect and adjust for window borders
            # Many applications have invisible borders around their windows
            
            # First, try to detect the border offset dynamically based on window type
            border_offset_x = 0
            border_offset_y = 0
            
            # Look for known window types that need adjustment
            if "Chrome" in win.title or "Firefox" in win.title or "Edge" in win.title:
                # Most modern browsers have similar window decorations
                border_offset_x = 8 
                border_offset_y = 8
            elif win.left < 0 or win.top < 0:
                # If window reports negative coordinates, it likely has borders
                # The negative values often represent the border width
                border_offset_x = abs(min(win.left, 0))
                border_offset_y = abs(min(win.top, 0))
                print(f"[DEBUG] Detected negative window position, likely border: {border_offset_x},{border_offset_y}")
            
            # Explanation: Windows often reports window positions including invisible borders
            # This is why you might see coordinates like -6,-6 for the top-left of a window
            # These invisible borders are part of the window's decoration but not its visible content
            # We adjust for these borders to make the capture area align with the visible content
            
            # A calibration option could be added in the future to let users fine-tune these offsets
            
            print(f"[DEBUG] Applying window border adjustment: {border_offset_x},{border_offset_y}")
            print(f"[DEBUG] Original window position: ({win.left}, {win.top})")
            print(f"[DEBUG] Adjusted position will start at: ({max(0, win.left + real_x - border_offset_x)}, {max(0, win.top + real_y - border_offset_y)})")
            
            # Calculate absolute screen coordinates with border adjustment
            # Max with 0 to ensure we don't go negative
            abs_x = max(0, win.left + real_x - border_offset_x)
            abs_y = max(0, win.top + real_y - border_offset_y)
            
            # Save the coordinates
            self.coordinates = (abs_x, abs_y, real_w, real_h)
            
            # Debug: Print capture area coords
            print(f"[DEBUG] Mapped to window coordinates: ({real_x}, {real_y}) {real_w}x{real_h}")
            print(f"[DEBUG] Saved absolute coordinates: {self.coordinates}")
            
            # Update history
            self.selection_history = self.selection_history[:self.history_index+1]
            self.selection_history.append(self.coordinates)
            self.history_index += 1
            
            # Redraw placeholder to update with the permanent selection rectangle
            self.draw_placeholder()
        except Exception as e:
            print(f"[DEBUG] on_canvas_release error: {e}")
            self.coordinates = None
        # update display and debug
        if self.coordinates:
            x, y, w, h = self.coordinates
            self.coords_label.config(text=f"X:{x} Y:{y} W:{w} H:{h}")
            self.print_selected_window_dims()
        else:
            self.coords_label.config(text="None")
        
        # We don't exit selection mode now since it's a toggle button
        canvas.event_generate('<Configure>')

    def on_undo(self):
        """Undo last capture selection - no longer used."""
        pass

    def on_redo(self):
        """Redo capture selection - no longer used."""
        pass
