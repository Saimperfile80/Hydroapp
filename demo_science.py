"""
Démonstration complète du système de calcul HydroAI
===================================================

Montre comment utiliser les modules :
  - Theis et Cooper-Jacob
  - Tests de perméabilité (Lefranc, Lugeon, Porchet)
  - Piézométrie
  - Module IA (détection anomalies, recommandations, validation)
"""

import numpy as np
import sys
from pathlib import Path

# Ajouter core au chemin
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.calculations import theis, cooper_jacob, lefranc, lugeon, porchet, piezo
from core.ai import AnomalyDetector, ParameterRecommender, PreComputeValidator


def demo_theis():
    """Démonstration essai Theis."""
    print("\n" + "="*70)
    print("DÉMO 1 : ESSAI THEIS")
    print("="*70)
    
    # Données d'essai synthétiques
    Q = 0.001  # m³/s
    distance = 50  # m
    times = np.array([10, 50, 100, 500, 1000, 5000])  # s
    
    # Générer données "vraies"
    T_true = 1e-3  # m²/s
    S_true = 1e-4
    drawdowns = np.array([theis.theis_drawdown(Q, T_true, S_true, distance, t) 
                          for t in times])
    # Ajouter bruit
    drawdowns += np.random.normal(0, 0.001, len(drawdowns))
    
    print(f"\nParamètres vrais: T={T_true:.2e} m²/s, S={S_true:.2e}")
    print(f"Données mesurées : {len(times)} points")
    print(f"Débit: {Q:.2e} m³/s, Distance: {distance:.0f} m")
    
    # Ajustement Theis
    analysis = theis.TheisAnalysis(Q, distance, times, drawdowns)
    result = analysis.fit()
    
    print(f"\nRésultats Theis:")
    print(f"  T estimée:  {result['T']:.2e} m²/s (vraie: {T_true:.2e})")
    print(f"  S estimé:   {result['S']:.2e} (vraie: {S_true:.2e})")
    print(f"  RMSE:       {result['rmse']:.6f} m")
    print(f"  Succès:     {result['success']}")


def demo_cooper_jacob():
    """Démonstration essai Cooper-Jacob."""
    print("\n" + "="*70)
    print("DÉMO 2 : ESSAI COOPER-JACOB (approximation semi-log)")
    print("="*70)
    
    Q = 0.001  # m³/s
    distance = 50  # m
    times = np.logspace(0, 5, 50)  # 1 à 100000 s
    
    T_true = 1e-3
    S_true = 1e-4
    drawdowns = np.array([cooper_jacob.cooper_jacob_drawdown(Q, T_true, S_true, distance, t)
                          for t in times])
    drawdowns += np.random.normal(0, 0.001, len(drawdowns))
    
    print(f"\nParamètres vrais: T={T_true:.2e}, S={S_true:.2e}")
    
    analysis = cooper_jacob.CooperJacobAnalysis(Q, distance, times, drawdowns)
    result = analysis.fit_linear()
    
    print(f"\nRésultats Cooper-Jacob:")
    print(f"  T estimée:      {result['T']:.2e} m²/s")
    print(f"  S estimé:       {result['S']:.2e}")
    print(f"  Pente (Δs/ΔlogT): {result['slope']:.4f} m")
    print(f"  Validité (u<0.05): {result['validity_percentage']:.1f}%")
    print(f"  RMSE:           {result['rmse']:.6f} m")


def demo_lefranc():
    """Démonstration test Lefranc."""
    print("\n" + "="*70)
    print("DÉMO 3 : TEST LEFRANC (perméabilité)")
    print("="*70)
    
    # Données synthétiques (charge dans forage)
    times = np.array([0, 10, 30, 60, 120, 300, 600])  # secondes
    h_initial = 0.5  # m
    h_infty = 0.02   # m (charge d'équilibre)
    tau = 50  # constante de temps
    
    heads = h_infty + (h_initial - h_infty) * np.exp(-times / tau)
    heads += np.random.normal(0, 0.001, len(heads))
    
    print(f"\nDonnées test de charge (cylindre de forage)")
    print(f"Charge initiale: {h_initial:.3f} m")
    print(f"Charge finale: {h_infty:.3f} m")
    
    test = lefranc.LeffrancTest(h_initial)
    result = test.fit_exponential(times, heads, aquifer_head=h_infty)
    
    if result['success']:
        print(f"\nRésultats Lefranc:")
        print(f"  K:   {result['K']:.2e} m/s")
        print(f"  K:   {result['K']*86400:.2e} m/jour")
        print(f"  τ:   {result['tau']:.2f} s")
        print(f"  RMSE: {result['rmse']:.4f} m")


