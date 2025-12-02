#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de vérification - Vérifier que tous les modules sont accessibles
"""

import sys
import os
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Tester imports des modules principaux"""
    
    print("=" * 60)
    print("HydroAI - Vérification installation")
    print("=" * 60)
    
    tests = []
    
    # Test 1: Modules de calcul
    print("\n✓ Test 1: Modules de calcul...")
    try:
        from core.calculations import (
            theis, cooper_jacob, lefranc, lugeon, porchet, piezo
        )
        print("  ✓ Theis, Cooper-Jacob, Lefranc, Lugeon, Porchet, Piezo - OK")
        tests.append(True)
    except ImportError as e:
        print(f"  ✗ Erreur import calculs: {e}")
        tests.append(False)
    
    # Test 2: Modules IA
    print("\n✓ Test 2: Modules IA...")
    try:
        from core.ai import (
            AnomalyDetector, ParameterRecommender, PreComputeValidator
        )
        print("  ✓ Anomaly Detection, Recommender, Validator - OK")
        tests.append(True)
    except ImportError as e:
        print(f"  ✗ Erreur import IA: {e}")
        tests.append(False)
    
    # Test 3: PySide6
    print("\n✓ Test 3: Interface PySide6...")
    try:
        from PySide6.QtWidgets import QApplication
        print("  ✓ PySide6 - OK")
        tests.append(True)
    except ImportError as e:
        print(f"  ✗ Erreur PySide6: {e}")
        tests.append(False)
    
    # Test 4: Dépendances scientifiques
    print("\n✓ Test 4: Dépendances scientifiques...")
    try:
        import numpy as np
        import scipy
        import pandas as pd
        import matplotlib
        print(f"  ✓ NumPy {np.__version__}, SciPy {scipy.__version__}, Pandas, Matplotlib - OK")
        tests.append(True)
    except ImportError as e:
        print(f"  ✗ Erreur dépendances: {e}")
        tests.append(False)
    
    # Test 5: Calcul simple Theis
    print("\n✓ Test 5: Calcul simple Theis...")
    try:
        import numpy as np
        from core.calculations import theis
        
        analysis = theis.TheisAnalysis(
            Q=0.001,
            distance=50,
            times=np.array([10, 50, 100, 500, 1000]),
            drawdowns=np.array([0.02, 0.045, 0.062, 0.115, 0.145])
        )
        result = analysis.fit()
        
        print(f"  ✓ T = {result['T']:.2e} m²/s, S = {result['S']:.2e} - OK")
        tests.append(True)
    except Exception as e:
        print(f"  ✗ Erreur calcul Theis: {e}")
        tests.append(False)
    
    # Test 6: Validation
    print("\n✓ Test 6: Validation IA...")
    try:
        from core.ai import PreComputeValidator
        
        validator = PreComputeValidator()
        result = validator.validate_theis_parameters(
            Q=0.001, T=1e-3, S=1e-4, distance=50, time_max=1000
        )
        
        print(f"  ✓ Statut: {result['status']}, Confiance: {result['confidence_score']:.0f}% - OK")
        tests.append(True)
    except Exception as e:
        print(f"  ✗ Erreur validation: {e}")
        tests.append(False)
    
    # Résumé
    print("\n" + "=" * 60)
    passed = sum(tests)
    total = len(tests)
    print(f"Résultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("✓ Installation OK - Vous pouvez lancer l'application!")
        print("\nPour lancer l'application:")
        print("  python run.py")
    else:
        print("✗ Des erreurs détectées - Voir ci-dessus")
    
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
