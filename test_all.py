#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HydroAI - Test Application WITHOUT UI
Pour vérifier que tout fonctionne avant de lancer l'interface graphique
"""

import sys
import os
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

def test_calculations():
    """Tester les modules de calcul"""
    print("\n" + "="*60)
    print("HYDROAI - TEST DES CALCULS")
    print("="*60 + "\n")
    
    try:
        import numpy as np
        from core.calculations import theis
        
        print("[1/6] Testing Theis calculation...")
        analysis = theis.TheisAnalysis(
            Q=0.001,
            distance=50,
            times=np.array([10, 50, 100, 500, 1000]),
            drawdowns=np.array([0.02, 0.045, 0.062, 0.115, 0.145])
        )
        result = analysis.fit()
        print(f"  ✓ T = {result['T']:.2e} m²/s")
        print(f"  ✓ S = {result['S']:.2e}")
        
    except Exception as e:
        print(f"  ✗ Erreur Theis: {e}")
        return False
    
    try:
        from core.calculations import cooper_jacob
        print("\n[2/6] Testing Cooper-Jacob calculation...")
        analysis = cooper_jacob.CooperJacobAnalysis(
            Q=0.001,
            distance=50,
            times=np.array([10, 50, 100, 500, 1000]),
            drawdowns=np.array([0.02, 0.045, 0.062, 0.115, 0.145])
        )
        result = analysis.fit()
        print(f"  ✓ T = {result['T']:.2e} m²/s")
        print(f"  ✓ S = {result['S']:.2e}")
        
    except Exception as e:
        print(f"  ✗ Erreur Cooper-Jacob: {e}")
        return False
    
    try:
        from core.calculations import piezo
        print("\n[3/6] Testing Piezometry analysis...")
        data = np.array([10.5, 10.48, 10.46, 10.44, 10.42, 10.40, 9.80])
        analysis = piezo.PiezoAnalysis(data)
        stats = analysis.get_statistics()
        print(f"  ✓ Mean: {stats['mean']:.4f} m")
        print(f"  ✓ Amplitude: {stats['amplitude']:.4f} m")
        
    except Exception as e:
        print(f"  ✗ Erreur Piezo: {e}")
        return False
    
    return True


def test_ai():
    """Tester les modules IA"""
    try:
        from core.ai import AnomalyDetector, ParameterRecommender, PreComputeValidator
        import numpy as np
        
        print("\n[4/6] Testing Anomaly Detection...")
        data = np.array([1, 2, 3, 4, 5, 100])  # 100 is outlier
        detector = AnomalyDetector()
        idx, explanations = detector.detect_outliers_zscore(data, N=2)
        print(f"  ✓ Detected {len(idx)} outliers")
        
        print("\n[5/6] Testing Parameter Recommender...")
        recommender = ParameterRecommender()
        result = recommender.recommend_from_lithology('sables')
        print(f"  ✓ Recommended K range for sables: {result['K_range_ms']}")
        
        print("\n[6/6] Testing Validation Engine...")
        validator = PreComputeValidator()
        result = validator.validate_theis_parameters(
            Q=0.001, T=1e-3, S=1e-4, distance=50, time_max=1000
        )
        print(f"  ✓ Validation status: {result['status']}")
        print(f"  ✓ Confidence score: {result['confidence_score']:.0f}%")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Erreur IA: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui():
    """Tester interface PySide6"""
    try:
        from PySide6.QtWidgets import QApplication
        print("\n[UI] Testing PySide6...")
        # Just import, don't create app (headless environment)
        print("  ✓ PySide6 importable")
        return True
    except Exception as e:
        print(f"  ✗ Erreur PySide6: {e}")
        return False


def main():
    """Exécuter tous les tests"""
    
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  HYDROAI - SYSTEM VERIFICATION".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    # Tests
    calc_ok = test_calculations()
    ai_ok = test_ai()
    ui_ok = test_ui()
    
    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ")
    print("="*60)
    
    status = []
    status.append(("Calculs", "✓ OK" if calc_ok else "✗ ERROR"))
    status.append(("IA", "✓ OK" if ai_ok else "✗ ERROR"))
    status.append(("UI", "✓ OK" if ui_ok else "✗ ERROR"))
    
    for name, result in status:
        print(f"  {name:20} {result}")
    
    print("="*60)
    
    if calc_ok and ai_ok and ui_ok:
        print("\n✓ ALL SYSTEMS OPERATIONAL")
        print("\nYou can now launch the GUI:")
        print("  python launcher.py")
        print("  OR")
        print("  python run.py")
        return 0
    else:
        print("\n✗ SOME SYSTEMS FAILED")
        print("\nPlease check errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
