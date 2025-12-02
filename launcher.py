#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Lanceur HydroAI - Script simplifié
Vérifie dépendances et lance application
"""

import sys
import os
import time
from pathlib import Path

# Setup path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def check_dependencies():
    """Vérifier dépendances avant lancement"""
    print("Vérification dépendances HydroAI...")
    print("-" * 60)
    
    deps = {
        'numpy': 'Calculs scientifiques',
        'scipy': 'Algorithmes optimization',
        'pandas': 'Gestion données',
        'matplotlib': 'Visualisation graphiques',
        'PySide6': 'Interface utilisateur'
    }
    
    missing = []
    for pkg, desc in deps.items():
        try:
            __import__(pkg)
            print(f"✓ {pkg:15} - {desc}")
        except ImportError:
            print(f"✗ {pkg:15} - {desc} [MANQUANT]")
            missing.append(pkg)
    
    print("-" * 60)
    
    if missing:
        print(f"\nPaquets manquants: {', '.join(missing)}")
        print("Installation: pip install " + " ".join(missing))
        return False
    
    print("\n✓ Toutes dépendances OK\n")
    return True


def main():
    """Lancer l'application"""
    
    # Vérifier dépendances
    if not check_dependencies():
        input("Appuyez sur Entrée pour quitter...")
        sys.exit(1)
    
    print("Chargement HydroAI...")
    print()
    
    try:
        from app.main_app import HydroAIApp
        from PySide6.QtWidgets import QApplication
        
        # Créer app Qt
        app = QApplication(sys.argv)
        
        # Créer fenêtre principale
        window = HydroAIApp()
        window.show()
        
        print("✓ Application lancée")
        print("\nFenêtre en cours de démarrage...")
        
        # Lancer event loop
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"\n✗ ERREUR LANCEMENT: {e}")
        print("\nVérifiez que tous les modules sont présents:")
        print("  - core/calculations/ (theis, cooper_jacob, etc.)")
        print("  - core/ai/ (anomaly_detection, etc.)")
        print("  - app/ui/tabs/ (home_tab, essais_pompage_tab, etc.)")
        
        import traceback
        traceback.print_exc()
        
        input("\nAppuyez sur Entrée pour quitter...")
        sys.exit(1)


if __name__ == "__main__":
    main()
