#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launcher pour HydroAI UI - Version Simplifiée
"""

import sys
import os

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Lancer l'application
if __name__ == "__main__":
    from app.main_app_simple import main
    main()
