# Module d'Importation HydroAI

## Vue d'ensemble

Le module d'importation permet d'importer des données hydrogéologiques depuis plusieurs formats de fichiers avec détection automatique du format et des paramètres.

## Formats supportés

### Données tabulaires
- **CSV** (Comma Separated Values)
- **TXT** (Text files with XYZ data)
- **XLSX/XLS** (Excel)

### Grilles et MNT
- **GRD** (Surfer grids - ASCII et binaire)
- **ASC** (ESRI ASCII grids)
- **GeoTIFF** (Raster géoréférencés)

### Données vectorielles
- **SHP** (Shapefile)
- **GeoJSON** (JSON géospatial)

## Utilisation basique

### Importation simple

```python
from data.importers import get_import_manager

manager = get_import_manager()

# Importer automatiquement en détectant le format
result = manager.import_file('data/wells.csv')

if result.success:
    df = result.data  # DataFrame pandas
    metadata = result.metadata
    stats = result.statistics
else:
    print("Erreurs:", result.errors)
```

### Importation avec paramètres

```python
# Spécifier les colonnes
result = manager.import_file(
    'data/points.csv',
    x_col='Longitude',
    y_col='Latitude',
    z_col='Altitude',
    crs='EPSG:4326'
)

# Paramètres Excel
result = manager.import_file(
    'data/aquifer.xlsx',
    sheet_name='Piezometry',
    x_col='X',
    y_col='Y'
)
```

## Architecture

### Classes principales

#### `BaseImporter`
Classe abstraite de base pour tous les importateurs.

**Méthodes:**
- `validate_file(filepath)` - Valide le format du fichier
- `import_data(filepath, **kwargs)` - Importe les données
- `detect_separator()` - Détecte le séparateur CSV
- `detect_encoding()` - Détecte l'encodage
- `detect_duplicates()` - Détecte les doublons spatiaux
- `validate_numeric()` - Valide les colonnes numériques

#### `CSVTXTImporter`
Importe fichiers CSV/TXT avec détection automatique.

**Paramètres:**
- `x_col` - Colonne X (par défaut: 'X')
- `y_col` - Colonne Y (par défaut: 'Y')
- `z_col` - Colonne Z (optionnel)
- `separator` - Séparateur CSV (auto-détecté)
- `encoding` - Encodage du fichier (auto-détecté)

#### `ExcelImporter`
Importe fichiers Excel avec support multi-feuilles.

**Paramètres:**
- `sheet_name` - Nom ou index de la feuille
- `x_col`, `y_col`, `z_col` - Colonnes de coordonnées

#### `SurferImporter`
Importe grilles Surfer (GRD ASCII/binaire, ASC).

#### `GeoTIFFImporter`
Importe rasters géoréférencés (GeoTIFF).

#### `ShapefileImporter`
Importe shapefiles (points, lignes, polygones).

#### `GeoJSONImporter`
Importe fichiers GeoJSON.

### Structures de données

#### `ImportMetadata`
Contient les métadonnées d'un fichier importé:
- `filename` - Nom du fichier
- `file_type` - Type de format
- `data_type` - Type de données (POINT_DATA, GRID_DATA, etc.)
- `crs` - Système de coordonnées (EPSG:xxxx)
- `rows`, `cols` - Dimensions
- `bounds` - Limites spatiales (xmin, ymin, xmax, ymax)
- `unit_x`, `unit_y`, `unit_z` - Unités
- `encoding` - Encodage du fichier
- `missing_value` - Valeur manquante

#### `ImportResult`
Résultat d'une importation:
- `success` - Booléen succès/échec
- `data` - DataFrame pandas des données
- `grid` - Array numpy (si grille)
- `metadata` - Métadonnées
- `warnings` - Liste d'avertissements
- `errors` - Liste d'erreurs
- `statistics` - Statistiques des données

#### `DataType`
Énumération des types de données:
- `POINT_DATA` - Données ponctuelles
- `GRID_DATA` - Grilles régulières
- `VECTOR_DATA` - Données vectorielles
- `TABULAR_DATA` - Données tabulaires
- `DEM` - Modèle numérique de terrain