def demo_lugeon():
    """Démonstration test Lugeon."""
    print("\n" + "="*70)
    print("DÉMO 4 : TEST LUGEON (roches, injection)")
    print("="*70)
    
    test_length = 5.0  # m
    test = lugeon.LugeonTest(test_length)
    
    # Ajouter mesures
    test.add_measurement(10, 2.5)   # 10 bar, 2.5 L/min
    test.add_measurement(10, 2.3)   # Répétition
    test.add_measurement(10, 2.4)
    
    result = test.compute_mean_k()
    
    print(f"\nTest Lugeon sur {test_length:.1f} m")
    print(f"Nombre de paliers: {result['num_steps']}")
    print(f"\nRésultats:")
    print(f"  K moyen: {result['K_mean']:.2e} m/s")
    print(f"  Lugeon: {result['lugeon_mean']:.2f} UL")
    print(f"  Qualité: {test.get_quality_assessment()}")
    print(test.get_summary())


def demo_porchet():
    """Démonstration test Porchet."""
    print("\n" + "="*70)
    print("DÉMO 5 : TEST PORCHET (formations meubles)")
    print("="*70)
    
    # Données synthétiques
    times = np.array([0, 5, 15, 30, 60, 120, 300])  # s
    K_true = 1e-4  # m/s
    radius = 0.1  # m
    H0 = 0.5  # m
    
    def porchet_model(t, K):
        H0_2_3 = H0 ** (2.0/3.0)
        coeff = 2 * K / radius
        term = H0_2_3 - coeff * t
        term = np.maximum(term, 0)
        return term ** (3.0/2.0)
    
    heads = np.array([porchet_model(t, K_true) for t in times])
    heads += np.random.normal(0, 0.001, len(heads))
    
    print(f"\nPuits de {radius:.2f} m de rayon, {H0:.2f} m d'eau initial")
    
    test = porchet.PorchetTest(radius, H0)
    result = test.fit(times, heads)
    
    if result['success']:
        print(f"\nRésultats Porchet:")
        print(f"  K: {result['K']:.2e} m/s")
        print(f"  K: {result['K']*86400:.2e} m/jour")
        print(f"  RMSE: {result['rmse']:.4f} m")


def demo_piezzometry():
    """Démonstration analyse piézométrique."""
    print("\n" + "="*70)
    print("DÉMO 6 : ANALYSE PIÉZOMÉTRIQUE")
    print("="*70)
    
    from datetime import datetime, timedelta
    
    # Générer série temporelle
    base_date = datetime(2023, 1, 1)
    dates = [base_date + timedelta(days=i) for i in range(365)]
    
    # Niveau avec tendance et saisonnalité
    t = np.arange(365) / 365
    levels = 10 + 0.5 * t + 0.3 * np.sin(2*np.pi*t) + np.random.normal(0, 0.02, 365)
    
    print(f"\nSérie piézométrique: {len(dates)} mesures sur 1 an")
    
    analysis = piezo.PiezoAnalysis(dates, levels)
    
    stats = analysis.get_statistics()
    print(f"\nStatistiques:")
    print(f"  Niveau min: {stats['min']:.3f} m")
    print(f"  Niveau max: {stats['max']:.3f} m")
    print(f"  Moyenne: {stats['mean']:.3f} m")
    print(f"  Amplitude: {stats['amplitude']:.3f} m")
    
    trend = analysis.compute_trend()
    print(f"\nTendance:")
    print(f"  Pente: {trend['slope_m_year']:.4f} m/an")
    print(f"  R²: {trend['r_squared']:.3f}")
    print(f"  {trend['interpretation']}")
    
    aquifer = analysis.identify_aquifer_type()
    print(f"\nType d'aquifère:")
    print(f"  {aquifer['behavior']}")
    print(f"  {aquifer['reactivity']}")


