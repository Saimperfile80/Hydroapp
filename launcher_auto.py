#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HydroAI Launcher - Installer packages si nécessaire, puis lancer app
"""

import subprocess
import sys
import os

def check_and_install():
    """Vérifier et installer packages si nécessaire"""
    
    packages = ['numpy', 'scipy', 'pandas', 'matplotlib', 'PySide6', 'reportlab']
    
    print("Vérification des packages...")
    
    for pkg in packages:
        try:
            __import__(pkg.replace('-', '_'))
            print(f"  ✓ {pkg}")
        except ImportError:
            print(f"  ✗ {pkg} - Installation en cours...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg, '--quiet'])
            print(f"  ✓ {pkg} installé")
    
    print("\n✓ Tous les packages sont prêts!\n")

if __name__ == "__main__":
    try:
        check_and_install()
        
        print("Démarrage de HydroAI...")
        print("-" * 60)
        
        from app.main_app import HydroAIApp
        from PySide6.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        window = HydroAIApp()
        window.show()
        
        sys.exit(app.exec())
    
    except Exception as e:
        print(f"\nERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
