#!/usr/bin/env python3
"""
GUIDE D'UTILISATION HYDROAI pour Étudiants
===========================================

Exemples pratiques d'utilisation des modules scientifiques HydroAI.
Chaque exemple montre comment traiter un cas réel d'essai hydrogéologiques.
"""

print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    🎓 GUIDE D'UTILISATION HYDROAI                             ║
║               Plateforme pédagogique de modélisation hydrogéologique          ║
╚═══════════════════════════════════════════════════════════════════════════════╝

PHILOSOPHIE
===========

HydroAI est conçu comme outil d'apprentissage :

  1. RIGUEUR SCIENTIFIQUE
     → Chaque calcul correspond à une méthode scientifique reconnue
     → Les résultats sont reproductibles et validables
  
  2. PÉDAGOGIE
     → L'IA ne remplace jamais le calcul
     → L'IA explique le choix de méthode
     → Les courbes montrent résultat théorique vs mesure
  
  3. GUIDANCE
     → Suggère paramètres selon géologie
     → Détecte anomalies dans données
     → Valide cohérence avant calcul


STRUCTURE DU PROJET
==================

   core/
   ├── calculations/     ← Modules de calcul (Theis, Cooper-Jacob, etc.)
   ├── ai/              ← Assistant pédagogique (détection, recommandation)
   ├── solver/          ← Solveur EF (en développement)
   └── io/              ← Import/Export (en développement)


CAS D'USAGE 1 : ESSAI DE POMPAGE THEIS
=======================================

CONTEXTE:
  Vous avez réalisé un essai de pompage en aquifère confiné.
  Vous mesurez le rabattement en fonction du temps.
  OBJECTIF: Estimer T (transmissivité) et S (coefficient emmagasinement)

DONNÉES (à préparer):
  • Débit de pompage constant : Q = 0.001 m³/s
  • Distance puits-piézomètre : r = 50 m
  • Temps (s) : [10, 50, 100, 500, 1000, 5000]
  • Rabattements (m) : [0.02, 0.045, 0.062, 0.115, 0.145, 0.200]

CODE:
  from core.calculations import theis
  import numpy as np
  
  Q = 0.001          # m³/s
  distance = 50      # m
  times = np.array([10, 50, 100, 500, 1000, 5000])
  drawdowns = np.array([0.02, 0.045, 0.062, 0.115, 0.145, 0.200])
  
  # Créer analyse
  analysis = theis.TheisAnalysis(Q, distance, times, drawdowns)
  
  # Ajuster aux données
  result = analysis.fit()
  
  # Afficher résultats
  print(f"Transmissivité T: {result['T']:.2e} m²/s")
  print(f"Coefficient S: {result['S']:.2e}")
  print(f"Qualité ajustement (RMSE): {result['rmse']:.4f} m")

INTERPRÉTATION:
  • T mesure facilité écoulement dans aquifère
  • S mesure capacité emmagasinement
  • Rapport S/porosité indique : libre (haut) vs captif (bas)

MODULE IA RECOMMANDE:
  → Si T > 1e-2 : "Transmissivité très élevée (atypique)"
  → Si S < 1e-6 : "Aquifère très captif (profond?)"
  → Si RMSE élevée : "Vérifier qualité mesures"


CAS D'USAGE 2 : ESSAI DE POMPAGE COOPER-JACOB
==============================================

CONTEXTE:
  Simplification graphique de Theis pour temps tardifs.
  AVANTAGE: Fit linéaire simple, moins de paramètres
  CONDITION: u = r²S/(4Tt) < 0.05

DONNÉES (même que Theis mais plus points):
  • 50 mesures sur plage log(t) large
  
CODE:
  from core.calculations import cooper_jacob
  
  analysis = cooper_jacob.CooperJacobAnalysis(Q, distance, times, drawdowns)
  result = analysis.fit_linear()
  
  print(f"Transmissivité: {result['T']:.2e} m²/s")
  print(f"Pente (Δs/Δlog₁₀t): {result['slope']:.4f} m")
  print(f"Validité u<0.05: {result['validity_percentage']:.1f}%")

COMPARAISON THEIS vs COOPER-JACOB:
  • Theis : plus complexe, valable tous les temps
  • Cooper-Jacob : simplifié, que pour u<0.05
  • Courbe semi-log montre région linéaire


CAS D'USAGE 3 : TEST DE PERMÉABILITÉ LEFRANC
==============================================

CONTEXTE:
  Test in situ de perméabilité dans forage.
  Montée rapide de charge, suivi de baisse.
  OBJECTIF: Estimer K (conductivité)

