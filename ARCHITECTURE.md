HydroAI - Plateforme Hydrogéologique Scientifique
==================================================

## 🎯 Vision

**HydroAI** = version étudiante d'un logiciel hydrogéologique professionnel.

### Principes fondamentaux

1. **Cœur scientifique = Modules de calcul hydrogéologiques**
   - Essais de pompage (Theis, Cooper-Jacob)
   - Tests de perméabilité (Lefranc, Lugeon, Porchet)
   - Analyse piézométrique
   - **PAS** d'approximation IA - calculs exacts et reproductibles

2. **L'IA est un assistant pédagogique, pas un moteur**
   - Détection d'anomalies dans les données
   - Recommandations de paramètres selon lithologie
   - Validation pré-calcul avec guidance
   - **Toujours** expliquer pourquoi (explicabilité)

3. **Architecture modulaire et testable**
   - Chaque calcul hydrogéologique = fichier séparé
   - Tests unitaires sur cas analytiques
   - Performance CPU suffisante (Python+NumPy)

---

## 📁 Structure du projet

```
hydroai/
├── core/                          # Cœur scientifique
│   ├── calculations/              # Modules de calcul hydrogéologiques
│   │   ├── __init__.py
│   │   ├── theis.py              # Essai Theis (conditions transitoires)
│   │   ├── cooper_jacob.py       # Approximation semi-log
│   │   ├── lefranc.py            # Test de perméabilité (forage)
│   │   ├── lugeon.py             # Test Lugeon (roches injectées)
│   │   ├── porchet.py            # Test Porchet (sables/graviers)
│   │   └── piezo.py              # Analyse piézométrique
│   │
│   ├── ai/                        # Module IA (assistant pédagogique)
│   │   ├── __init__.py
│   │   ├── anomaly_detection.py  # Détection anomalies (Z-score, IQR, spatial)
│   │   ├── parameter_recommender.py  # Recommandations par lithologie
│   │   └── validation_engine.py  # Validation pré-calcul
│   │
│   ├── solver/                    # Solveur EF (à développer)
│   │   └── __init__.py
│   │
│   ├── mesh/                      # Maillage (à développer)
│   │   └── __init__.py
│   │
│   ├── io/                        # Import/Export (à développer)
│   │   └── __init__.py
│   │
│   ├── post/                      # Post-traitement (à développer)
│   │   └── __init__.py
│   │
│   ├── project/                   # Gestion projets (à développer)
│   │   └── __init__.py
│   │
│   └── __init__.py
│
├── app/                           # Interface utilisateur (UI)
│   ├── main.py
│   ├── ui/
│   ├── data/
│   └── ...
│
├── demo_science.py                # Démonstration complète
├── requirements.txt
└── README.md
```

---

## 🔬 Modules de Calcul (core/calculations)

### 1. **Theis** (theis.py)
Solution classique pour essai de pompage en milieu confiné transitoire.

**Classe:** `TheisAnalysis`
- Calcule fonction de puits W(u)
- Estime T et S par ajustement aux données
- Génère courbes théoriques

**Usage:**
```python
from core.calculations import theis

analysis = theis.TheisAnalysis(Q=0.001, distance=50, times=times, drawdowns=drawdowns)
result = analysis.fit()
print(f"T={result['T']}, S={result['S']}")
```

### 2. **Cooper-Jacob** (cooper_jacob.py)
Approximation semi-log valide pour u < 0.05. Plus simple graphiquement.

**Classe:** `CooperJacobAnalysis`
- Fit linéaire en log10(t)
- Calcule T et S par extrapolation
- Mesure validité de l'approximation

### 3. **Lefranc** (lefranc.py)
Test de perméabilité en forage (charge/décharge).

**Classe:** `LeffrancTest`
- Fit exponentiel de décroissance
- Calcule K selon géométrie (cylindre, packer)

### 4. **Lugeon** (lugeon.py)
Test d'injectivité pour roches. Mesure en "Lugeons" (unité standard).

**Classe:** `LugeonTest`
- Injection progressive (5→10→5 bar)
- Calcul perméabilité normalisée
- Évaluation qualité test

### 5. **Porchet** (porchet.py)
Test de perméabilité pour formations meubles. Méthode du puits peu profond.

**Classe:** `PorchetTest`
- Solution analytique éq. différentielle
- Fit courbe baisse de charge

