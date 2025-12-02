"""
Module base pour tous les importateurs de données.
Définit l'interface standard pour l'import de données hydrogéologiques.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
from enum import Enum


class DataType(Enum):
    """Types de données hydrogéologiques"""
    POINT_DATA = "point_data"              # XYZ, charges, concentrations
    GRID_DATA = "grid_data"                # Grilles Surfer, GeoTIFF
    VECTOR_DATA = "vector_data"            # SHP, GeoJSON (rivières, limites)
    TABULAR_DATA = "tabular_data"          # CSV, Excel (séries temporelles, puits)
    DEM = "dem"                            # Modèle numérique de terrain


@dataclass
class ImportMetadata:
    """Métadonnées d'un fichier importé"""
    filename: str
    file_type: str
    data_type: DataType
    crs: Optional[str] = None                    # Système de coordonnées (EPSG:xxxx)
    unit_x: str = "m"                           # Unité X (m, km, ft)
    unit_y: str = "m"                           # Unité Y
    unit_z: str = "m"                           # Unité Z (altitude/profondeur)
    unit_values: Optional[str] = None           # Unité des valeurs
    rows: int = 0                               # Nombre de lignes
    cols: int = 0                               # Nombre de colonnes (si grille)
    bounds: Optional[Tuple[float, float, float, float]] = None  # (xmin, ymin, xmax, ymax)
    timestamp: Optional[str] = None             # Date/heure import
    encoding: str = "utf-8"                     # Encodage fichier
    separator: Optional[str] = None             # Séparateur (CSV)
    missing_value: Optional[str] = "-9999"      # Valeur manquante
    skip_rows: int = 0                          # Lignes à ignorer (en-têtes)
    notes: str = ""                             # Notes additionnelles


@dataclass
class ImportResult:
    """Résultat d'une importation"""
    success: bool
    data: Optional[pd.DataFrame] = None         # DataFrame importé
    grid: Optional[np.ndarray] = None           # Grille (si applicable)
    metadata: Optional[ImportMetadata] = None
    warnings: List[str] = None                  # Avertissements (doublons, valeurs manquantes)
    errors: List[str] = None                    # Erreurs lors de l'import
    statistics: Optional[Dict[str, Any]] = None # Stats (min, max, moyenne, etc.)

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []
        if self.statistics is None:
            self.statistics = {}


class BaseImporter(ABC):
    """Classe de base pour tous les importateurs"""

    def __init__(self):
        self.metadata = None
        self.data = None
        self.grid = None
        self.warnings = []
        self.errors = []

    @abstractmethod
    def validate_file(self, filepath: str) -> bool:
        """Valider que le fichier est au bon format"""
        pass

    @abstractmethod
    def import_data(self, filepath: str, **kwargs) -> ImportResult:
        """Importer les données du fichier"""
        pass

    def detect_separator(self, filepath: str, encoding: str = 'utf-8') -> str:
        """Détecter automatiquement le séparateur CSV"""
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                first_line = f.readline()
            
            separators = [',', ';', '\t', ' ', '|']
            max_count = 0
            best_sep = ','
            
            for sep in separators:
                count = first_line.count(sep)
                if count > max_count:
                    max_count = count
                    best_sep = sep
            
            return best_sep
        except Exception as e:
            self.errors.append(f"Erreur détection séparateur: {str(e)}")
            return ','

    def detect_encoding(self, filepath: str) -> str:
        """Détecter l'encodage du fichier"""
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        for enc in encodings:
            try:
                with open(filepath, 'r', encoding=enc) as f:
                    f.read(1000)
                return enc
            except:
                continue
        return 'utf-8'

    def detect_missing_values(self, df: pd.DataFrame) -> Dict[str, int]:
        """Détecte les valeurs manquantes"""
        missing = {}
        for col in df.columns:
            count = df[col].isna().sum()
            if count > 0:
                missing[col] = count
        return missing

    def detect_duplicates(self, df: pd.DataFrame, 
                         x_col: str = 'X', 
                         y_col: str = 'Y') -> Tuple[int, pd.DataFrame]:
        """Détecte les doublons spatiaux"""
        if x_col not in df.columns or y_col not in df.columns:
            return 0, df
        
        before = len(df)
        df_dedup = df.drop_duplicates(subset=[x_col, y_col])
        after = len(df_dedup)
        
        return before - after, df_dedup

    def validate_numeric(self, df: pd.DataFrame, columns: List[str]) -> List[str]:
        """Valide que les colonnes sont numériques"""
        errors = []
        for col in columns:
            if col in df.columns:
                try:
                    pd.to_numeric(df[col], errors='coerce')
                except:
                    errors.append(f"Colonne '{col}' n'est pas numérique")
        return errors

    def calculate_statistics(self, df: pd.DataFrame, 
                            numeric_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Calcule les statistiques des données importées"""
        stats = {
            'total_rows': len(df),
            'total_cols': len(df.columns),
            'columns': list(df.columns),
        }
        
        if numeric_columns is None:
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        for col in numeric_columns:
            if col in df.columns:
                stats[f'{col}_min'] = df[col].min()
                stats[f'{col}_max'] = df[col].max()
                stats[f'{col}_mean'] = df[col].mean()
                stats[f'{col}_std'] = df[col].std()
                stats[f'{col}_missing'] = df[col].isna().sum()
        
        return stats

    def get_bounds(self, df: pd.DataFrame, 
                   x_col: str = 'X', 
                   y_col: str = 'Y') -> Optional[Tuple[float, float, float, float]]:
        """Calcule les limites spatiales des données"""
        if x_col not in df.columns or y_col not in df.columns:
            return None
        
        try:
            xmin = df[x_col].min()
            xmax = df[x_col].max()
            ymin = df[y_col].min()
            ymax = df[y_col].max()
            return (xmin, ymin, xmax, ymax)
        except:
            return None