DONNÉES:
  • Charge initiale: 0.5 m
  • Temps (s): [0, 10, 30, 60, 120, 300, 600]
  • Charges (m): [0.5, 0.35, 0.25, 0.18, 0.10, 0.04, 0.02]

CODE:
  from core.calculations import lefranc
  
  test = lefranc.LeffrancTest(initial_head=0.5)
  result = test.fit_exponential(times, heads, aquifer_head=0.02)
  
  print(f"Conductivité K: {result['K']:.2e} m/s")
  print(f"K en m/jour: {result['K']*86400:.2e}")

INTERPRÉTATION:
  K est paramètre clé:
  • K > 1e-3 : Très perméable (graviers)
  • K ~ 1e-5 : Moyen (sables)
  • K < 1e-7 : Peu perméable (argile)

MODULE IA RECOMMANDE:
  Après entrée K, propose lithologie probable et explique


CAS D'USAGE 4 : TEST LUGEON (ROCHES)
====================================

CONTEXTE:
  Test d'injection d'eau à pression croissante.
  Standard en génie civil pour qualifier roches.
  Résultat en "Lugeons" = débit L/min/m à 10 bar

DONNÉES (paliers 5, 10, 15, 10, 5 bar):
  Pressions: [5, 10, 15, 10, 5]
  Débits: [1.2, 2.5, 3.8, 2.4, 1.1]

CODE:
  from core.calculations import lugeon
  
  test = lugeon.LugeonTest(test_length=5.0)  # 5 m de test
  
  test.add_measurement(5, 1.2)
  test.add_measurement(10, 2.5)
  test.add_measurement(15, 3.8)
  test.add_measurement(10, 2.4)
  test.add_measurement(5, 1.1)
  
  result = test.compute_mean_k()
  
  print(f"Lugeons: {result['lugeon_mean']:.2f} UL")
  print(f"Conductivité: {result['K_mean']:.2e} m/s")
  print(f"Qualité: {test.get_quality_assessment()}")

INTERPRÉTATION:
  Lugeons (UL) standards:
  • < 1 : Excellent (roches saines)
  • 1-10 : Bon
  • 10-100 : Passable (injection recommandée)
  • > 100 : Mauvais (grosse fissuration)


CAS D'USAGE 5 : TEST PORCHET (FORMATIONS MEUBLES)
=================================================

CONTEXTE:
  Puits peu profond dans sables/graviers.
  Mesure vitesse baisse de charge.

CODE:
  from core.calculations import porchet
  
  test = porchet.PorchetTest(radius=0.1, initial_head=0.5)
  result = test.fit(times, heads)
  
  print(f"Conductivité: {result['K']:.2e} m/s")


CAS D'USAGE 6 : ANALYSE PIÉZOMÉTRIQUE
=====================================

CONTEXTE:
  Suivi de niveaux d'eau sur 1 an dans piézomètre.
  Identifier: tendance, saisonnalité, type aquifère

CODE:
  from core.calculations import piezo
  from datetime import datetime, timedelta
  
  dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(365)]
  levels = [10.5, 10.4, 10.2, 9.8, 9.5, 9.2, ...]  # en mètres
  
  analysis = piezo.PiezoAnalysis(dates, levels)
  
  # Statistiques
  stats = analysis.get_statistics()
  print(f"Amplitude: {stats['amplitude']:.2f} m")
  
  # Tendance
  trend = analysis.compute_trend()
  print(f"Pente long terme: {trend['slope_m_year']:.4f} m/an")
  print(f"Interprétation: {trend['interpretation']}")
  
  # Type aquifère
  aquifer = analysis.identify_aquifer_type()
  print(f"{aquifer['behavior']}")
  print(f"{aquifer['reactivity']}")


CAS D'USAGE 7 : DÉTECTION D'ANOMALIES (IA)
==========================================

CONTEXTE:
  Vos données de mesure contiennent peut-être des erreurs.
  L'IA aide à les identifier.

CODE:
  from core.ai import AnomalyDetector
  
  detector = AnomalyDetector()
  
  data = np.array([1.0, 1.05, 0.98, 1.1, 15.0, 1.02])  # Point 4 = anomalie
  
  # Détection
  idx, explanations = detector.detect_outliers_zscore(data)
  
  for e in explanations:
      print(f"  ❌ {e}")
  
  # Check complet
  check = detector.comprehensive_check({'rabattement': data})
  print(f"Status: {check['status']}")
  print(f"Confiance: {check['confidence_score']:.0f}%")

RÉSULTAT:
  ❌ Point 4: valeur=15.0, Z-score=8.3 (à 8.3σ de la moyenne 1.05)
  
  Status: ATTENTION
  Confiance: 70%
  → Vérifier ce point (erreur mesure? événement réel?)


CAS D'USAGE 8 : RECOMMANDATIONS DE PARAMÈTRES (IA)
==================================================

