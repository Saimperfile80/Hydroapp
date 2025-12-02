"""
Importateurs pour GeoTIFF, Shapefile et GeoJSON
"""

import pandas as pd
import numpy as np
import json
from typing import Optional, Dict, Any
from .base_importer import BaseImporter, ImportResult, ImportMetadata, DataType
import os


class GeoTIFFImporter(BaseImporter):
    """Importateur GeoTIFF pour MNT et grilles raster"""

    def __init__(self):
        super().__init__()
        self.file_type = "GeoTIFF"

    def validate_file(self, filepath: str) -> bool:
        """Valider le fichier GeoTIFF"""
        if not os.path.exists(filepath):
            self.errors.append(f"Fichier n'existe pas: {filepath}")
            return False
        
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in ['.tif', '.tiff']:
            self.errors.append(f"Format non supporté: {ext}")
            return False
        
        return True

    def import_data(self, filepath: str, 
                   crs: Optional[str] = None,
                   unit_z: str = "m",
                   **kwargs) -> ImportResult:
        """
        Importe un GeoTIFF
        
        Args:
            filepath: Chemin du fichier
            crs: Système de coordonnées
            unit_z: Unité des valeurs
        """
        
        result = ImportResult(success=False)
        
        if not self.validate_file(filepath):
            result.errors = self.errors
            return result

        try:
            # Importer rasterio
            try:
                import rasterio
                from rasterio.windows import Window
            except ImportError:
                result.errors.append("Bibliothèque 'rasterio' non installée. Installez avec: pip install rasterio")
                return result
            
            with rasterio.open(filepath) as src:
                # Lire les métadonnées
                profile = src.profile
                bounds = src.bounds
                transform = src.transform
                
                # Lire les données
                data = src.read(1)  # Première bande
                
                # Gérer les valeurs NODATA
                if profile.get('nodata') is not None:
                    data = np.ma.masked_equal(data, profile['nodata'])
                
                # Créer les coordonnées
                height, width = data.shape
                
                # Créer un DataFrame avec points de la grille
                points = []
                for j in range(height):
                    for i in range(width):
                        # Utiliser le transform pour convertir pixel en coordonnées
                        x = transform.c + i * transform.a + 0.5 * transform.a
                        y = transform.f + j * transform.e + 0.5 * transform.e
                        z = float(data[j, i])
                        
                        points.append({
                            'X': x,
                            'Y': y,
                            'Z': z if not np.ma.is_masked(data[j, i]) else np.nan
                        })
                
                df = pd.DataFrame(points)
                
                # CRS
                if crs is None and src.crs is not None:
                    crs = src.crs.to_string()
                
                # Métadonnées
                metadata = ImportMetadata(
                    filename=os.path.basename(filepath),
                    file_type=self.file_type,
                    data_type=DataType.DEM if 'dem' in filepath.lower() else DataType.GRID_DATA,
                    crs=crs,
                    unit_z=unit_z,
                    rows=len(df),
                    cols=3,
                    bounds=(bounds.left, bounds.bottom, bounds.right, bounds.top),
                )
                
                # Statistiques
                valid_data = data[~np.ma.getmaskarray(data)]
                stats = {
                    'raster_width': width,
                    'raster_height': height,
                    'total_points': len(df),
                    'z_min': np.min(valid_data),
                    'z_max': np.max(valid_data),
                    'z_mean': np.mean(valid_data),
                    'x_min': bounds.left,
                    'x_max': bounds.right,
                    'y_min': bounds.bottom,
                    'y_max': bounds.top,
                    'crs': crs,
                }
                
                result.success = True
                result.data = df
                result.grid = data
                result.metadata = metadata
                result.statistics = stats

        except Exception as e:
            result.errors.append(f"Erreur importation GeoTIFF: {str(e)}")

        return result


