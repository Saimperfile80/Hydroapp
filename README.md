# HydroAI

**Plateforme de modélisation hydrogéologique avec IA embarquée**

Version étudiante de qualité professionnelle pour apprentissage et recherche.

---

## 🎯 Vision

HydroAI = **outil pédagogique sérieux** basé sur:

1. **Modules de calcul scientifiques rigoureux**
   - Essais de pompage (Theis, Cooper-Jacob)
   - Tests de perméabilité (Lefranc, Lugeon, Porchet)
   - Analyse piézométrique
   - Solveur EF pour écoulement saturé (en cours)

2. **Assistant IA pédagogique** (PAS un moteur de calcul)
   - Détection d'anomalies dans données
   - Recommandations de paramètres
   - Validation pré-calcul
   - **Explicabilité** sur chaque décision

3. **Interface utilisateur** intuitive (PySide6)
   - Import/export multiformat
   - Visualisation courbes
   - Gestion projets
   - Rapports PDF automatisés

---

## ✅ État du projet

### Phase 1 : Architecture scientifique ✅ COMPLÈTE

- ✅ 6 modules de calcul hydrogéologiques (1,700 lignes)
- ✅ 3 modules IA explicable (950 lignes)
- ✅ Structure modulaire scalable
- 🔄 Frontend PySide6 (en cours)
- ⏳ Solveur EF 2D (planifié)

---

## 🚀 Installation rapide

### Prérequis
- Python 3.8+
- pip ou conda

### Installation

```bash
# Cloner le repo
git clone https://github.com/hydroai/hydroai.git
cd hydroai

# Installer dépendances
pip install -r requirements.txt
```

### Dépendances
```
numpy >= 1.23.0
scipy >= 1.9.0
pandas >= 1.5.0
PySide6 >= 6.4.0
matplotlib >= 3.5.0
```

---

## 📖 Guide rapide

### Cas 1 : Essai Theis

```python
from core.calculations import theis
import numpy as np

# Données
Q = 0.001  # m³/s
distance = 50  # m
times = np.array([10, 50, 100, 500, 1000])
drawdowns = np.array([0.02, 0.045, 0.062, 0.115, 0.145])

# Analyse
analysis = theis.TheisAnalysis(Q, distance, times, drawdowns)
result = analysis.fit()

print(f"T = {result['T']:.2e} m²/s")
print(f"S = {result['S']:.2e}")
```

### Cas 2 : Détection anomalies

```python
from core.ai import AnomalyDetector

detector = AnomalyDetector()
idx, explanations = detector.detect_outliers_zscore(data)

for e in explanations:
    print(f"❌ {e}")
```

### Cas 3 : Recommandations

```python
from core.ai import ParameterRecommender

recommender = ParameterRecommender()
result = recommender.recommend_from_lithology('sables')
print(result['explanation'])
```

Voir `GUIDE_ETUDIANT.py` pour exemples complets.

---

## 📁 Structure

```
hydroai/
├── core/
│   ├── calculations/          # Modules hydrogéologiques
│   │   ├── theis.py
│   │   ├── cooper_jacob.py
│   │   ├── lefranc.py
│   │   ├── lugeon.py
│   │   ├── porchet.py
│   │   └── piezo.py
│   ├── ai/                    # Assistant pédagogique
│   │   ├── anomaly_detection.py
│   │   ├── parameter_recommender.py
│   │   └── validation_engine.py
│   ├── solver/                # Solveur EF (en développement)
│   ├── mesh/                  # Maillage (en développement)
│   ├── io/                    # Import/Export (en développement)
│   └── ...
├── app/                       # Interface utilisateur
├── tests/                     # Tests unitaires
├── ARCHITECTURE.md            # Architecture complète
├── GUIDE_ETUDIANT.py          # Guide d'utilisation
└── requirements.txt
```

---

## 🔬 Modules disponibles

### Modules de calcul

