#!/usr/bin/env python3
"""
Pictor - Real-time Pictionary Assistant
Entry point for the application
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from pictor.gui.main.main_window import WordMatcherWindow


def main():
    """Main entry point"""
    try:
        app = WordMatcherWindow()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()