class ShapefileImporter(BaseImporter):
    """Importateur Shapefile pour vecteurs (points, lignes, polygones)"""

    def __init__(self):
        super().__init__()
        self.file_type = "Shapefile"

    def validate_file(self, filepath: str) -> bool:
        """Valider le fichier Shapefile"""
        if not os.path.exists(filepath):
            self.errors.append(f"Fichier n'existe pas: {filepath}")
            return False
        
        ext = os.path.splitext(filepath)[1].lower()
        if ext != '.shp':
            self.errors.append(f"Format non supporté: {ext}")
            return False
        
        # Vérifier fichiers additionnels
        base = os.path.splitext(filepath)[0]
        for ext in ['.shx', '.dbf']:
            if not os.path.exists(base + ext):
                self.errors.append(f"Fichier manquant: {base}{ext}")
                return False
        
        return True

    def import_data(self, filepath: str, 
                   crs: Optional[str] = None,
                   **kwargs) -> ImportResult:
        """
        Importe un Shapefile
        
        Args:
            filepath: Chemin du fichier .shp
            crs: Système de coordonnées (optionnel)
        """
        
        result = ImportResult(success=False)
        
        if not self.validate_file(filepath):
            result.errors = self.errors
            return result

        try:
            try:
                import geopandas as gpd
            except ImportError:
                result.errors.append("Bibliothèque 'geopandas' non installée. Installez avec: pip install geopandas")
                return result
            
            # Importer le shapefile
            gdf = gpd.read_file(filepath)
            
            # Déterminer le type de géométrie
            geom_types = gdf.geometry.type.unique()
            primary_type = geom_types[0]
            
            if primary_type == 'Point':
                data_type = DataType.POINT_DATA
            elif primary_type in ['LineString', 'MultiLineString']:
                data_type = DataType.VECTOR_DATA
            elif primary_type in ['Polygon', 'MultiPolygon']:
                data_type = DataType.VECTOR_DATA
            else:
                data_type = DataType.VECTOR_DATA
            
            # Extraire les coordonnées
            points = []
            for idx, row in gdf.iterrows():
                geom = row.geometry
                
                if primary_type == 'Point':
                    x, y = geom.x, geom.y
                    points.append({
                        'X': x,
                        'Y': y,
                        'geometry_type': 'Point'
                    })
                elif primary_type in ['LineString', 'MultiLineString']:
                    coords = list(geom.coords) if primary_type == 'LineString' else []
                    for x, y in coords:
                        points.append({
                            'X': x,
                            'Y': y,
                            'geometry_type': 'LineString',
                            'feature_id': idx
                        })
                elif primary_type in ['Polygon', 'MultiPolygon']:
                    if primary_type == 'Polygon':
                        coords = list(geom.exterior.coords)
                    else:
                        coords = []
                    for x, y in coords:
                        points.append({
                            'X': x,
                            'Y': y,
                            'geometry_type': 'Polygon',
                            'feature_id': idx
                        })
            
            df = pd.DataFrame(points)
            
            # CRS
            if crs is None and gdf.crs is not None:
                crs = gdf.crs.to_string()
            
            # Bounds
            bounds = gdf.total_bounds  # (minx, miny, maxx, maxy)
            
            # Métadonnées
            metadata = ImportMetadata(
                filename=os.path.basename(filepath),
                file_type=self.file_type,
                data_type=data_type,
                crs=crs,
                rows=len(df),
                cols=len(df.columns),
                bounds=tuple(bounds),
            )
            
            # Statistiques
            stats = {
                'total_features': len(gdf),
                'total_points': len(df),
                'geometry_types': geom_types.tolist(),
                'x_min': bounds[0],
                'y_min': bounds[1],
                'x_max': bounds[2],
                'y_max': bounds[3],
                'crs': crs,
                'attributes': list(gdf.columns[:-1]),  # Exclure la colonne geometry
            }
            
            result.success = True
            result.data = df
            result.metadata = metadata
            result.statistics = stats

        except Exception as e:
            result.errors.append(f"Erreur importation Shapefile: {str(e)}")

        return result


class GeoJSONImporter(BaseImporter):
    """Importateur GeoJSON"""

    def __init__(self):
        super().__init__()
        self.file_type = "GeoJSON"

    def validate_file(self, filepath: str) -> bool:
        """Valider le fichier GeoJSON"""
        if not os.path.exists(filepath):
            self.errors.append(f"Fichier n'existe pas: {filepath}")
            return False
        
        ext = os.path.splitext(filepath)[1].lower()
        if ext != '.geojson' and ext != '.json':
            self.errors.append(f"Format non supporté: {ext}")
            return False
        
        # Vérifier que c'est du JSON valide
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                json.load(f)
        except:
            self.errors.append("Fichier JSON invalide")
            return False
        
        return True

    def import_data(self, filepath: str, 
                   crs: Optional[str] = None,
                   **kwargs) -> ImportResult:
        """
        Importe un GeoJSON
        
        Args:
            filepath: Chemin du fichier
            crs: Système de coordonnées
        """
        
        result = ImportResult(success=False)
        
        if not self.validate_file(filepath):
            result.errors = self.errors
            return result

        try:
            try:
                import geopandas as gpd
            except ImportError:
                result.errors.append("Bibliothèque 'geopandas' non installée. Installez avec: pip install geopandas")
                return result
            
            # Importer le GeoJSON
            gdf = gpd.read_file(filepath, driver='GeoJSON')
            
            # Déterminer le type de géométrie
            geom_types = gdf.geometry.type.unique()
            primary_type = geom_types[0]
            
            if primary_type == 'Point':
                data_type = DataType.POINT_DATA
            else:
                data_type = DataType.VECTOR_DATA
            
            # Extraire les points
            points = []
            for idx, row in gdf.iterrows():
                geom = row.geometry
                
                if primary_type == 'Point':
                    x, y = geom.x, geom.y
                    props = {k: row[k] for k in gdf.columns if k != 'geometry'}
                    points.append({
                        'X': x,
                        'Y': y,
                        **props
                    })
                elif primary_type == 'LineString':
                    for x, y in geom.coords:
                        points.append({'X': x, 'Y': y})
                elif primary_type == 'Polygon':
                    for x, y in geom.exterior.coords:
                        points.append({'X': x, 'Y': y})
            
            df = pd.DataFrame(points)
            
            # CRS
            if crs is None and gdf.crs is not None:
                crs = gdf.crs.to_string()
            
            # Bounds
            bounds = gdf.total_bounds
            
            # Métadonnées
            metadata = ImportMetadata(
                filename=os.path.basename(filepath),
                file_type=self.file_type,
                data_type=data_type,
                crs=crs,
                rows=len(df),
                cols=len(df.columns),
                bounds=tuple(bounds),
            )
            
            # Statistiques
            stats = {
                'total_features': len(gdf),
                'total_points': len(df),
                'geometry_types': geom_types.tolist(),
                'x_min': bounds[0],
                'y_min': bounds[1],
                'x_max': bounds[2],
                'y_max': bounds[3],
                'crs': crs,
            }
            
            result.success = True
            result.data = df
            result.metadata = metadata
            result.statistics = stats

        except Exception as e:
            result.errors.append(f"Erreur importation GeoJSON: {str(e)}")

        return result