| Module | Description | Classe | Usage |
|--------|-------------|--------|-------|
| **Theis** | Essai pompage (Theis 1935) | `TheisAnalysis` | Aquifère confiné, transitoire |
| **Cooper-Jacob** | Approximation semi-log | `CooperJacobAnalysis` | Simplification graphique |
| **Lefranc** | Test de charge/décharge | `LeffrancTest` | Perméabilité in situ forage |
| **Lugeon** | Test injection roches | `LugeonTest` | Qualification massif rocheux |
| **Porchet** | Test formations meubles | `PorchetTest` | Sables/graviers superficiels |
| **Piézométrie** | Analyse niveaux d'eau | `PiezoAnalysis` | Séries temporelles |

### Module IA

| Component | Description |
|-----------|-------------|
| **Anomaly Detection** | Z-score, IQR, spatial outliers |
| **Parameter Recommender** | Plages par lithologie |
| **Validation Engine** | Check pré-calcul (OK/ATTENTION/BLOQUÉ) |

---

## 🎓 Pour les étudiants

HydroAI est conçu comme outil d'apprentissage:

- **Résultats reproductibles** : chaque calcul suit une méthode scientifique standard
- **Explications** : l'IA aide à comprendre pourquoi, pas juste donner réponse
- **Guidage** : détection anomalies, recommandations paramétriques
- **Validation** : vérification cohérence avant simulation

**Voir `GUIDE_ETUDIANT.py` pour cas complets.**

---

## 🧪 Tests

```bash
# Lancer tests
pytest tests/

# Test spécifique
pytest tests/test_theis.py

# Avec couverture
pytest --cov=core tests/
```

Cas de test incluent:
- Solutions analytiques (Thiem, Theis)
- Données synthétiques avec anomalies connues
- Validation format import/export

---

## 📊 Performance

- **Theis** : < 100 ms pour 100 points
- **Cooper-Jacob** : < 50 ms (fit linéaire)
- **Détection anomalies** : < 10 ms pour 1000 points
- **Solveur EF** (planifié) : dépend taille maillage

---

## 🔄 Roadmap

### Phase 1 (MVP - Nov-Déc 2025)
- ✅ Architecture scientifique
- ⏳ Frontend PySide6 avec onglets
- ⏳ Module I/O (CSV, XLSX, GRD)
- ⏳ Visualisation matplotlib

### Phase 2 (Solveur - Jan-Fév 2026)
- ⏳ Solveur EF 2D steady-state
- ⏳ Conditions aux limites (Dirichlet, Neumann, etc.)
- ⏳ Schémas temps (Euler implicite)
- ⏳ Validation analytique

### Phase 3 (Complet - Mar-Avr 2026)
- ⏳ Transport et hydrochimie
- ⏳ Bassin versant
- ⏳ IA entraînement embarqué
- ⏳ Export PDF rapports

---

## 🤝 Contribution

Les contributions sont bienvenues!

1. Fork le repo
2. Créer branche (`git checkout -b feature/xyz`)
3. Commit changements (`git commit -am 'Add feature'`)
4. Push branche (`git push origin feature/xyz`)
5. Ouvrir Pull Request

---

## 📄 Licence

MIT License - Voir LICENSE.md

---

## 👥 Équipe

Développé à l'Université/Institut de Recherche [TBD]

---

## 📞 Support

- **Documentation** : `ARCHITECTURE.md`
- **Guide étudiant** : `GUIDE_ETUDIANT.py`
- **Issues GitHub** : [hydroai/issues](https://github.com/hydroai/hydroai/issues)
- **Discussions** : [hydroai/discussions](https://github.com/hydroai/hydroai/discussions)

---

## 🔗 Ressources

### Références scientifiques
- Theis, C.V. (1935). "The relation between the lowering of the piezometric surface..."
- Cooper, H.H. & Jacob, C.E. (1946). "A generalized graphical method..."
- Domenico, P.A. & Schwartz, F.W. (1998). "Physical and Chemical Hydrogeology"

### Outils connexes
- FEFLOW (commercial, inspiration)
- PEST (calibration)
- PyGMSH (maillage)
- Matplotlib (visualisation)

---

## ❤️ Merci

Merci d'utiliser HydroAI pour votre apprentissage et recherche en hydrogéologie!

**Contribuez à une meilleure compréhension des ressources en eau souterraine.**

---

*Dernière mise à jour : November 2025*
*Version : 0.1.0-alpha*
