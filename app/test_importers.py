"""
Tests du module d'importation
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.importers import (
    get_import_manager,
    CSVTXTImporter,
    ExcelImporter,
)


def create_test_csv():
    """Crée un fichier CSV de test"""
    data = {
        'X': [100, 101, 102, 103, 104],
        'Y': [200, 201, 202, 203, 204],
        'Z': [50.5, 51.2, 49.8, 52.1, 50.9],
        'Charge_m': [45.3, 45.5, 45.1, 45.8, 45.4],
        'Conductivite': [1e-4, 1.2e-4, 9.8e-5, 1.1e-4, 1.05e-4],
    }
    
    df = pd.DataFrame(data)
    filepath = '/tmp/test_points.csv'
    df.to_csv(filepath, index=False)
    return filepath


def create_test_excel():
    """Crée un fichier Excel de test"""
    data = {
        'X': [110, 111, 112],
        'Y': [210, 211, 212],
        'Z': [55.0, 56.0, 54.5],
        'Concentration_mg/L': [10.5, 11.2, 9.8],
    }
    
    df = pd.DataFrame(data)
    filepath = '/tmp/test_wells.xlsx'
    df.to_excel(filepath, index=False)
    return filepath


def test_csv_import():
    """Test d'importation CSV"""
    print("\n" + "="*60)
    print("TEST 1: Importation CSV")
    print("="*60)
    
    filepath = create_test_csv()
    print(f"Fichier créé: {filepath}")
    
    manager = get_import_manager()
    result = manager.import_file(filepath, x_col='X', y_col='Y')
    
    if result.success:
        print(f"✓ Importation réussie")
        print(f"  - Lignes: {result.metadata.rows}")
        print(f"  - Colonnes: {list(result.data.columns)}")
        print(f"  - Limites: {result.metadata.bounds}")
        print(f"\nDonnées:")
        print(result.data)
        print(f"\nStatistiques:")
        for key, value in result.statistics.items():
            print(f"  {key}: {value}")
    else:
        print(f"✗ Erreur: {result.errors}")
    
    if result.warnings:
        print(f"\nAvertissements: {result.warnings}")


def test_excel_import():
    """Test d'importation Excel"""
    print("\n" + "="*60)
    print("TEST 2: Importation Excel")
    print("="*60)
    
    filepath = create_test_excel()
    print(f"Fichier créé: {filepath}")
    
    manager = get_import_manager()
    result = manager.import_file(filepath, x_col='X', y_col='Y')
    
    if result.success:
        print(f"✓ Importation réussie")
        print(f"  - Lignes: {result.metadata.rows}")
        print(f"  - Colonnes: {list(result.data.columns)}")
        print(f"\nDonnées:")
        print(result.data)
    else:
        print(f"✗ Erreur: {result.errors}")


def test_format_detection():
    """Test de détection de format"""
    print("\n" + "="*60)
    print("TEST 3: Détection de formats supportés")
    print("="*60)
    
    manager = get_import_manager()
    formats = manager.get_supported_formats()
    
    print("Formats supportés:")
    for ext, desc in sorted(formats.items()):
        print(f"  {ext:10} - {desc}")


def test_batch_import():
    """Test d'importation batch"""
    print("\n" + "="*60)
    print("TEST 4: Importation batch")
    print("="*60)
    
    filepath_csv = create_test_csv()
    filepath_excel = create_test_excel()
    
    manager = get_import_manager()
    results = manager.batch_import([filepath_csv, filepath_excel])
    
    for i, result in enumerate(results, 1):
        status = "✓" if result.success else "✗"
        print(f"{status} Fichier {i}: {result.metadata.filename if result.metadata else 'Unknown'}")
        if not result.success:
            print(f"  Erreurs: {result.errors}")


def test_import_history():
    """Test d'historique"""
    print("\n" + "="*60)
    print("TEST 5: Historique d'importation")
    print("="*60)
    
    manager = get_import_manager()
    
    # Effectuer quelques importations
    filepath_csv = create_test_csv()
    filepath_excel = create_test_excel()
    
    manager.import_file(filepath_csv)
    manager.import_file(filepath_excel)
    
    # Afficher les stats
    stats = manager.get_import_statistics()
    print("Statistiques:")
    print(f"  Total: {stats['total_imports']}")
    print(f"  Réussies: {stats['successful']}")
    print(f"  Échouées: {stats['failed']}")
    print(f"  Formats utilisés: {stats['formats_used']}")
    
    # Afficher l'historique
    print("\nHistorique:")
    for entry in manager.get_import_history():
        print(f"  {entry['format']:10} - {entry.get('rows', '?')} lignes - {'OK' if entry['success'] else 'ERREUR'}")


def main():
    """Lance tous les tests"""
    print("\n" + "█"*60)
    print("TESTS MODULE D'IMPORTATION HYDROAI")
    print("█"*60)
    
    try:
        test_format_detection()
        test_csv_import()
        test_excel_import()
        test_batch_import()
        test_import_history()
        
        print("\n" + "█"*60)
        print("✓ TOUS LES TESTS COMPLÉTÉS")
        print("█"*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Erreur: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
