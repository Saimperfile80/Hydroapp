#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lanceur HydroAI - Point d'entrée principal
"""

import sys
import os

# Ajouter racine au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main_app import main

if __name__ == "__main__":
    main()