### `ImportManager`
Gestionnaire centralisé pour toutes les importations.

**Méthodes principales:**
```python
# Importer un fichier
result = manager.import_file(filepath, **kwargs)

# Importer plusieurs fichiers
results = manager.batch_import([filepath1, filepath2])

# Obtenir formats supportés
formats = manager.get_supported_formats()

# Historique
history = manager.get_import_history()
stats = manager.get_import_statistics()
```

## Détections automatiques

### Séparateur CSV
Détecte automatiquement: `,`, `;`, `\t`, ` `, `|`

### Encodage
Essaie dans l'ordre: UTF-8, Latin-1, ISO-8859-1, CP1252

### En-têtes
Détecte automatiquement si première ligne est un en-tête

### Doublons
Détecte et supprime les doublons spatiaux basés sur X,Y

### Valeurs manquantes
Reconnaît: -9999, NA, N/A, chaînes vides

## Validation et nettoyage

### Contrôles effectués
- ✓ Existence du fichier
- ✓ Format valide
- ✓ Colonnes requises présentes
- ✓ Données numériques valides
- ✓ Doublons spatiaux
- ✓ Valeurs manquantes
- ✓ Limites spatiales cohérentes

### Avertissements générés
- Doublons détectés
- Valeurs manquantes
- Colonnes numériques non valides
- Limites inattendues

## Statistiques

Chaque importation calcule automatiquement:
- Min, max, moyenne, écart-type
- Nombre de valeurs manquantes
- Limites spatiales (xmin, ymin, xmax, ymax)
- Nombre total de points
- Pour grilles: dimensions, taille de cellule

## Exemples d'utilisation

### Importer des données de puits

```python
from data.importers import get_import_manager

manager = get_import_manager()

# Importer données de puits
result = manager.import_file(
    'wells.csv',
    x_col='Easting',
    y_col='Northing',
    z_col='Elevation',
    crs='EPSG:32632'  # Zone 32N
)

if result.success:
    print(f"Importés {result.metadata.rows} puits")
    print(f"Limites: {result.metadata.bounds}")
    print(f"Charge min: {result.statistics['Charge_m_min']}")
```

### Importer un MNT

```python
# Importer un MNT GeoTIFF
result = manager.import_file(
    'dem.tif',
    unit_z='m'
)

if result.success:
    print(f"MNT {result.statistics['raster_width']} x {result.statistics['raster_height']}")
    print(f"Altitude: {result.statistics['z_min']:.1f} - {result.statistics['z_max']:.1f} m")
```

### Importer des limites de bassin

```python
# Importer un shapefile de bassin versant
result = manager.import_file(
    'watershed.shp',
    crs='EPSG:32632'
)

if result.success:
    print(f"Bassin versant importé")
    print(f"Surface: ~{(result.metadata.bounds[2] - result.metadata.bounds[0]) * (result.metadata.bounds[3] - result.metadata.bounds[1]) / 1e6:.1f} km²")
```

## Gestion des erreurs

```python
result = manager.import_file('data.csv')

if not result.success:
    # Afficher les erreurs
    for error in result.errors:
        print(f"ERREUR: {error}")
    
    # Afficher les avertissements
    for warning in result.warnings:
        print(f"AVERTISSEMENT: {warning}")
```

## Performance

Capacités testées:
- CSV/Excel: jusqu'à 1M points
- Grilles: jusqu'à 10000 x 10000 pixels
- Shapefiles: jusqu'à 100k géométries

## Limitations actuelles

- GRD binaire: format Surfer standard uniquement
- GeoTIFF: bande simple (première bande lue)
- Shapefile: pas de support pour les attributs complexes

## Installation des dépendances

```bash
# Dépendances minimales (CSV, Excel)
pip install pandas openpyxl

# Avec support géospatial
pip install geopandas rasterio shapely fiona

# Installation complète (recommandée)
pip install -r requirements.txt
```

## Développement future

- [ ] Support OGR pour plus de formats
- [ ] Compression GZIP pour grilles
- [ ] Multi-bandes GeoTIFF
- [ ] Streaming pour gros fichiers
- [ ] Reprojection automatique
- [ ] Visualisation en temps réel
