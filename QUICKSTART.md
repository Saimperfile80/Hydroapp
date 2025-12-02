# HydroAI - Guide de Démarrage Rapide

## 🚀 Installation complète (5 min)

### 1. Prérequis
- Python 3.8+
- pip ou conda

### 2. Installation environnement

```bash
# Cloner/télécharger le projet
cd hydroai

# Installer dépendances (une fois)
pip install numpy scipy pandas PySide6 matplotlib

# OU avec conda
conda install numpy scipy pandas -c conda-forge
pip install PySide6 matplotlib
```

### 3. Vérifier installation

```bash
# Test rapide
python -c "import numpy, scipy, pandas, PySide6; print('OK')"

# Test complet
python check_install.py
```

---

## 🎯 Lancer l'application

### Option 1: Script simplifié (RECOMMANDÉ)
```bash
python launcher.py
```

### Option 2: Script principal
```bash
python run.py
```

### Option 3: Direct
```bash
python -m app.main_app
```

---

## 📊 Utilisation rapide

### Onglet 1: Accueil
- Voir présentation HydroAI
- Cliquer "Commencer" pour aller à Essais Pompage

### Onglet 2: Essais Pompage (Theis & Cooper-Jacob)

**Étape 1: Saisir données**
- Tab "Saisie manuelle": Copier/coller temps et rabattements
  ```
  10,0.020
  50,0.045
  100,0.062
  500,0.115
  1000,0.145
  ```
- OU Tab "Importer CSV": Charger fichier CSV

**Étape 2: Paramètres**
- Débit Q (m³/s): 0.001
- Distance r (m): 50
- Méthode: Theis (complet)

**Étape 3: Actions**
- Bouton "✓ Valider": Vérifier paramètres avec IA
- Bouton "▶ Analyser": Exécuter calcul
- Voir résultats (T, S) et graphique

**Étape 4: Exporter**
- "💾 Export CSV": Sauvegarder résultats
- "📄 Export PDF": Générer rapport

### Onglet 3: Perméabilité (Lefranc, Lugeon, Porchet)

1. Sélectionner type test (combobox)
2. Remplir paramètres
3. Cliquer "▶ Analyser"
4. Voir résultats K (m/s, m/day ou Lugeons)

### Onglet 4: Piézométrie

1. "📂 Importer CSV": Charger série temporelle (niveaux d'eau)
2. Cliquer "▶ Analyser"
3. Voir:
   - Statistiques (min, max, moyenne, écart-type)
   - Tendance (pente/jour, type aquifère)
   - Graphiques (série + histogramme)

---

## 📁 Structure fichiers

```
hydroai/
├── core/
│   ├── calculations/          ← Modules scientifiques
│   │   ├── theis.py
│   │   ├── cooper_jacob.py
│   │   ├── lefranc.py
│   │   ├── lugeon.py
│   │   ├── porchet.py
│   │   └── piezo.py
│   ├── ai/                    ← Assistant IA
│   │   ├── anomaly_detection.py
│   │   ├── parameter_recommender.py
│   │   └── validation_engine.py
│   └── solver/, mesh/, io/... (skeleton)
│
├── app/
│   ├── main_app.py            ← Application principale
│   ├── ui/
│   │   └── tabs/              ← Onglets interface
│   │       ├── home_tab.py
│   │       ├── essais_pompage_tab.py
│   │       ├── permeabilite_tab.py
│   │       └── piezo_tab.py
│   └── data/, ui/...
│
├── launcher.py                 ← Lanceur
├── run.py                      ← Point d'entrée
├── check_install.py           ← Vérification
├── README.md                  ← Documentation complète
├── ARCHITECTURE.md            ← Architecture technique
├── GUIDE_ETUDIANT.py         ← Guide avec cas d'étude
└── requirements.txt
```

---

## ✅ Vérification rapide

Tout fonctionne si vous voyez:

```
=== Verification HydroAI ===

✓ OK: Modules calculs (Theis, Cooper-Jacob)
✓ OK: Modules IA
✓ OK: PySide6
✓ OK: NumPy
✓ OK: Calcul Theis - T=1.23e-03 m2/s, S=4.56e-05

Status: READY TO RUN
```

---

## 🔧 Troubleshooting

### "ModuleNotFoundError: numpy"
```bash
pip install numpy scipy pandas
# Si toujours pas: pip install --upgrade numpy
```

### "No module named 'PySide6'"
```bash
pip install PySide6
# Ou: pip install PySide6 --upgrade
```

### Fenêtre Qt ne s'affiche pas
- Vérifier Python 3.8+ : `python --version`
- Vérifier PySide6 : `pip list | grep PySide6`
- Essayer: `python launcher.py` au lieu de `python run.py`

### Erreur lors du calcul Theis
- Vérifier données valides (times > 0, drawdowns > 0)
- Vérifier Q > 0, r > 0
- Voir GUIDE_ETUDIANT.py pour exemples valides

---

## 📚 Documentation

- **README.md**: Vue d'ensemble complète
- **ARCHITECTURE.md**: Architecture technique détaillée
- **GUIDE_ETUDIANT.py**: 9 cas d'étude avec code exact
- **GUIDE_RAPIDE.md**: Ce document

---

## 🎓 Exemples de données test

### Theis simple
```
temps(s) | rabattement(m)
10       | 0.020
50       | 0.045
100      | 0.062
500      | 0.115
1000     | 0.145
```

Résultat attendu:
- T ≈ 1e-3 m²/s
- S ≈ 1e-4

### Piézométrie
```
jour | niveau(m)
1    | 10.50
2    | 10.48
3    | 10.46
...  | ...
30   | 9.80
```

Résultat: Tendance baisse ≈ 0.023 m/jour

---

## 📞 Support

- **Questions sur HydroAI** : Voir ARCHITECTURE.md
- **Questions sur code** : Voir docstrings dans fichiers .py
- **Questions modèles** : Voir GUIDE_ETUDIANT.py
- **Erreurs** : Vérifier check_install.py

---

## 🚀 Prochaines étapes

1. ✅ Application lancée
2. ⏳ Importer vos propres données
3. ⏳ Explorer tous les onglets
4. ⏳ Lire GUIDE_ETUDIANT.py pour cas avancés
5. ⏳ Consulter ARCHITECTURE.md pour extension

---

**Bon travail!** 🎉

Développé avec Python 🐍 + PySide6 + NumPy/SciPy
