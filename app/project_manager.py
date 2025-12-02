#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestionnaire de projets HydroAI
Sauvegarde/chargement projets avec historique
"""

import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class ProjectManager:
    """Gestionnaire de projets HydroAI avec SQLite backend"""
    
    def __init__(self, project_dir: str = "./projects"):
        """
        Initialiser gestionnaire projets.
        
        Args:
            project_dir: Répertoire projets (créé s'il n'existe pas)
        """
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.project_dir / "projects.db"
        self._init_database()
    
    def _init_database(self):
        """Initialiser base de données SQLite"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Table projets
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_at TEXT,
                    modified_at TEXT,
                    data_json TEXT
                )
            """)
            
            # Table historique
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY,
                    project_id INTEGER,
                    timestamp TEXT,
                    action TEXT,
                    details TEXT,
                    FOREIGN KEY(project_id) REFERENCES projects(id)
                )
            """)
            
            # Table analyses
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY,
                    project_id INTEGER,
                    method TEXT,
                    timestamp TEXT,
                    parameters JSON,
                    results JSON,
                    FOREIGN KEY(project_id) REFERENCES projects(id)
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("✓ Base de données initialisée")
        
        except Exception as e:
            logger.error(f"Erreur initialisation DB: {e}")
    
    def create_project(self, name: str, description: str = "") -> Tuple[bool, Optional[str]]:
        """
        Créer nouveau projet.
        
        Args:
            name: Nom du projet
            description: Description
            
        Returns:
            (success, error_message)
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO projects (name, description, created_at, modified_at, data_json)
                VALUES (?, ?, ?, ?, ?)
            """, (name, description, now, now, "{}"))
            
            project_id = cursor.lastrowid
            
            # Ajouter à historique
            cursor.execute("""
                INSERT INTO history (project_id, timestamp, action, details)
                VALUES (?, ?, ?, ?)
            """, (project_id, now, "CREATE", f"Project '{name}' created"))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✓ Projet créé: {name}")
            return True, None
        
        except sqlite3.IntegrityError:
            return False, f"Projet '{name}' existe déjà"
        except Exception as e:
            logger.error(f"Erreur création projet: {e}")
            return False, str(e)
    
    def save_analysis(self, project_name: str, method: str, 
                     parameters: Dict, results: Dict) -> Tuple[bool, Optional[str]]:
        """
        Sauvegarder résultats d'analyse.
        
        Args:
            project_name: Nom du projet
            method: Méthode utilisée (Theis, Lefranc, etc.)
            parameters: Dict paramètres
            results: Dict résultats
            
        Returns:
            (success, error_message)
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Récupérer project_id
            cursor.execute("SELECT id FROM projects WHERE name = ?", (project_name,))
            result = cursor.fetchone()
            
            if not result:
                return False, f"Projet '{project_name}' non trouvé"
            
            project_id = result[0]
            now = datetime.now().isoformat()
            
            # Convertir arrays numpy en listes pour JSON
            params_json = self._serialize_dict(parameters)
            results_json = self._serialize_dict(results)
            
            cursor.execute("""
                INSERT INTO analyses (project_id, method, timestamp, parameters, results)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, method, now, params_json, results_json))
            
            # Mettre à jour modified_at
            cursor.execute("""
                UPDATE projects SET modified_at = ? WHERE id = ?
            """, (now, project_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✓ Analyse '{method}' sauvegardée dans '{project_name}'")
            return True, None
        
        except Exception as e:
            logger.error(f"Erreur sauvegarde analyse: {e}")
            return False, str(e)
    
    def load_project(self, project_name: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Charger projet et toutes ses analyses.
        
        Args:
            project_name: Nom du projet
            
        Returns:
            (success, project_data, error_message)
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Récupérer projet
            cursor.execute("""
                SELECT id, name, description, created_at, modified_at, data_json
                FROM projects WHERE name = ?
            """, (project_name,))
            
            result = cursor.fetchone()
            if not result:
                return False, None, f"Projet '{project_name}' non trouvé"
            
            project_id, name, desc, created, modified, data_json = result
            
            # Récupérer analyses
            cursor.execute("""
                SELECT method, timestamp, parameters, results FROM analyses
                WHERE project_id = ? ORDER BY timestamp DESC
            """, (project_id,))
            
            analyses = []
            for row in cursor.fetchall():
                method, timestamp, params, results = row
                analyses.append({
                    'method': method,
                    'timestamp': timestamp,
                    'parameters': json.loads(params),
                    'results': json.loads(results)
                })
            
            # Récupérer historique
            cursor.execute("""
                SELECT timestamp, action, details FROM history
                WHERE project_id = ? ORDER BY timestamp DESC
            """, (project_id,))
            
            history = [{'timestamp': t, 'action': a, 'details': d} 
                      for t, a, d in cursor.fetchall()]
            
            conn.close()
            
            project_data = {
                'id': project_id,
                'name': name,
                'description': desc,
                'created_at': created,
                'modified_at': modified,
                'analyses': analyses,
                'history': history
            }
            
            logger.info(f"✓ Projet chargé: {name} ({len(analyses)} analyses)")
            return True, project_data, None
        
        except Exception as e:
            logger.error(f"Erreur chargement projet: {e}")
            return False, None, str(e)
    
    def list_projects(self) -> Tuple[bool, Optional[List], Optional[str]]:
        """
        Lister tous les projets.
        
        Returns:
            (success, projects_list, error_message)
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, description, created_at, modified_at
                FROM projects ORDER BY modified_at DESC
            """)
            
            projects = []
            for row in cursor.fetchall():
                proj_id, name, desc, created, modified = row
                projects.append({
                    'id': proj_id,
                    'name': name,
                    'description': desc,
                    'created_at': created,
                    'modified_at': modified
                })
            
            conn.close()
            logger.info(f"✓ {len(projects)} projets trouvés")
            return True, projects, None
        
        except Exception as e:
            logger.error(f"Erreur listing: {e}")
            return False, None, str(e)
    
    def delete_project(self, project_name: str) -> Tuple[bool, Optional[str]]:
        """
        Supprimer un projet et ses données.
        
        Args:
            project_name: Nom du projet
            
        Returns:
            (success, error_message)
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Récupérer ID
            cursor.execute("SELECT id FROM projects WHERE name = ?", (project_name,))
            result = cursor.fetchone()
            
            if not result:
                return False, f"Projet '{project_name}' non trouvé"
            
            project_id = result[0]
            
            # Supprimer analyses et historique
            cursor.execute("DELETE FROM analyses WHERE project_id = ?", (project_id,))
            cursor.execute("DELETE FROM history WHERE project_id = ?", (project_id,))
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✓ Projet supprimé: {project_name}")
            return True, None
        
        except Exception as e:
            logger.error(f"Erreur suppression: {e}")
            return False, str(e)
    
    @staticmethod
    def _serialize_dict(d: Dict) -> str:
        """Sérialiser dict avec support arrays numpy"""
        def serialize(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [serialize(item) for item in obj]
            return obj
        
        return json.dumps(serialize(d))
    
    @staticmethod
    def export_project(project_data: Dict, filepath: str) -> Tuple[bool, Optional[str]]:
        """
        Exporter projet complet en JSON.
        
        Args:
            project_data: Données du projet
            filepath: Chemin destination
            
        Returns:
            (success, error_message)
        """
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(project_data, f, indent=2)
            
            logger.info(f"✓ Projet exporté: {filepath}")
            return True, None
        
        except Exception as e:
            logger.error(f"Erreur export: {e}")
            return False, str(e)