def demo_ia_anomalies():
    """Démonstration détection d'anomalies IA."""
    print("\n" + "="*70)
    print("DÉMO 7 : DÉTECTION D'ANOMALIES (Module IA)")
    print("="*70)
    
    # Données avec anomalies
    data = np.array([1.0, 1.1, 1.05, 1.2, 10.0, 1.15, 0.95, 1.05])
    # Point 4 (valeur 10.0) est une anomalie
    
    detector = AnomalyDetector()
    idx_z, exp_z = detector.detect_outliers_zscore(data, threshold=2.5)
    
    print(f"\nDonnées: {data}")
    print(f"\nAnomalies détectées (Z-score):")
    for e in exp_z:
        print(f"  ❌ {e}")
    
    if len(exp_z) == 0:
        print("  ✓ Aucune anomalie détectée")
    
    # Check complet
    check = detector.comprehensive_check({'propriete': data})
    print(f"\nCheck complet:")
    print(f"  Contamination: {check['contamination_rate']:.1f}%")
    print(f"  Confiance: {check['confidence_score']:.0f}%")
    print(f"  Status: {check['status']}")


def demo_ia_recommendations():
    """Démonstration recommandations IA."""
    print("\n" + "="*70)
    print("DÉMO 8 : RECOMMANDATIONS DE PARAMÈTRES (Module IA)")
    print("="*70)
    
    recommender = ParameterRecommender()
    
    # Exemple 1 : Par lithologie
    print("\n1) Recommandations pour SABLES")
    result = recommender.recommend_from_lithology('sables')
    print(result['explanation'])
    
    # Exemple 2 : À partir de K mesuré
    print("\n2) Recommandations à partir de K mesuré")
    result = recommender.recommend_from_measured_data({'K_ms': 1e-4})
    print(f"  Lithologie probable: {result['recommendations'].get('lithology_guess')}")
    print(f"  Confiance: {result['confidence']:.0f}%")


def demo_ia_validation():
    """Démonstration validation pré-calcul."""
    print("\n" + "="*70)
    print("DÉMO 9 : VALIDATION PRÉ-CALCUL (Module IA)")
    print("="*70)
    
    validator = PreComputeValidator()
    
    # Test 1 : Paramètres valides
    print("\n1) Paramètres Theis valides:")
    result = validator.validate_theis_parameters(
        Q=0.001, T=1e-3, S=1e-4, distance=50, time_max=10000
    )
    print(f"  Status: {result['status']}")
    print(f"  Confiance: {result['confidence_score']:.0f}%")
    print(f"  Peut procéder: {result['can_proceed']}")
    
    # Test 2 : Paramètres problématiques
    print("\n2) Paramètres Theis problématiques:")
    result = validator.validate_theis_parameters(
        Q=-0.001, T=0, S=1.5, distance=50, time_max=10000
    )
    print(f"  Status: {result['status']}")
    print(f"  Confiance: {result['confidence_score']:.0f}%")
    if result['issues']:
        print(f"  Problèmes:")
        for issue in result['issues']:
            print(f"    {issue}")


def main():
    """Lance toutes les démonstrations."""
    print("\n" + "="*70)
    print("HYDROAI - DÉMONSTRATION COMPLÈTE DU SYSTÈME DE CALCUL")
    print("="*70)
    print("\nArchitecture scientifique modulaire :")
    print("  ✓ Modules de calcul hydrogéologiques (Theis, Cooper-Jacob, etc.)")
    print("  ✓ Tests de perméabilité (Lefranc, Lugeon, Porchet)")
    print("  ✓ Analyse piézométrique")
    print("  ✓ Module IA assistant pédagogique")
    
    try:
        demo_theis()
        demo_cooper_jacob()
        demo_lefranc()
        demo_lugeon()
        demo_porchet()
        demo_piezzometry()
        demo_ia_anomalies()
        demo_ia_recommendations()
        demo_ia_validation()
        
        print("\n" + "="*70)
        print("✓ TOUTES LES DÉMONSTRATIONS COMPLÉTÉES AVEC SUCCÈS")
        print("="*70)
        print("\nProchaines étapes:")
        print("  1. Développer solveur EF 2D pour écoulement")
        print("  2. Intégrer avec UI PySide6")
        print("  3. Ajouter import/export de données")
        print("  4. Implémenter post-traitement et visualisation")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
