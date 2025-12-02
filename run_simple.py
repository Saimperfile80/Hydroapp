#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HydroAI Simplified Launcher
Direct launch without verification (for testing)
"""

import sys
import os
from pathlib import Path

# Add current dir to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("Starting HydroAI...")
    print("-" * 60)
    
    # Import and launch
    from app.main_app import HydroAIApp
    from PySide6.QtWidgets import QApplication
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create main window
    window = HydroAIApp()
    window.show()
    
    print("[OK] Application started")
    print("     Fenetre en cours de demarrage...")
    print("-" * 60)
    
    # Start event loop
    sys.exit(app.exec())
    
except Exception as e:
    print(f"\nERROR: {e}")
    print("\nMake sure you have:")
    print("  - Python 3.8+")
    print("  - NumPy, SciPy, PySide6 installed")
    print("\nRun: pip install numpy scipy PySide6 matplotlib pandas")
    import traceback
    traceback.print_exc()
