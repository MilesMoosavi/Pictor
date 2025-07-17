import tkinter as tk
import subprocess
import sys
import os


class DebugWindow:
    """A small debug window with restart functionality for development"""
    
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Debug Tools")
        self.window.geometry("200x80")
        self.window.resizable(False, False)
        
        # Make it stay on top and in a convenient position
        self.window.attributes('-topmost', True)
        self.window.geometry("+50+50")  # Position near top-left
        
        # Set up the UI
        self.setup_ui()
        
        # Make sure it doesn't close the main app when closed
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_ui(self):
        """Set up the debug window UI"""
        # Main frame
        main_frame = tk.Frame(self.window, bg='#f0f0f0', padx=10, pady=10)
        main_frame.pack(fill='both', expand=True)
        
        # Title label
        title_label = tk.Label(
            main_frame,
            text="Development Tools",
            font=('Arial', 9, 'bold'),
            bg='#f0f0f0'
        )
        title_label.pack(pady=(0, 5))
        
        # Restart button
        restart_btn = tk.Button(
            main_frame,
            text="🔄 Restart App",
            command=self.restart_app,
            font=('Arial', 10, 'bold'),
            bg='#FF9800',
            fg='white',
            padx=20,
            pady=5
        )
        restart_btn.pack()
    
    def restart_app(self):
        """Restart the entire application"""
        print("[DEBUG] Restarting application from debug window...")
        
        # Get the path to the main script
        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        main_script = os.path.join(project_root, 'main.py')
        
        print(f"[DEBUG] Main script path: {main_script}")
        
        # Start new instance
        subprocess.Popen([sys.executable, main_script])
        
        # Exit current process completely
        os._exit(0)
    
    def on_close(self):
        """Handle window close event"""
        self.window.withdraw()  # Hide instead of destroying
    
    def show(self):
        """Show the debug window"""
        self.window.deiconify()
    
    def hide(self):
        """Hide the debug window"""
        self.window.withdraw()