CONTEXTE:
  Vous avez mesuré K. Vous voulez estimations de porosité, S, etc.
  L'IA recommande basé sur lithologie.

CODE:
  from core.ai import ParameterRecommender
  
  recommender = ParameterRecommender()
  
  # Option 1 : Recommander par lithologie
  result = recommender.recommend_from_lithology('sables')
  print(result['explanation'])
  
  # Option 2 : À partir de K mesuré
  result = recommender.recommend_from_measured_data({'K_ms': 1e-4})
  print(f"Lithologie probable: {result['recommendations']['lithology_guess']}")
  print(f"Confiance: {result['confidence']:.0f}%")

OUTPUT:
  Lithologie probable: sables
  Confiance: 85%
  
  Plages recommandées:
  • K: 1e-3 à 1e-5 m/s
  • Porosité: 25-40%
  • Coefficient emmagasinement: 1e-3 à 1e-4
  
  Explication pédagogique...


CAS D'USAGE 9 : VALIDATION PRÉ-CALCUL (IA)
==========================================

CONTEXTE:
  Avant lancer simulation, vérifier cohérence paramètres.

CODE:
  from core.ai import PreComputeValidator
  
  validator = PreComputeValidator()
  
  result = validator.validate_theis_parameters(
      Q=0.001, T=1e-3, S=1e-4, distance=50, time_max=10000
  )
  
  print(f"Status: {result['status']}")           # OK / ATTENTION / BLOQUÉ
  print(f"Confiance: {result['confidence_score']:.0f}%")
  print(f"Peut procéder: {result['can_proceed']}")
  
  if not result['can_proceed']:
      for issue in result['issues']:
          print(f"  ❌ {issue}")
  
  for warning in result['warnings']:
      print(f"  ⚠ {warning}")

RÉSULTATS POSSIBLES:
  ✓ OK (100%) : Tous paramètres cohérents
  ⚠ ATTENTION (85%) : Vérifier certaines valeurs
  ❌ BLOQUÉ (0%) : Erreur bloquante


WORKFLOW COMPLET D'UN ÉTUDIANT
=============================

Jour 1 - Essai de pompage:
  1. Importer données CSV (essai Theis)
  2. Vérifier avec IA → détection anomalies
  3. Choisir méthode Theis ou Cooper-Jacob
  4. Obtenir T et S → enregistrer dans projet

Jour 2 - Analyse génie civil:
  5. Lefranc / Lugeon / Porchet
  6. Comparer résultats avec Theis
  7. Identifier lithologie

Jour 3 - Interprétation:
  8. Analyse piézométrique long terme
  9. IA recommande plages cohérentes
  10. Rapport final avec courbes


BONNES PRATIQUES
=================

✓ FAIRE:
  • Importer données brutes sans nettoyage préalable
  • Laisser IA détecter anomalies
  • Valider recommandations IA avant de les accepter
  • Documenter chaque étape du calcul
  • Comparer plusieurs méthodes (Theis + Cooper-Jacob)
  
❌ NE PAS FAIRE:
  • Forcer résultats IA si incompatible
  • Ignorer avertissements "ATTENTION"
  • Utiliser données avec anomalies détectées
  • Accepter paramètres sans vérifier cohérence
  • Lancer simulation si IA dit "BLOQUÉ"


DÉPANNAGE
=========

Q: "Mon ajustement Theis a RMSE très élevé"
A: 
  1. Vérifier données aberrantes (IA détection)
  2. Tenter Cooper-Jacob (peut être mieux)
  3. Vérifier Q constant durant essai
  4. Vérifier distance puits-piézomètre

Q: "Lithologie recommandée ne correspond pas terrain"
A:
  1. Valeurs K sont plages typiques, pas exactes
  2. Terrain peut avoir hétérogénéités
  3. Mesurer K localement (Lefranc)
  4. Combiner plusieurs tests

Q: "Validation pré-calcul bloquée, pourquoi?"
A: Lire messages d'erreur, corriger paramètres
   Exemple: S doit être < porosité


RESSOURCES
==========

Documentation:
  • ARCHITECTURE.md : Vue d'ensemble technique
  • Code source dans core/calculations/ : Commentaires détaillés
  • Docstrings Python : Aide interactif

Références scientifiques:
  • Theis, C.V. (1935) - Classique
  • Cooper & Jacob (1946) - Semi-log
  • Domenico & Schwartz (1998) - Livre référence
  • Lefranc et al. (1991) - Tests in situ


═══════════════════════════════════════════════════════════════════════════════

Bon travail et explorateur responsable du sous-sol! 🌍

═══════════════════════════════════════════════════════════════════════════════
""")
