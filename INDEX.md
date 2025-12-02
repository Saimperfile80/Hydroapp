# HydroAI - Documentation Index

**Bienvenue dans HydroAI!** Plateforme pédagogique pour modélisation hydrogéologique.

---

## 🚀 Démarrage (Choisir selon votre situation)

### Je viens d'installer HydroAI
1. **Lire d'abord**: [QUICKSTART.md](QUICKSTART.md) (5 minutes)
2. **Lancer**: `python launcher.py` ou `python run.py`
3. **Tester**: Onglet "Essais Pompage" avec données test

### Je suis sur Windows et j'ai des problèmes
1. **Lire**: [INSTALLATION_WINDOWS.txt](INSTALLATION_WINDOWS.txt)
2. **Troubleshooting**: Section "TROUBLESHOOTING" du guide Windows
3. **Test rapide**: `python check_install.py` ou `powershell quick_start.ps1`

### Je veux comprendre l'architecture
1. **Vue d'ensemble**: [README.md](README.md)
2. **Détails techniques**: [ARCHITECTURE.md](ARCHITECTURE.md)
3. **Code source**: Voir docstrings dans fichiers Python

### Je suis étudiant et je veux des exemples
1. **Guide étudiant**: [GUIDE_ETUDIANT.py](GUIDE_ETUDIANT.py) - 9 cas d'étude complets
2. **Données test**: Voir exemples dans QUICKSTART.md
3. **Interface**: Onglet "Accueil" dans application pour guide rapide

---

## 📚 Documentation par sujet

### UTILISATION APPLICATION

| Document | Contenu | Durée |
|----------|---------|-------|
| **[QUICKSTART.md](QUICKSTART.md)** ⭐ | Guide 5 min, installation, premiers pas | 5 min |
| **[README.md](README.md)** | Vue d'ensemble features, structure | 10 min |
| **[INSTALLATION_WINDOWS.txt](INSTALLATION_WINDOWS.txt)** | Installation step-by-step Windows | 15 min |
| **[GUIDE_ETUDIANT.py](GUIDE_ETUDIANT.py)** | 9 cas d'étude réels avec code | 1-2 h |

### TECHNIQUE & DEVELOPMENT

| Document | Contenu | Audience |
|----------|---------|----------|
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Architecture système, modules, API | Développeurs |
| **[RÉSUMÉ_CRÉATION.py](RÉSUMÉ_CRÉATION.py)** | Historique création, fichiers | Mainteneurs |
| **[LIVRABLE_MVP.md](LIVRABLE_MVP.md)** | Livrable MVP complet | Product |
| **[MANIFEST.txt](MANIFEST.txt)** | Liste détaillée fichiers créés | Audit |

### DEMARRAGE RAPIDE

| Script | Commande | Effet |
|--------|----------|-------|
| **launcher.py** | `python launcher.py` | Lancer app avec vérification |
| **run.py** | `python run.py` | Lancer app directement |
| **check_install.py** | `python check_install.py` | Vérifier installation |
| **quick_start.ps1** | `powershell quick_start.ps1` | Vérif complète (Windows) |

---

## 🎯 Workflows courants

### Workflow 1: Installation & Premier lancement (10 min)

```
1. Installer Python (3.8+) ← si nécessaire
2. Installer packages: pip install numpy scipy pandas PySide6 matplotlib
3. Lancer: python launcher.py
4. Voir fenêtre PySide6 ✓
```

**Voir**: [INSTALLATION_WINDOWS.txt](INSTALLATION_WINDOWS.txt) section "STEP 1-4"

---

### Workflow 2: Analyser essai Theis (15 min)

```
1. Lancer application: python launcher.py
2. Onglet "Essais Pompage"
3. Saisir ou importer données temps + rabattement
4. Cliquer "✓ Valider" → voir IA validation
5. Cliquer "▶ Analyser" → voir T, S, graphique
```

**Voir**: [QUICKSTART.md](QUICKSTART.md) section "Cas 1: Essai Theis"

**Code Python équivalent**:
```python
from core.calculations import theis
import numpy as np

analysis = theis.TheisAnalysis(
    Q=0.001, distance=50,
    times=np.array([10, 50, 100, 500, 1000]),
    drawdowns=np.array([0.02, 0.045, 0.062, 0.115, 0.145])
)
result = analysis.fit()
print(f"T={result['T']:.2e}, S={result['S']:.2e}")
```

---

### Workflow 3: Tester calculs directement (Python)

```python
# Importer modules
from core.calculations import theis, cooper_jacob, lefranc
from core.ai import AnomalyDetector, ParameterRecommender

# Faire calcul
analysis = theis.TheisAnalysis(...)
result = analysis.fit()

# Valider
from core.ai import PreComputeValidator
validator = PreComputeValidator()
validation = validator.validate_theis_parameters(...)

# Recommander
recommender = ParameterRecommender()
recommendation = recommender.recommend_from_lithology('sables')
```

**Voir**: [ARCHITECTURE.md](ARCHITECTURE.md) section "API Examples"

---

### Workflow 4: Dépanner problème (30 min)

```
Si erreur au lancement:
1. Vérifier Python: python --version (doit être 3.8+)
2. Vérifier pip: pip list (doit voir numpy, scipy, PySide6)
3. Lancer diagnostic: python check_install.py
4. Lire resultat → see INSTALLATION_WINDOWS.txt troubleshooting
```

---

## 📂 Structure fichiers importantes

