#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'import/export de données
Gère CSV, JSON, et fichiers projets
"""

import csv
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class DataIOManager:
    """Gestionnaire I/O pour données hydrogeologiques"""
    
    # Extensions supportées
    SUPPORTED_FORMATS = {
        '.csv': 'CSV (comma-separated)',
        '.json': 'JSON (structured)',
        '.txt': 'TXT (tab-separated)'
    }
    
    @staticmethod
    def load_csv(filepath: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Charger données depuis CSV.
        
        Format attendu:
        - Headers: time, drawdown (ou head, discharge, etc.)
        - Numeric values
        
        Args:
            filepath: Chemin au fichier CSV
            
        Returns:
            (success, data_dict, error_message)
        """
        try:
            filepath = Path(filepath)
            if not filepath.exists():
                return False, None, f"Fichier non trouvé: {filepath}"
            
            data = {
                'times': [],
                'values': [],
                'headers': [],
                'metadata': {}
            }
            
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                if not reader.fieldnames:
                    return False, None, "Fichier CSV vide"
                
                data['headers'] = list(reader.fieldnames)
                
                for i, row in enumerate(reader):
                    try:
                        # Chercher colonne temps
                        if 'time' in row:
                            t = float(row['time'])
                        elif 'temps' in row:
                            t = float(row['temps'])
                        elif 'second' in row or 's' in row:
                            t = float(row['second'] or row['s'])
                        else:
                            t = float(i)  # Index par défaut
                        
                        # Chercher colonne valeur
                        if 'drawdown' in row:
                            v = float(row['drawdown'])
                        elif 'head' in row:
                            v = float(row['head'])
                        elif 'charge' in row:
                            v = float(row['charge'])
                        elif 'discharge' in row:
                            v = float(row['discharge'])
                        else:
                            # Prendre première colonne numérique
                            for key, val in row.items():
                                if key.lower() not in ['time', 'temps']:
                                    try:
                                        v = float(val)
                                        break
                                    except:
                                        pass
                            else:
                                continue
                        
                        data['times'].append(t)
                        data['values'].append(v)
                    
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Ligne {i+2} invalide: {e}")
                        continue
                
                if not data['times']:
                    return False, None, "Aucune donnée numérique trouvée"
                
                data['times'] = np.array(data['times'])
                data['values'] = np.array(data['values'])
                data['metadata'] = {
                    'source': str(filepath),
                    'num_points': len(data['times']),
                    'loaded_at': datetime.now().isoformat()
                }
                
                logger.info(f"✓ CSV chargé: {len(data['times'])} points")
                return True, data, None
        
        except Exception as e:
            logger.error(f"Erreur CSV: {e}")
            return False, None, str(e)
    
    @staticmethod
    def save_csv(filepath: str, times: np.ndarray, values: np.ndarray,
                 headers: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
        """
        Sauvegarder données en CSV.
        
        Args:
            filepath: Chemin destination
            times: Array temps
            values: Array valeurs
            headers: Headers personnalisés
            
        Returns:
            (success, error_message)
        """
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            if headers is None:
                headers = ['time', 'value']
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                
                for t, v in zip(times, values):
                    writer.writerow([t, v])
            
            logger.info(f"✓ CSV sauvegardé: {filepath}")
            return True, None
        
        except Exception as e:
            logger.error(f"Erreur sauvegarde CSV: {e}")
            return False, str(e)
    
    @staticmethod
    def load_json(filepath: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """Charger données depuis JSON."""
        try:
            filepath = Path(filepath)
            if not filepath.exists():
                return False, None, f"Fichier non trouvé: {filepath}"
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convertir lists en arrays
            if 'times' in data and isinstance(data['times'], list):
                data['times'] = np.array(data['times'])
            if 'values' in data and isinstance(data['values'], list):
                data['values'] = np.array(data['values'])
            
            logger.info(f"✓ JSON chargé: {filepath}")
            return True, data, None
        
        except Exception as e:
            logger.error(f"Erreur JSON: {e}")
            return False, None, str(e)
    
    @staticmethod
    def save_json(filepath: str, data: Dict) -> Tuple[bool, Optional[str]]:
        """Sauvegarder données en JSON."""
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Convertir arrays en lists pour sérialisation
            data_serializable = {}
            for key, val in data.items():
                if isinstance(val, np.ndarray):
                    data_serializable[key] = val.tolist()
                elif isinstance(val, (np.integer, np.floating)):
                    data_serializable[key] = float(val)
                else:
                    data_serializable[key] = val
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data_serializable, f, indent=2)
            
            logger.info(f"✓ JSON sauvegardé: {filepath}")
            return True, None
        
        except Exception as e:
            logger.error(f"Erreur sauvegarde JSON: {e}")
            return False, str(e)
    
    @staticmethod
    def export_pdf(filepath: str, results: Dict, title: str = "HydroAI Results") -> Tuple[bool, Optional[str]]:
        """
        Exporter résultats en PDF.
        
        Args:
            filepath: Chemin destination PDF
            results: Dict avec résultats
            title: Titre du rapport
            
        Returns:
            (success, error_message)
        """
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors
            
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            doc = SimpleDocTemplate(str(filepath), pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Titre
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#0066cc'),
                spaceAfter=30
            )
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Résultats en tableau
            data = [['Parameter', 'Value']]
            for key, val in results.items():
                if not key.startswith('_'):
                    if isinstance(val, float):
                        data.append([key, f"{val:.6e}"])
                    else:
                        data.append([key, str(val)])
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.5*inch))
            
            # Metadata
            story.append(Paragraph(f"<i>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>", 
                                  styles['Normal']))
            
            doc.build(story)
            logger.info(f"✓ PDF exporté: {filepath}")
            return True, None
        
        except ImportError:
            logger.error("reportlab non installé - PDF export impossible")
            return False, "reportlab not installed. Run: pip install reportlab"
        except Exception as e:
            logger.error(f"Erreur export PDF: {e}")
            return False, str(e)
    
    @staticmethod
    def export_image(filepath: str, figure) -> Tuple[bool, Optional[str]]:
        """
        Exporter figure matplotlib en PNG.
        
        Args:
            filepath: Chemin destination
            figure: Figure matplotlib
            
        Returns:
            (success, error_message)
        """
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            figure.savefig(str(filepath), dpi=150, bbox_inches='tight')
            logger.info(f"✓ Image exportée: {filepath}")
            return True, None
        
        except Exception as e:
            logger.error(f"Erreur export image: {e}")
            return False, str(e)


def get_example_data(test_type: str = 'theis') -> Tuple[np.ndarray, np.ndarray]:
    """
    Retourner données d'exemple pour tests.
    
    Args:
        test_type: 'theis', 'lefranc', 'piezo'
        
    Returns:
        (times, values) arrays
    """
    if test_type.lower() == 'theis':
        # Données Theis synthétiques: T=1e-3 m²/s, S=1e-4
        times = np.array([1, 3, 10, 30, 100, 300, 1000, 3000, 10000])
        drawdowns = np.array([0.05, 0.12, 0.24, 0.38, 0.61, 0.86, 1.15, 1.43, 1.71])
        return times, drawdowns
    
    elif test_type.lower() == 'lefranc':
        # Données Lefranc: charge décroissante exponentielle
        times = np.linspace(0, 600, 50)
        heads = 1.5 * np.exp(-times/200) + 0.5
        return times, heads
    
    elif test_type.lower() == 'piezo':
        # Données piézométriques: tendance + oscillations
        times = np.arange(0, 365, 1)
        piezo = 100 + 5*np.sin(2*np.pi*times/365) - 0.01*times + np.random.normal(0, 0.5, len(times))
        return times, piezo
    
    else:
        raise ValueError(f"Unknown test type: {test_type}")
