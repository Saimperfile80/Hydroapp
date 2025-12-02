"""
Importateur pour fichiers CSV et TXT
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from .base_importer import BaseImporter, ImportResult, ImportMetadata, DataType
import os


class CSVTXTImporter(BaseImporter):
    """Importateur CSV/TXT avec détection automatique des paramètres"""

    def __init__(self):
        super().__init__()
        self.file_type = "CSV/TXT"

    def validate_file(self, filepath: str) -> bool:
        """Valider le fichier CSV/TXT"""
        if not os.path.exists(filepath):
            self.errors.append(f"Fichier n'existe pas: {filepath}")
            return False
        
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in ['.csv', '.txt', '.dat', '.xyz']:
            self.errors.append(f"Format non supporté: {ext}")
            return False
        
        return True

    def auto_detect_format(self, filepath: str) -> Dict[str, Any]:
        """Détecte automatiquement le format du fichier"""
        config = {
            'separator': ',',
            'encoding': 'utf-8',
            'skip_rows': 0,
            'decimal': '.',
            'has_header': True,
        }

        # Détection encodage
        config['encoding'] = self.detect_encoding(filepath)

        # Détection séparateur
        config['separator'] = self.detect_separator(filepath, config['encoding'])

        # Détection en-têtes
        try:
            with open(filepath, 'r', encoding=config['encoding']) as f:
                first_line = f.readline().strip()
                # Si première ligne contient du texte et pas seulement des nombres, c'est un en-tête
                parts = first_line.split(config['separator'])
                try:
                    float(parts[0])
                    config['has_header'] = False
                except:
                    config['has_header'] = True
        except:
            pass

        return config

    def import_data(self, filepath: str, 
                   x_col: str = 'X', 
                   y_col: str = 'Y',
                   z_col: Optional[str] = 'Z',
                   crs: Optional[str] = None,
                   auto_detect: bool = True,
                   **kwargs) -> ImportResult:
        """
        Importe les données CSV/TXT
        
        Args:
            filepath: Chemin du fichier
            x_col: Nom colonne X
            y_col: Nom colonne Y
            z_col: Nom colonne Z (optionnel)
            crs: Système de coordonnées (EPSG:xxxx)
            auto_detect: Détection automatique des paramètres
            **kwargs: Paramètres additionnels (separator, encoding, etc.)
        """
        
        result = ImportResult(success=False)
        
        # Valider le fichier
        if not self.validate_file(filepath):
            result.errors = self.errors
            return result

        try:
            # Détection automatique
            if auto_detect:
                config = self.auto_detect_format(filepath)
                config.update(kwargs)
            else:
                config = kwargs

            separator = config.get('separator', ',')
            encoding = config.get('encoding', 'utf-8')
            skip_rows = config.get('skip_rows', 0)
            header = 0 if config.get('has_header', True) else None

            # Importation
            df = pd.read_csv(
                filepath,
                sep=separator,
                encoding=encoding,
                skiprows=skip_rows,
                header=header,
                decimal=config.get('decimal', '.'),
                na_values=config.get('missing_value', ['-9999', 'NA', 'N/A', '']),
            )

            # Renommer les colonnes si nécessaire (pas d'en-tête)
            if not config.get('has_header', True):
                df.columns = [f'Col_{i}' for i in range(len(df.columns))]

            # Valider les colonnes requises
            missing_cols = []
            for col in [x_col, y_col]:
                if col not in df.columns:
                    missing_cols.append(col)
            
            if missing_cols:
                result.errors.append(f"Colonnes manquantes: {missing_cols}")
                return result

            # Détection et suppression des doublons
            n_duplicates, df = self.detect_duplicates(df, x_col, y_col)
            if n_duplicates > 0:
                result.warnings.append(f"Doublons détectés et supprimés: {n_duplicates}")

            # Détection valeurs manquantes
            missing = self.detect_missing_values(df)
            if missing:
                msg = ", ".join([f"{col}: {count}" for col, count in missing.items()])
                result.warnings.append(f"Valeurs manquantes détectées: {msg}")

            # Validation numériques
            numeric_cols = [x_col, y_col]
            if z_col and z_col in df.columns:
                numeric_cols.append(z_col)
            
            errors = self.validate_numeric(df, numeric_cols)
            if errors:
                result.errors.extend(errors)
                return result

            # Conversion numériques
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Calcul des limites
            bounds = self.get_bounds(df, x_col, y_col)

            # Statistiques
            stats = self.calculate_statistics(df, numeric_cols)

            # Métadonnées
            metadata = ImportMetadata(
                filename=os.path.basename(filepath),
                file_type=self.file_type,
                data_type=DataType.POINT_DATA,
                crs=crs,
                rows=len(df),
                cols=len(df.columns),
                bounds=bounds,
                encoding=encoding,
                separator=separator,
                missing_value=config.get('missing_value', '-9999'),
                skip_rows=skip_rows,
            )

            result.success = True
            result.data = df
            result.metadata = metadata
            result.statistics = stats
            result.warnings.extend(self.warnings)

        except Exception as e:
            result.errors.append(f"Erreur importation: {str(e)}")
            result.success = False

        return result


class ExcelImporter(BaseImporter):
    """Importateur Excel avec gestion multi-feuilles"""

    def __init__(self):
        super().__init__()
        self.file_type = "Excel"

    def validate_file(self, filepath: str) -> bool:
        """Valider le fichier Excel"""
        if not os.path.exists(filepath):
            self.errors.append(f"Fichier n'existe pas: {filepath}")
            return False
        
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in ['.xlsx', '.xls']:
            self.errors.append(f"Format non supporté: {ext}")
            return False
        
        return True

    def get_sheets(self, filepath: str) -> List[str]:
        """Récupère la liste des feuilles Excel"""
        try:
            xls = pd.ExcelFile(filepath)
            return xls.sheet_names
        except Exception as e:
            self.errors.append(f"Erreur lecture feuilles: {str(e)}")
            return []

    def import_data(self, filepath: str, 
                   sheet_name: str = 0,
                   x_col: str = 'X',
                   y_col: str = 'Y',
                   z_col: Optional[str] = 'Z',
                   crs: Optional[str] = None,
                   **kwargs) -> ImportResult:
        """
        Importe les données Excel
        
        Args:
            filepath: Chemin du fichier
            sheet_name: Nom ou index de la feuille
            x_col: Nom colonne X
            y_col: Nom colonne Y
            z_col: Nom colonne Z
            crs: Système de coordonnées
        """
        
        result = ImportResult(success=False)
        
        if not self.validate_file(filepath):
            result.errors = self.errors
            return result

        try:
            # Importation
            df = pd.read_excel(
                filepath,
                sheet_name=sheet_name,
                **kwargs
            )

            # Valider les colonnes requises
            missing_cols = []
            for col in [x_col, y_col]:
                if col not in df.columns:
                    missing_cols.append(col)
            
            if missing_cols:
                result.errors.append(f"Colonnes manquantes: {missing_cols}")
                return result

            # Détection et suppression des doublons
            n_duplicates, df = self.detect_duplicates(df, x_col, y_col)
            if n_duplicates > 0:
                result.warnings.append(f"Doublons supprimés: {n_duplicates}")

            # Détection valeurs manquantes
            missing = self.detect_missing_values(df)
            if missing:
                msg = ", ".join([f"{col}: {count}" for col, count in missing.items()])
                result.warnings.append(f"Valeurs manquantes: {msg}")

            # Validation numériques
            numeric_cols = [x_col, y_col]
            if z_col and z_col in df.columns:
                numeric_cols.append(z_col)
            
            errors = self.validate_numeric(df, numeric_cols)
            if errors:
                result.errors.extend(errors)
                return result

            # Conversion numériques
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Calcul des limites
            bounds = self.get_bounds(df, x_col, y_col)

            # Statistiques
            stats = self.calculate_statistics(df, numeric_cols)

            # Métadonnées
            metadata = ImportMetadata(
                filename=os.path.basename(filepath),
                file_type=self.file_type,
                data_type=DataType.POINT_DATA,
                crs=crs,
                rows=len(df),
                cols=len(df.columns),
                bounds=bounds,
            )

            result.success = True
            result.data = df
            result.metadata = metadata
            result.statistics = stats

        except Exception as e:
            result.errors.append(f"Erreur importation: {str(e)}")

        return result
