"""
Gestionnaire centralisé d'importation avec détection automatique de format
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path

from .base_importer import BaseImporter, ImportResult, DataType
from .csv_excel_importer import CSVTXTImporter, ExcelImporter
from .surfer_importer import SurferImporter
from .geospatial_importer import GeoTIFFImporter, ShapefileImporter, GeoJSONImporter


class ImportManager:
    """Gestionnaire d'importation avec détection automatique du format"""

    def __init__(self):
        self.importers = {
            '.csv': CSVTXTImporter(),
            '.txt': CSVTXTImporter(),
            '.dat': CSVTXTImporter(),
            '.xyz': CSVTXTImporter(),
            '.xlsx': ExcelImporter(),
            '.xls': ExcelImporter(),
            '.grd': SurferImporter(),
            '.asc': SurferImporter(),
            '.tif': GeoTIFFImporter(),
            '.tiff': GeoTIFFImporter(),
            '.shp': ShapefileImporter(),
            '.geojson': GeoJSONImporter(),
            '.json': GeoJSONImporter(),
        }
        
        self.import_history = []
        self.last_import = None

    def get_importer(self, filepath: str) -> Optional[BaseImporter]:
        """Retourne l'importateur approprié basé sur l'extension du fichier"""
        ext = Path(filepath).suffix.lower()
        return self.importers.get(ext)

    def get_supported_formats(self) -> Dict[str, str]:
        """Retourne la liste des formats supportés"""
        return {
            '.csv': 'Comma Separated Values',
            '.txt': 'Text (XYZ)',
            '.dat': 'Data (XYZ)',
            '.xyz': 'XYZ Points',
            '.xlsx': 'Excel 2007+',
            '.xls': 'Excel 97-2003',
            '.grd': 'Surfer Grid (ASCII/Binary)',
            '.asc': 'ESRI ASCII Grid',
            '.tif': 'GeoTIFF',
            '.tiff': 'GeoTIFF',
            '.shp': 'Shapefile (Vector)',
            '.geojson': 'GeoJSON',
            '.json': 'JSON (GeoJSON)',
        }

    def import_file(self, filepath: str, 
                   crs: Optional[str] = None,
                   **kwargs) -> ImportResult:
        """
        Importe un fichier avec détection automatique du format
        
        Args:
            filepath: Chemin du fichier
            crs: Système de coordonnées (optionnel)
            **kwargs: Paramètres additionnels (x_col, y_col, sheet_name, etc.)
        
        Returns:
            ImportResult avec données et métadonnées
        """
        
        result = ImportResult(success=False)
        
        # Vérifier l'existence du fichier
        if not os.path.exists(filepath):
            result.errors.append(f"Fichier n'existe pas: {filepath}")
            return result
        
        # Obtenir l'importateur
        importer = self.get_importer(filepath)
        if importer is None:
            ext = Path(filepath).suffix.lower()
            result.errors.append(f"Format non supporté: {ext}")
            return result
        
        # Importer les données
        try:
            # Ajouter CRS s'il est fourni
            if crs:
                kwargs['crs'] = crs
            
            result = importer.import_data(filepath, **kwargs)
            
            if result.success:
                # Enregistrer dans l'historique
                self.import_history.append({
                    'filepath': filepath,
                    'format': importer.file_type,
                    'rows': result.metadata.rows if result.metadata else 0,
                    'success': True,
                })
                self.last_import = result
            else:
                # Enregistrer l'erreur
                self.import_history.append({
                    'filepath': filepath,
                    'format': importer.file_type,
                    'success': False,
                    'errors': result.errors,
                })
            
            return result
            
        except Exception as e:
            result.errors.append(f"Erreur lors de l'importation: {str(e)}")
            return result

    def batch_import(self, filepaths: list, 
                    crs: Optional[str] = None,
                    **kwargs) -> list:
        """
        Importe plusieurs fichiers
        
        Args:
            filepaths: Liste des chemins de fichiers
            crs: Système de coordonnées commun
            **kwargs: Paramètres additionnels
        
        Returns:
            Liste des ImportResult
        """
        
        results = []
        for filepath in filepaths:
            result = self.import_file(filepath, crs=crs, **kwargs)
            results.append(result)
        
        return results

    def get_import_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques d'importation"""
        total = len(self.import_history)
        successful = sum(1 for h in self.import_history if h.get('success', False))
        failed = total - successful
        
        formats_used = {}
        for h in self.import_history:
            fmt = h.get('format', 'Unknown')
            formats_used[fmt] = formats_used.get(fmt, 0) + 1
        
        return {
            'total_imports': total,
            'successful': successful,
            'failed': failed,
            'formats_used': formats_used,
            'last_import': self.last_import.metadata.filename if self.last_import else None,
        }

    def get_import_history(self) -> list:
        """Retourne l'historique des importations"""
        return self.import_history

    def clear_history(self):
        """Efface l'historique"""
        self.import_history = []
        self.last_import = None


# Singleton global
_import_manager = None

def get_import_manager() -> ImportManager:
    """Retourne une instance unique du gestionnaire d'importation"""
    global _import_manager
    if _import_manager is None:
        _import_manager = ImportManager()
    return _import_manager
