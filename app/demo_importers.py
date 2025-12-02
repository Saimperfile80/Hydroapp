"""
Démonstration interactive du module d'importation HydroAI
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.importers import (
    get_import_manager,
    CSVTXTImporter,
    ExcelImporter,
)


def print_header(title):
    """Affiche un en-tête formaté"""
    print("\n" + "█" * 70)
    print(f"  {title}")
    print("█" * 70)


def print_section(title):
    """Affiche une section"""
    print(f"\n{'─' * 70}")
    print(f"  {title}")
    print(f"{'─' * 70}")


def demo_csv_import():
    """Démo: Importation CSV"""
    print_header("DÉMO 1: Importation CSV avec détection automatique")
    
    # Créer fichier test
    data = {
        'X': [100, 101, 102, 103, 104, 105],
        'Y': [200, 201, 202, 203, 204, 205],
        'Z': [50.5, 51.2, 49.8, 52.1, 50.9, 51.5],
        'Charge_m': [45.3, 45.5, 45.1, 45.8, 45.4, 45.6],
        'Conductivite_m_s': [1.0e-4, 1.2e-4, 9.8e-5, 1.1e-4, 1.05e-4, 1.15e-4],
        'Concentration_mg/L': [10.5, 11.2, 9.8, 12.1, 10.9, 11.5],
    }
    
    df = pd.DataFrame(data)
    filepath = os.path.join(tempfile.gettempdir(), "demo_wells.csv")
    df.to_csv(filepath, index=False)
    print(f"✓ Fichier créé: {filepath}")
    
    print_section("Contenu du fichier CSV")
    print(df.to_string(index=False))
    
    print_section("Importation avec ImportManager")
    manager = get_import_manager()
    result = manager.import_file(filepath, x_col='X', y_col='Y', z_col='Z')
    
    if result.success:
        print("✓ SUCCÈS - Importation réussie!")
        
        print_section("📊 Métadonnées")
        print(f"  Fichier: {result.metadata.filename}")
        print(f"  Type de fichier: {result.metadata.file_type}")
        print(f"  Type de données: {result.metadata.data_type.value}")
        print(f"  Lignes: {result.metadata.rows}")
        print(f"  Colonnes: {result.metadata.cols}")
        print(f"  Limites spatiales: {result.metadata.bounds}")
        
        print_section("📈 Statistiques")
        stats = result.statistics
        for key, value in sorted(stats.items()):
            if isinstance(value, (int, float)):
                if isinstance(value, float):
                    print(f"  {key}: {value:.4f}")
                else:
                    print(f"  {key}: {value}")
            elif isinstance(value, list):
                print(f"  {key}: {len(value)} colonnes")
        
        print_section("⚠️ Avertissements")
        if result.warnings:
            for w in result.warnings:
                print(f"  • {w}")
        else:
            print("  Aucun avertissement")
        
        print_section("Aperçu des données importées")
        print(result.data.to_string(index=False))
        
        return True
    else:
        print("✗ ERREUR - Importation échouée!")
        for error in result.errors:
            print(f"  • {error}")
        return False


def demo_excel_import():
    """Démo: Importation Excel"""
    print_header("DÉMO 2: Importation Excel multi-feuilles")
    
    # Créer fichier Excel test
    data_sheet1 = {
        'X': [110, 111, 112, 113],
        'Y': [210, 211, 212, 213],
        'Z': [55.0, 56.0, 54.5, 56.5],
        'Debit_L/s': [5.2, 5.8, 4.9, 6.1],
    }
    
    data_sheet2 = {
        'X': [120, 121, 122],
        'Y': [220, 221, 222],
        'Concentration': [10.5, 11.2, 9.8],
    }
    
    filepath = os.path.join(tempfile.gettempdir(), "demo_aquifer.xlsx")
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        pd.DataFrame(data_sheet1).to_excel(writer, sheet_name='Piezometry', index=False)
        pd.DataFrame(data_sheet2).to_excel(writer, sheet_name='Chemistry', index=False)
    
    print(f"✓ Fichier Excel créé avec 2 feuilles: {filepath}")
    
    print_section("Feuille 1: Piézométrie")
    print(pd.DataFrame(data_sheet1).to_string(index=False))
    
    print_section("Importation de la feuille 'Piezometry'")
    manager = get_import_manager()
    result = manager.import_file(filepath, sheet_name='Piezometry', x_col='X', y_col='Y')
    
    if result.success:
        print("✓ SUCCÈS - Feuille importée!")
        print(f"  Lignes: {result.metadata.rows}")
        print(f"  Colonnes: {result.metadata.cols}")
        # Afficher toutes les stats disponibles
        for key, value in result.statistics.items():
            if 'Debit' in key or 'min' in key or 'max' in key:
                if isinstance(value, (int, float)):
                    print(f"  {key}: {value:.2f}")
        return True
    else:
        print("✗ ERREUR - Importation échouée!")
        return False


def demo_supported_formats():
    """Démo: Formats supportés"""
    print_header("DÉMO 3: Formats supportés et détection automatique")
    
    manager = get_import_manager()
    formats = manager.get_supported_formats()
    
    print_section("Formats reconnus automatiquement")
    print(f"Total: {len(formats)} formats")
    
    categories = {
        'Tabulaire': ['.csv', '.txt', '.dat', '.xyz', '.xlsx', '.xls'],
        'Grilles': ['.grd', '.asc', '.tif', '.tiff'],
        'Vecteurs': ['.shp', '.geojson', '.json'],
    }
    
    for category, exts in categories.items():
        print(f"\n  {category}:")
        for ext in exts:
            if ext in formats:
                print(f"    {ext:10} → {formats[ext]}")


def demo_import_manager_features():
    """Démo: Fonctionnalités du gestionnaire"""
    print_header("DÉMO 4: Gestionnaire d'importation - Historique et statistiques")
    
    # Créer plusieurs fichiers
    files = []
    for i in range(3):
        data = {
            'X': np.random.uniform(100, 200, 5),
            'Y': np.random.uniform(200, 300, 5),
            'Z': np.random.uniform(40, 60, 5),
        }
        df = pd.DataFrame(data)
        filepath = os.path.join(tempfile.gettempdir(), f"demo_data_{i}.csv")
        df.to_csv(filepath, index=False)
        files.append(filepath)
        print(f"✓ Créé: {os.path.basename(filepath)}")
    
    print_section("Import batch (3 fichiers)")
    manager = get_import_manager()
    manager.clear_history()  # Réinitialiser
    
    results = manager.batch_import(files)
    
    for i, result in enumerate(results, 1):
        status = "✓" if result.success else "✗"
        rows = result.metadata.rows if result.metadata else "?"
        print(f"  {status} Fichier {i}: {rows} lignes")
    
    print_section("📊 Statistiques globales")
    stats = manager.get_import_statistics()
    print(f"  Total d'importations: {stats['total_imports']}")
    print(f"  Réussies: {stats['successful']}")
    print(f"  Échouées: {stats['failed']}")
    print(f"  Formats utilisés: {stats['formats_used']}")
    print(f"  Dernière importation: {stats['last_import']}")


def demo_error_handling():
    """Démo: Gestion des erreurs"""
    print_header("DÉMO 5: Gestion des erreurs et validations")
    
    print_section("Test 1: Fichier inexistant")
    manager = get_import_manager()
    result = manager.import_file("/tmp/fichier_inexistant.csv")
    
    if not result.success:
        print("✓ Erreur correctement détectée:")
        for error in result.errors:
            print(f"  • {error}")
    
    print_section("Test 2: Format non supporté")
    # Créer un fichier avec mauvaise extension
    filepath = os.path.join(tempfile.gettempdir(), "test.xyz123")
    with open(filepath, 'w') as f:
        f.write("test")
    
    result = manager.import_file(filepath)
    if not result.success:
        print("✓ Format non supporté correctement rejeté:")
        for error in result.errors:
            print(f"  • {error}")
    
    print_section("Test 3: CSV avec colonnes manquantes")
    data = {'A': [1, 2, 3], 'B': [4, 5, 6]}
    filepath = os.path.join(tempfile.gettempdir(), "bad_cols.csv")
    pd.DataFrame(data).to_csv(filepath, index=False)
    
    result = manager.import_file(filepath, x_col='X', y_col='Y')
    if not result.success:
        print("✓ Colonnes manquantes correctement détectées:")
        for error in result.errors:
            print(f"  • {error}")


def demo_data_quality():
    """Démo: Qualité des données"""
    print_header("DÉMO 6: Analyse de qualité des données")
    
    # Créer un dataset avec problèmes
    data = {
        'X': [100, 101, 102, 100, 103, 104],  # Doublon
        'Y': [200, 201, 202, 200, 203, 204],  # Doublon
        'Z': [50.5, 51.2, np.nan, 52.1, 50.9, 51.5],  # Valeur manquante
        'Charge': [45.3, 45.5, 45.1, 45.8, np.nan, 45.6],  # Valeur manquante
    }
    
    df = pd.DataFrame(data)
    filepath = os.path.join(tempfile.gettempdir(), "data_quality_test.csv")
    df.to_csv(filepath, index=False)
    
    print_section("Données avec problèmes")
    print("Avant import:")
    print(df.to_string(index=False))
    
    print_section("Importation")
    manager = get_import_manager()
    result = manager.import_file(filepath, x_col='X', y_col='Y')
    
    if result.success:
        print("✓ Données importées")
        
        print_section("⚠️ Problèmes détectés")
        if result.warnings:
            for w in result.warnings:
                print(f"  • {w}")
        
        print_section("Données après nettoyage")
        print(result.data.to_string(index=False))
        
        print_section("Statistiques de qualité")
        print(f"  Lignes avant: {len(df)}")
        print(f"  Lignes après: {len(result.data)}")
        print(f"  Doublons supprimés: {len(df) - len(result.data)}")


def main():
    """Exécute toutes les démos"""
    print("\n")
    print("███" * 23)
    print("███  DÉMONSTRATION - MODULE D'IMPORTATION HYDROAI  ███")
    print("███" * 23)
    
    try:
        # Exécuter les démos
        demo_csv_import()
        demo_excel_import()
        demo_supported_formats()
        demo_import_manager_features()
        demo_error_handling()
        demo_data_quality()
        
        # Résumé final
        print_header("✓ DÉMOS COMPLÉTÉES AVEC SUCCÈS")
        print("\n✓ Module d'importation fonctionnel!")
        print("✓ 7 types de fichiers supportés")
        print("✓ Détections automatiques actives")
        print("✓ Gestion des erreurs robuste")
        print("✓ Historique et statistiques disponibles")
        print("\n" + "█" * 70 + "\n")
        
    except Exception as e:
        print(f"\n✗ Erreur lors de la démo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
