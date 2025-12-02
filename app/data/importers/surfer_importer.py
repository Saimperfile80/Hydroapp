"""
Importateur pour grilles Surfer (GRD ASCII et binaire, ASC)
"""

import pandas as pd
import numpy as np
import struct
from typing import Optional, Tuple, Dict, Any
from .base_importer import BaseImporter, ImportResult, ImportMetadata, DataType
import os


class SurferImporter(BaseImporter):
    """Importateur pour grilles Surfer GRD (ASCII et binaire) et ASC"""

    def __init__(self):
        super().__init__()
        self.file_type = "Surfer"

    def validate_file(self, filepath: str) -> bool:
        """Valider le fichier Surfer"""
        if not os.path.exists(filepath):
            self.errors.append(f"Fichier n'existe pas: {filepath}")
            return False
        
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in ['.grd', '.asc', '.txt']:
            self.errors.append(f"Format non supporté: {ext}")
            return False
        
        return True

    def is_binary_grd(self, filepath: str) -> bool:
        """Détermine si le fichier GRD est binaire ou ASCII"""
        try:
            with open(filepath, 'rb') as f:
                header = f.read(4)
            # Grille binaire Surfer commence par "DSAA" ou "DSBB"
            return header.startswith(b'DS')
        except:
            return False

    def import_ascii_grd(self, filepath: str) -> Tuple[np.ndarray, Dict]:
        """Importe une grille Surfer ASCII"""
        meta = {}
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # En-tête Surfer ASCII
            # DSAA
            # nx ny
            # xmin xmax
            # ymin ymax
            # zmin zmax
            
            if len(lines) < 5:
                self.errors.append("Format ASCII GRD invalide")
                return None, meta
            
            # Vérifier la signature
            if not lines[0].strip() == 'DSAA':
                self.warnings.append("Format ASCII attendu mais signature non trouvée")
            
            # Lire la grille
            nx, ny = map(int, lines[1].split())
            xmin, xmax = map(float, lines[2].split())
            ymin, ymax = map(float, lines[3].split())
            zmin, zmax = map(float, lines[4].split())
            
            # Lire les données
            data_str = ' '.join([line.strip() for line in lines[5:]])
            z_values = list(map(float, data_str.split()))
            
            if len(z_values) != nx * ny:
                self.errors.append(f"Nombre de valeurs incorrect: {len(z_values)} != {nx * ny}")
                return None, meta
            
            # Organiser en grille
            grid = np.array(z_values).reshape((ny, nx))
            
            meta = {
                'nx': nx,
                'ny': ny,
                'xmin': xmin,
                'xmax': xmax,
                'ymin': ymin,
                'ymax': ymax,
                'zmin': grid.min(),
                'zmax': grid.max(),
            }
            
            return grid, meta
            
        except Exception as e:
            self.errors.append(f"Erreur lecture ASCII GRD: {str(e)}")
            return None, meta

    def import_binary_grd(self, filepath: str) -> Tuple[np.ndarray, Dict]:
        """Importe une grille Surfer binaire"""
        meta = {}
        try:
            with open(filepath, 'rb') as f:
                # Header
                tag = f.read(4)
                if not tag.startswith(b'DS'):
                    self.errors.append("Format binaire GRD invalide")
                    return None, meta
                
                # Paramètres de la grille
                nx = struct.unpack('<i', f.read(4))[0]
                ny = struct.unpack('<i', f.read(4))[0]
                xmin = struct.unpack('<f', f.read(4))[0]
                xmax = struct.unpack('<f', f.read(4))[0]
                ymin = struct.unpack('<f', f.read(4))[0]
                ymax = struct.unpack('<f', f.read(4))[0]
                zmin = struct.unpack('<f', f.read(4))[0]
                zmax = struct.unpack('<f', f.read(4))[0]
                
                # Lire les données Z
                z_values = []
                for _ in range(nx * ny):
                    z = struct.unpack('<f', f.read(4))[0]
                    z_values.append(z)
                
                grid = np.array(z_values).reshape((ny, nx))
                
                meta = {
                    'nx': nx,
                    'ny': ny,
                    'xmin': xmin,
                    'xmax': xmax,
                    'ymin': ymin,
                    'ymax': ymax,
                    'zmin': grid.min(),
                    'zmax': grid.max(),
                }
                
                return grid, meta
                
        except Exception as e:
            self.errors.append(f"Erreur lecture binaire GRD: {str(e)}")
            return None, meta

    def import_asc(self, filepath: str) -> Tuple[np.ndarray, Dict]:
        """Importe une grille ESRI ASC"""
        meta = {}
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # En-tête ASC
            # ncols
            # nrows
            # xllcorner
            # yllcorner
            # cellsize
            # NODATA_value
            
            header = {}
            data_start = 0
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if line.lower().startswith('ncols'):
                    header['ncols'] = int(line.split()[1])
                elif line.lower().startswith('nrows'):
                    header['nrows'] = int(line.split()[1])
                elif line.lower().startswith('xllcorner'):
                    header['xllcorner'] = float(line.split()[1])
                elif line.lower().startswith('yllcorner'):
                    header['yllcorner'] = float(line.split()[1])
                elif line.lower().startswith('cellsize'):
                    header['cellsize'] = float(line.split()[1])
                elif line.lower().startswith('nodata_value'):
                    header['nodata'] = float(line.split()[1])
                else:
                    # Début des données
                    data_start = i
                    break
            
            # Vérifier en-tête
            required = ['ncols', 'nrows', 'xllcorner', 'yllcorner', 'cellsize']
            if not all(k in header for k in required):
                self.errors.append("En-tête ASC incomplet")
                return None, meta
            
            # Lire les données
            data_str = ' '.join([lines[i].strip() for i in range(data_start, len(lines))])
            z_values = list(map(float, data_str.split()))
            
            ncols = header['ncols']
            nrows = header['nrows']
            if len(z_values) != ncols * nrows:
                self.errors.append(f"Nombre de valeurs incorrect: {len(z_values)} != {ncols * nrows}")
                return None, meta
            
            grid = np.array(z_values).reshape((nrows, ncols))
            
            # Remplacer les valeurs NODATA
            if 'nodata' in header:
                grid[grid == header['nodata']] = np.nan
            
            meta = {
                'nx': ncols,
                'ny': nrows,
                'cellsize': header['cellsize'],
                'xmin': header['xllcorner'],
                'xmax': header['xllcorner'] + ncols * header['cellsize'],
                'ymin': header['yllcorner'],
                'ymax': header['yllcorner'] + nrows * header['cellsize'],
                'zmin': np.nanmin(grid),
                'zmax': np.nanmax(grid),
            }
            
            return grid, meta
            
        except Exception as e:
            self.errors.append(f"Erreur lecture ASC: {str(e)}")
            return None, meta

    def import_data(self, filepath: str, 
                   crs: Optional[str] = None,
                   unit_z: str = "m",
                   **kwargs) -> ImportResult:
        """
        Importe une grille Surfer
        
        Args:
            filepath: Chemin du fichier
            crs: Système de coordonnées
            unit_z: Unité des valeurs Z
        """
        
        result = ImportResult(success=False)
        
        if not self.validate_file(filepath):
            result.errors = self.errors
            return result

        try:
            ext = os.path.splitext(filepath)[1].lower()
            
            if ext == '.grd':
                if self.is_binary_grd(filepath):
                    grid, meta = self.import_binary_grd(filepath)
                else:
                    grid, meta = self.import_ascii_grd(filepath)
            else:  # .asc
                grid, meta = self.import_asc(filepath)
            
            if grid is None:
                result.errors = self.errors
                return result
            
            # Créer un DataFrame avec les coordonnées de grille
            nx, ny = meta['nx'], meta['ny']
            xmin, xmax = meta['xmin'], meta['xmax']
            ymin, ymax = meta['ymin'], meta['ymax']
            
            x_coords = np.linspace(xmin, xmax, nx)
            y_coords = np.linspace(ymin, ymax, ny)
            
            # Créer un tableau de points
            points = []
            for j, y in enumerate(y_coords):
                for i, x in enumerate(x_coords):
                    points.append({
                        'X': x,
                        'Y': y,
                        'Z': grid[j, i]
                    })
            
            df = pd.DataFrame(points)
            
            # Métadonnées
            metadata = ImportMetadata(
                filename=os.path.basename(filepath),
                file_type=self.file_type,
                data_type=DataType.GRID_DATA,
                crs=crs,
                unit_z=unit_z,
                rows=len(df),
                cols=3,
                bounds=(xmin, ymin, xmax, ymax),
            )
            
            # Statistiques
            stats = {
                'grid_nx': nx,
                'grid_ny': ny,
                'x_min': xmin,
                'x_max': xmax,
                'y_min': ymin,
                'y_max': ymax,
                'z_min': meta['zmin'],
                'z_max': meta['zmax'],
                'z_mean': np.nanmean(grid),
                'total_points': len(df),
            }
            
            result.success = True
            result.data = df
            result.grid = grid
            result.metadata = metadata
            result.statistics = stats
            result.warnings.extend(self.warnings)

        except Exception as e:
            result.errors.append(f"Erreur importation grille: {str(e)}")

        return result