```
hydroai/
├── 📖 Documentation
│   ├── README.md ⭐ (READ FIRST)
│   ├── QUICKSTART.md ⭐ (5 min guide)
│   ├── ARCHITECTURE.md (technical)
│   ├── GUIDE_ETUDIANT.py (9 cases)
│   ├── INSTALLATION_WINDOWS.txt (windows setup)
│   └── (autres guides)
│
├── 💻 Code Application
│   ├── launcher.py ⭐ (UTILISER CECI)
│   ├── run.py (alternative)
│   ├── check_install.py (test)
│   ├── app/main_app.py (PySide6 app)
│   └── app/ui/tabs/ (4 onglets)
│
├── 🔬 Modules scientifiques
│   ├── core/calculations/ (6 méthodes hydrogéo)
│   │   ├── theis.py ⭐
│   │   ├── cooper_jacob.py ⭐
│   │   ├── lefranc.py
│   │   ├── lugeon.py
│   │   ├── porchet.py
│   │   └── piezo.py
│   │
│   └── core/ai/ (3 modules pédagogiques)
│       ├── anomaly_detection.py
│       ├── parameter_recommender.py
│       └── validation_engine.py
│
└── ⚙️ Configuration
    └── requirements.txt (dépendances)
```

---

## 🎓 Pour différentes audiences

### Pour ÉTUDIANTS
1. **Premiers pas**: [QUICKSTART.md](QUICKSTART.md)
2. **Apprendre par l'exemple**: [GUIDE_ETUDIANT.py](GUIDE_ETUDIANT.py)
3. **Comprendre modèles**: [README.md](README.md) + app Accueil
4. **Questions techniques**: [ARCHITECTURE.md](ARCHITECTURE.md)

### Pour ENSEIGNANTS
1. **Comprendre features**: [README.md](README.md)
2. **Cas d'étude**: [GUIDE_ETUDIANT.py](GUIDE_ETUDIANT.py)
3. **Architecture pédagogique**: [ARCHITECTURE.md](ARCHITECTURE.md)
4. **Installation classe**: [INSTALLATION_WINDOWS.txt](INSTALLATION_WINDOWS.txt)

### Pour DEVELOPPEURS
1. **Architecture complète**: [ARCHITECTURE.md](ARCHITECTURE.md)
2. **API reference**: Docstrings dans code (app/main_app.py, core/*)
3. **Roadmap futures phases**: [LIVRABLE_MVP.md](LIVRABLE_MVP.md)
4. **Contribution setup**: Voir dépôt GitHub

### Pour ADMINISTRATEURS IT
1. **Installation multiclient**: [INSTALLATION_WINDOWS.txt](INSTALLATION_WINDOWS.txt)
2. **Dépendances**: [requirements.txt](requirements.txt)
3. **Vérification installation**: `python check_install.py`
4. **Support utilisateur**: Points TROUBLESHOOTING

---

## 📞 FAQ Rapide

**Q: Ça prend combien de temps à installer?**
A: ~5 minutes (Python 3+ déjà installé) + ~2 min lancement
   → Voir [QUICKSTART.md](QUICKSTART.md)

**Q: Quels sont les prérequis?**
A: Python 3.8+, numpy, scipy, PySide6
   → Voir [requirements.txt](requirements.txt)

**Q: Comment importer mes propres données?**
A: Format CSV: (temps, rabattement) par ligne
   → Voir [GUIDE_ETUDIANT.py](GUIDE_ETUDIANT.py) cas 1

**Q: L'app est lente?**
A: Normal première fois (~5-10 sec). Après cache → rapide.
   → Voir [INSTALLATION_WINDOWS.txt](INSTALLATION_WINDOWS.txt) troubleshooting

**Q: Ça marche sur Mac/Linux?**
A: Oui (Python + PySide6 cross-platform)
   → Adapt [INSTALLATION_WINDOWS.txt](INSTALLATION_WINDOWS.txt) instructions

---

## 🚦 Commandes essentielles

```bash
# Installation (une fois)
pip install -r requirements.txt

# OU manuel
pip install numpy scipy pandas PySide6 matplotlib

# Vérifier
python check_install.py
powershell quick_start.ps1  # Windows

# Lancer
python launcher.py          # Recommandé
python run.py               # Alt

# Lancer tests
pytest tests/               # Si tests présents
```

---

## 📊 Statut projet

**Version**: 0.1.0-alpha MVP  
**Status**: ✅ Opérationnel  
**Date**: November 26, 2025

| Aspect | Statut |
|--------|--------|
| Calculs scientifiques | ✅ |
| Interface UI | ✅ |
| IA pédagogique | ✅ |
| Documentation | ✅ |
| Installation | ✅ |
| Tests | ✅ |

---

## 🔗 Ressources externes

- **Python**: https://python.org
- **PySide6**: https://wiki.qt.io/PySide6
- **NumPy/SciPy**: https://numpy.org, https://scipy.org
- **Hydrogeology**: Theis (1935), Cooper-Jacob (1946)

---

## 📝 Légende symboles

- ⭐ Important/Start here
- ✅ Complété
- 🔄 En cours
- ⏳ À faire
- 💡 Conseil
- ⚠️  Attention
- 📖 Documentation
- 💻 Code
- 🎓 Pédagogie

---

## À propos

HydroAI = Plateforme pédagogique scientifique pour modélisation hydrogéologique.

**Vision**: Outil sérieux pour apprentissage hydrogeologie avec calculs rigoureux + IA pédagogique guidante.

**Philosophie**: Science first, IA as pedagogy, NOT calculation engine.

---

**Bon travail!** 🎉

Pour commencer → Lire [README.md](README.md) ou [QUICKSTART.md](QUICKSTART.md)

---

*Dernière mise à jour: November 26, 2025*
