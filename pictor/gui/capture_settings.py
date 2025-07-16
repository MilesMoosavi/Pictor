import tkinter as tk
from tkinter import ttk, messagebox


class CaptureSettingsWindow:
    """OBS-style capture settings window"""
    
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Select Capture Area")
        self.window.geometry("550x400")
        self.window.configure(bg='#f0f0f0')
        self.window.resizable(True, True)
        
        # Make it modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # State variables
        self.monitoring = False
        self.coordinates = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the capture settings UI"""
        
        # Top section
        top_frame = tk.Frame(self.window, bg='#f0f0f0')
        top_frame.pack(fill='x', padx=10, pady=10)
        
        # Select capture area button
        self.select_area_btn = tk.Button(
            top_frame,
            text="Select Capture Area",
            command=self.on_select_area,
            font=('Arial', 10),
            padx=20, pady=5
        )
        self.select_area_btn.pack()
        
        # Coordinates display
        coords_frame = tk.Frame(top_frame, bg='#f0f0f0')
        coords_frame.pack(pady=5)
        
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
        self.preview_canvas = tk.Canvas(
            preview_frame,
            bg='black',
            height=200,
            relief='solid',
            borderwidth=2
        )
        self.preview_canvas.pack(fill='both', expand=True, pady=5)
        
        # "No area selected" text
        self.no_area_text = self.preview_canvas.create_text(
            275, 100,  # Center of canvas
            text="No area selected",
            fill='white',
            font=('Arial', 12)
        )
        
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
        
    def on_select_area(self):
        """Handle select area button click"""
        # Simulate area selection
        self.coordinates = (100, 100, 400, 300)  # x, y, width, height
        self.coords_label.config(text=f"X:{self.coordinates[0]} Y:{self.coordinates[1]} W:{self.coordinates[2]} H:{self.coordinates[3]}")
        
        # Update preview
        self.preview_canvas.delete(self.no_area_text)
        self.preview_canvas.create_rectangle(10, 10, 540, 190, outline='green', width=2)
        self.preview_canvas.create_text(275, 100, text="Capture Area Selected", fill='lime', font=('Arial', 12))
        
        messagebox.showinfo("Select Area", f"Area selected: {self.coordinates}")
        
    def on_refresh_windows(self):
        """Refresh the window list"""
        self.populate_windows()
        messagebox.showinfo("Refresh", "Window list refreshed")
        
    def populate_windows(self):
        """Populate the window dropdown with sample data"""
        # Sample windows for now
        windows = [
            "Chrome - Pictionary Game",
            "Firefox - Drawing Game", 
            "Desktop",
            "Notepad - Untitled",
            "VS Code - Pictor"
        ]
        
        self.window_dropdown['values'] = windows
        if windows:
            self.window_dropdown.set(windows[0])
            
    def on_toggle_monitoring(self):
        """Toggle monitoring state"""
        self.monitoring = not self.monitoring
        
        if self.monitoring:
            self.monitor_btn.config(text="Stop Monitoring", bg='#f44336')
            messagebox.showinfo("Monitoring", f"Monitoring started at {self.rate_var.get():.1f} FPS")
        else:
            self.monitor_btn.config(text="Start Monitoring", bg='#4CAF50')
            messagebox.showinfo("Monitoring", "Monitoring stopped")
    
    def get_settings(self):
        """Get current capture settings"""
        return {
            'window': self.window_var.get(),
            'coordinates': self.coordinates,
            'priority': self.priority_var.get(),
            'capture_rate': self.rate_var.get(),
            'monitoring': self.monitoring
        }