### 6. **Piézométrie** (piezo.py)
Analyse séries piézométriques (niveaux d'eau).

**Classe:** `PiezoAnalysis`
- Statistiques descriptives
- Tendance long terme (linéaire)
- Classification type aquifère
- Courbe remontée / dérivée

---

## 🤖 Module IA (core/ai)

**Philosophie:** L'IA n'est PAS un moteur de calcul. C'est un guide pédagogique.

### 1. **Détection d'Anomalies** (anomaly_detection.py)

**Classe:** `AnomalyDetector`

Méthodes explicables:
- **Z-score**: Points à N écarts-types de moyenne
- **IQR**: Points en dehors quartiles
- **Spatial**: Points isolés de leurs voisins

Retourne pour chaque anomalie: index + explication textuelle

```python
detector = AnomalyDetector()
idx, explanations = detector.detect_outliers_zscore(data, threshold=3.0)
# "Point 4: valeur=10.2, Z-score=5.0 (à 5.0σ de la moyenne 1.0)"
```

### 2. **Recommandeur de Paramètres** (parameter_recommender.py)

**Classe:** `ParameterRecommender`

Base de données lithologies:
- Graviers, sables, silt/limon, argile
- Calcaire fissuré, granite fissuré

Pour chaque lithologie : plages typiques K, porosité, coefficient emmagasinement.

```python
recommender = ParameterRecommender()
result = recommender.recommend_from_lithology('sables')
# → K: 1e-3 à 1e-5 m/s
# → Porosité: 25-40%
# → Explication textuelle pédagogique
```

### 3. **Validation Pré-calcul** (validation_engine.py)

**Classe:** `PreComputeValidator`

Vérifie AVANT simulation:
- Cohérence Theis (Q, T, S, distance, temps)
- Cohérence géologie (K, porosité, S)
- Validité conditions aux limites

Status: OK / ATTENTION / **BLOQUÉ**

```python
validator = PreComputeValidator()
result = validator.validate_theis_parameters(Q=0.001, T=1e-3, S=1e-4, ...)
# Status: "OK" (confiance 95%)
# Ou: "BLOQUÉ" avec liste problèmes
```

---

## 🎓 Utilisation pédagogique

### Workflow typique étudiant :

1. **Importer données** (essai pompage)
   - UI: sélectionner fichier CSV
   - IA: détecte anomalies → guidance pour nettoyage

2. **Choisir méthode**
   - "Theis" pour transitoire long
   - "Cooper-Jacob" pour approx simple
   - IA: recommande selon contexte

3. **Tester paramètres**
   - IA: suggère K et S selon lithologie
   - UI: affiche courbes comparaison (mesure vs théorie)

4. **Validation**
   - IA: score de confiance pré-calcul
   - Peut lancer simulation si OK

5. **Interpréter résultats**
   - IA: explique ce que T et S signifient
   - Aquifère captif vs libre?
   - Hétérogénéités?

---

## 🏗️ Prochaines étapes (Priorité)

### Phase 1 (MVP Core - 2-3 semaines)

1. **Solveur EF 2D** (solver/)
   - Assemblage éléments finis simple
   - Conditions Dirichlet/Neumann
   - Solveur linéaire sparse (scipy)
   - Validation sur solutions analytiques (Thiem, Theis, etc.)

2. **UI dynamique** (app/ + PySide6)
   - Home tab
   - Tab "Essais Pompage" (Theis/Cooper-Jacob)
   - Tab "Perméabilité" (Lefranc/Lugeon/Porchet)
   - Tab "Piézométrie"
   - Interconnexion avec modules scientifiques

3. **I/O complet** (io/)
   - CSV, XLSX, GRD, GeoTIFF, SHP importers
   - Validateurs de format
   - Exporters PDF/PNG/CSV des résultats

### Phase 2 (Solveur temps + Transport - 3-4 semaines)

- Schémas temps implicites (Euler implicite, Crank-Nicolson)
- Pas temps adaptatif
- Advection-dispersion simple
- Sorption linéaire

### Phase 3 (IA embarquée + Visualisation)

- Entraînement modèles localement
- Cartes 2D/3D, coupes, séries temp
- Export rapports PDF automatisés
- ONNX pour portabilité

---

## 📚 Références scientifiques

**Theis/Cooper-Jacob:**
- Theis, C.V. (1935) - Solution classique
- Cooper & Jacob (1946) - Approximation semi-log
- Domenico & Schwartz (1998)

**Tests perméabilité:**
- Lefranc, P. et al. (1991)
- Lugeon, A. (1933)
- Porchet, G. (1991)

---

## 💻 Dépendances

```
numpy >= 1.23.0
scipy >= 1.9.0
pandas >= 1.5.0
PySide6 >= 6.4.0
matplotlib >= 3.5.0
```

---

## 🧪 Tests et Validation

Structure tests:
```
tests/
├── test_theis.py           # Cas analytiques
├── test_cooper_jacob.py
├── test_lefranc.py
├── test_lugeon.py
├── test_porchet.py
├── test_piezo.py
├── test_anomaly_detection.py
├── test_ai_validator.py
└── test_solver_2d.py       # EF validation
```

**Critères acceptation:**
- RMSE < 0.1% sur solutions analytiques
- Détection anomalies : TP/FP/TN/FN mesurés
- UI responsive (< 100ms interactions)

---

## 📝 Licence et Attribution

HydroAI - Plateforme pédagogique d'apprentissage en hydrogéologie.

Basée sur standards scientifiques établis en hydrogeologie et géotechnique.

---

## 👥 Équipe développement

- Architecture et design
- Modules de calcul scientifiques
- Interface utilisateur PySide6
- Module IA assistant
- Tests et validation

---

**Date création:** November 2025
**Version:** 0.1.0-alpha
**Statut:** Architecture scientifique complète, UI en développement, Solveur EF planifié
