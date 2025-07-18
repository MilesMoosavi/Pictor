"""
Capture Settings Panel for Pictor Settings Window
"""
import tkinter as tk
from tkinter import ttk, messagebox
import pygetwindow as gw

class CaptureSettingsPanel(tk.Frame):
    """A frame that contains the capture settings controls."""
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg='#f0f0f0', **kwargs)
        self.app = app
        
        # State variables
        self.monitoring = False
        self.coordinates = None
        self.selection_history = []
        self.history_index = -1
        self._canvas_info = {}
        self.select_mode = False
        
        # UI state variables
        self.window_var = tk.StringVar()
        self.priority_var = tk.StringVar(value="Match title")
        self.rate_var = tk.DoubleVar(value=1.0)
        
        # Widget references
        self.window_dropdown = None
        self.monitor_btn = None
        self.select_area_btn = None
        self.coords_label = None
        self.preview_canvas = None
        self.refresh_btn = None
        self.rate_scale = None

        self.build_ui()

    def build_ui(self):
        """Create the capture settings UI."""
        # Create title
        title_label = tk.Label(
            self,
            text="Capture Settings",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0'
        )
        title_label.pack(pady=(20, 10))

        # Description
        desc_label = tk.Label(
            self,
            text="Configure screen capture and monitoring settings",
            font=('Arial', 10),
            bg='#f0f0f0',
            fg='#666666'
        )
        desc_label.pack(pady=(0, 20))

        # --- Inline capture settings controls ---
        # Window selection
        window_frame = tk.Frame(self, bg='#f0f0f0')
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
        priority_frame = tk.Frame(self, bg='#f0f0f0')
        priority_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(
            priority_frame,
            text="Window Match Priority:",
            bg='#f0f0f0',
            font=('Arial', 9)
        ).pack(side='left')
        
        priority_dropdown = ttk.Combobox(
            priority_frame,
            textvariable=self.priority_var,
            values=["Match title", "Match exact window", "Match any window"],
            state='readonly',
            width=20
        )
        priority_dropdown.pack(side='right')
        
        # Preview area
        preview_frame = tk.Frame(self, bg='#f0f0f0')
        preview_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(
            preview_frame,
            text="Preview:",
            bg='#f0f0f0',
            font=('Arial', 9)
        ).pack(anchor='w')
        
        # Preview canvas
        self.preview_canvas = tk.Canvas(
            preview_frame,
            bg='#ccc',
            height=200,
            relief='flat',
            borderwidth=0,
            highlightthickness=0
        )
        self.preview_canvas.pack(fill='both', expand=True, pady=5)
        self.preview_canvas.bind('<Configure>', self.draw_placeholder)
        self.preview_canvas.bind('<ButtonPress-1>', self.on_canvas_press)
        self.preview_canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.preview_canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
        self.preview_canvas.event_generate('<Configure>')
        
        # Configured Coordinates display
        coords_frame = tk.Frame(self, bg='#f0f0f0')
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
        bottom_frame = tk.Frame(self, bg='#f0f0f0')
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
        
        # Populate window list and bind selection event
        self.populate_windows()
        self.window_dropdown.bind('<<ComboboxSelected>>', lambda e: (
            self.print_selected_window_dims(), 
            self.preview_canvas.event_generate('<Configure>') if self.preview_canvas else None,
            print("[DEBUG] Window selection changed - redrawing preview")
        ))

    def on_refresh_windows(self):
        """Refresh the window list"""
        self.populate_windows()
        self.print_selected_window_dims()
        if self.preview_canvas:
            self.preview_canvas.event_generate('<Configure>')
        
    def populate_windows(self):
        """Populate the window dropdown with all open window titles"""
        try:
            all_titles = gw.getAllTitles()
            filtered = [w for w in all_titles if w and w.strip()]
            game_keywords = ['skribbl', 'draw', 'pictionary', 'quickdraw']
            browser_terms = ['chrome', 'firefox', 'edge']
            blacklist = [
                'visual studio code', 'file explorer', 'settings',
                'task manager', 'program manager', 'windows input experience',
                'word matcher', 'select capture area', 'grammarly', 'voicemod', 'wv_',
                'refresh'
            ]
            windows = []
            for w in filtered:
                lw = w.lower()
                if any(term in lw for term in blacklist):
                    continue
                if any(b in lw for b in browser_terms) and not any(g in lw for g in game_keywords):
                    continue
                windows.append(w)
            
            seen = set()
            unique_windows = [x for x in windows if not (x in seen or seen.add(x))]
        except Exception:
            unique_windows = []
        
        if not unique_windows:
            unique_windows = ["No sources detected"]
        
        if self.window_dropdown:
            self.window_dropdown['values'] = unique_windows
            if unique_windows and unique_windows[0] != "No sources detected":
                self.window_dropdown.set(unique_windows[0])
                self.print_selected_window_dims()
            else:
                self.window_dropdown.set("No sources detected")
            
    def on_toggle_monitoring(self):
        """Toggle monitoring state"""
        self.monitoring = not self.monitoring
        
        if self.monitoring:
            if self.select_mode:
                self.select_mode = False
                if self.select_area_btn: self.select_area_btn.config(text="Enable Selection Mode", bg=self.cget('bg'), fg="black")
                if self.preview_canvas: self.preview_canvas.config(cursor="")
            
            if self.monitor_btn: self.monitor_btn.config(text="Stop Monitoring", bg='#f44336')
            messagebox.showinfo("Monitoring", f"Monitoring started at {self.rate_var.get():.1f} FPS")
        else:
            if self.monitor_btn: self.monitor_btn.config(text="Start Monitoring", bg='#4CAF50')
            messagebox.showinfo("Monitoring", "Monitoring stopped")
    
    def on_select_area(self):
        """Toggle interactive selection mode on/off"""
        self.select_mode = not self.select_mode
        
        if self.select_mode:
            if self.monitoring:
                self.monitoring = False
                if self.monitor_btn: self.monitor_btn.config(text="Start Monitoring", bg='#4CAF50')
                
            if self.select_area_btn: self.select_area_btn.config(text="Disable Selection Mode", bg='orange', fg="white")
            if self.preview_canvas: self.preview_canvas.config(cursor="crosshair")
            messagebox.showinfo("Selection Mode", "Click and drag on the preview to select capture area")
        else:
            if self.select_area_btn: self.select_area_btn.config(text="Enable Selection Mode", bg=self.cget('bg'), fg="black")
            if self.preview_canvas:
                self.preview_canvas.config(cursor="")
                self.preview_canvas.delete('selrect')
    
    def print_selected_window_dims(self):
        """Prints debug info for selected window dimensions"""
        title = self.window_var.get()
        if not title or title == "No sources detected":
            return
            
        try:
            win = gw.getWindowsWithTitle(title)[0]
            print(f"[DEBUG] Selected window '{title}' dims: left={win.left}, top={win.top}, width={win.width}, height={win.height}")
        except Exception as e:
            print(f"[DEBUG] Failed to get dims for '{title}': {e}")
            
    def draw_placeholder(self, event=None):
        """Draw a proportional representation of the selected window."""
        canvas = self.preview_canvas
        if not canvas: return
            
        canvas.delete('all')
        title = self.window_var.get()
        
        if not title or title == "No sources detected": return
            
        try:
            win = gw.getWindowsWithTitle(title)[0]
            ww, wh = win.width, win.height
            left, top = win.left, win.top
        except Exception:
            return

        cw, ch = canvas.winfo_width(), canvas.winfo_height()
        margin = 20
        scale = min((cw - margin) / ww, (ch - margin) / wh) if ww > 0 and wh > 0 else 0
        
        rw, rh = ww * scale, wh * scale
        xoff = (cw - rw) / 2
        yoff = (ch - rh) / 2
        
        self._canvas_info = {'scale': scale, 'xoff': xoff, 'yoff': yoff, 'rw': rw, 'rh': rh, 'left': left, 'top': top}
                              
        canvas.create_rectangle(xoff, yoff, xoff + rw, yoff + rh, fill='#888', outline='', tags='placeholder')
        canvas.create_rectangle(xoff, yoff, xoff + rw, yoff + rh, fill='#000000', outline='', stipple='gray75', tags='overlay')
                                
        if not self.coordinates:
            canvas.create_text(cw/2, ch/2, text="No capture area selected", fill='white', font=('Arial', 10, 'italic'), tags='selection')
        else:
            info = self._canvas_info
            window_rel_x = self.coordinates[0] - info['left']
            window_rel_y = self.coordinates[1] - info['top']
            
            cx = info['xoff'] + window_rel_x * info['scale']
            cy = info['yoff'] + window_rel_y * info['scale']
            
            cw_sel = self.coordinates[2] * info['scale']
            ch_sel = self.coordinates[3] * info['scale']
            
            x0, y0 = info['xoff'], info['yoff']
            x1, y1 = x0 + info['rw'], y0 + info['rh']
            
            cx1, cy1 = max(x0, min(x1, cx)), max(y0, min(y1, cy))
            cx2, cy2 = max(x0, min(x1, cx + cw_sel)), max(y0, min(y1, cy + ch_sel))
            
            canvas.create_rectangle(cx1, cy1, cx2, cy2, fill='#888', outline='', tags='selection')
            canvas.create_rectangle(cx1, cy1, cx2, cy2, outline='red', dash=(4, 2), width=3, tags='selection')
    
    def on_canvas_press(self, event):
        """Start drag-select on preview canvas."""
        if not self.select_mode: return
        
        info = self._canvas_info
        x0, y0 = info.get('xoff', 0), info.get('yoff', 0)
        x1, y1 = x0 + info.get('rw', 0), y0 + info.get('rh', 0)
        
        if not (x0 <= event.x <= x1 and y0 <= event.y <= y1): return
            
        self.start_x = max(x0, min(x1, event.x))
        self.start_y = max(y0, min(y1, event.y))
        if self.preview_canvas:
            self.preview_canvas.delete('selrect')

    def on_canvas_drag(self, event):
        """Update drag-select rectangle."""
        if not self.select_mode or self.start_x is None or self.start_y is None: return
        
        canvas = self.preview_canvas
        if not canvas: return
        canvas.delete('selrect')
        info = self._canvas_info
        x0, y0 = info['xoff'], info['yoff']
        x1, y1 = x0 + info['rw'], y0 + info['rh']
        
        x2 = max(x0, min(x1, event.x))
        y2 = max(y0, min(y1, event.y))
        
        canvas.create_rectangle(self.start_x, self.start_y, x2, y2, outline='red', dash=(4, 2), tags='selrect')

    def on_canvas_release(self, event):
        """Finalize selection and map to window coords."""
        if not self.select_mode or self.start_x is None or self.start_y is None: return
        
        canvas = self.preview_canvas
        if not canvas: return
        canvas.delete('selrect')
        
        info = self._canvas_info
        x0, y0 = info['xoff'], info['yoff']
        x1, y1 = x0 + info['rw'], y0 + info['rh']
        
        event_x = max(x0, min(x1, event.x))
        event_y = max(y0, min(y1, event.y))
        
        cx = min(self.start_x, event_x)
        cy = min(self.start_y, event_y)
        cw = abs(event_x - self.start_x)
        ch = abs(event_y - self.start_y)
        
        self.start_x = self.start_y = None
        
        if cw < 5 or ch < 5: return

        scale = info['scale']
        if scale == 0: return # Avoid division by zero
        real_x = int((cx - info['xoff']) / scale)
        real_y = int((cy - info['yoff']) / scale)
        real_w = int(cw / scale)
        real_h = int(ch / scale)
        
        try:
            win = gw.getWindowsWithTitle(self.window_var.get())[0]
            abs_x = win.left + real_x
            abs_y = win.top + real_y
            self.coordinates = (abs_x, abs_y, real_w, real_h)
            
            self.selection_history.append(self.coordinates)
            self.history_index = len(self.selection_history) - 1
            
            self.draw_placeholder()
            if self.coords_label:
                self.coords_label.config(text=f"({abs_x}, {abs_y}, {real_w}, {real_h})")
        except Exception as e:
            print(f"[DEBUG] on_canvas_release error: {e}")
            self.coordinates = None
