"""
Fenêtre principale HydroAI avec tous les modules
"""

import sys
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QFileDialog, QTableWidget, QTableWidgetItem,
    QMessageBox, QStatusBar, QMenuBar, QMenu, QComboBox, QSpinBox,
    QDoubleSpinBox, QLineEdit, QFormLayout, QGroupBox, QProgressBar
)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QColor, QPixmap, QFont
from PyQt6.QtCore import QTimer
import pandas as pd

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.importers import get_import_manager


class MainWindow(QMainWindow):
    """Fenêtre principale de HydroAI"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HydroAI - Modélisation Hydrogéologique avec IA")
        self.setGeometry(100, 100, 1400, 900)
        
        # État de l'application
        self.current_data = None
        self.import_manager = get_import_manager()
        
        # Créer l'interface
        self.init_ui()
        self.apply_stylesheet()
        
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Menu bar
        self.create_menu_bar()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # En-tête avec logo et titre
        header = self.create_header()
        layout.addWidget(header)
        
        # Onglets principaux
        tabs = QTabWidget()
        
        # Onglet 1: Accueil
        tabs.addTab(self.create_home_tab(), "🏠 Accueil")
        
        # Onglet 2: Données
        tabs.addTab(self.create_data_tab(), "📊 Données")
        
        # Onglet 3: Géométrie
        tabs.addTab(self.create_geometry_tab(), "🔲 Géométrie")
        
        # Onglet 4: Simulation
        tabs.addTab(self.create_simulation_tab(), "⚙️ Simulation")
        
        # Onglet 5: IA
        tabs.addTab(self.create_ia_tab(), "🤖 IA")
        
        # Onglet 6: Résultats
        tabs.addTab(self.create_results_tab(), "📈 Résultats")
        
        # Onglet 7: Bassin versant
        tabs.addTab(self.create_watershed_tab(), "💧 Bassin Versant")
        
        layout.addWidget(tabs)
        
        # Barre de statut
        self.statusBar().showMessage("Prêt")
        
        central_widget.setLayout(layout)
    
    def create_menu_bar(self):
        """Crée la barre de menu"""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("📁 Fichier")
        
        action_new = file_menu.addAction("Nouveau projet")
        action_new.triggered.connect(self.new_project)
        
        action_open = file_menu.addAction("Ouvrir projet")
        action_open.triggered.connect(self.open_project)
        
        action_save = file_menu.addAction("Enregistrer")
        action_save.triggered.connect(self.save_project)
        
        file_menu.addSeparator()
        action_exit = file_menu.addAction("Quitter")
        action_exit.triggered.connect(self.close)
        
        # Menu Édition
        edit_menu = menubar.addMenu("✏️ Édition")
        edit_menu.addAction("Annuler")
        edit_menu.addAction("Refaire")
        
        # Menu Aide
        help_menu = menubar.addMenu("❓ Aide")
        help_menu.addAction("À propos")
        help_menu.addAction("Documentation")
    
    def create_header(self):
        """Crée l'en-tête de l'application"""
        widget = QWidget()
        layout = QHBoxLayout()
        
        # Logo/titre
        title = QLabel("HydroAI")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #13a4ec;")
        
        subtitle = QLabel("Plateforme de modélisation hydrogéologique intégrée avec IA")
        subtitle.setStyleSheet("color: #666; font-size: 12px;")
        
        left_layout = QVBoxLayout()
        left_layout.addWidget(title)
        left_layout.addWidget(subtitle)
        
        layout.addLayout(left_layout)
        layout.addStretch()
        
        widget.setLayout(layout)
        widget.setStyleSheet("background-color: #f0f0f0; padding: 15px; border-radius: 5px;")
        
        return widget
    
    def create_home_tab(self):
        """Onglet d'accueil"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Titre
        title = QLabel("Bienvenue dans HydroAI")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        
        # Description
        description = QLabel(
            "HydroAI est une plateforme complète de modélisation hydrogéologique "
            "2D/3D par éléments finis avec intégration d'intelligence artificielle.\n\n"
            "Fonctionnalités principales:\n"
            "• Importation multiformat (CSV, Excel, Surfer, GeoTIFF, SHP, GeoJSON)\n"
            "• Maillage 2D/3D automatique et adaptatif\n"
            "• Solveur d'écoulement par éléments finis\n"
            "• Transport de solutés et hydrochimie\n"
            "• Module d'intelligence artificielle intégré\n"
            "• Génération et analyse de bassins versants\n"
            "• Visualisation et export (PNG, PDF)\n"
            "• Gestion complète de projets"
        )
        description.setWordWrap(True)
        description.setStyleSheet("font-size: 11px; line-height: 1.5;")
        
        # Boutons d'action
        buttons_layout = QHBoxLayout()
        
        btn_new = QPushButton("➕ Nouveau projet")
        btn_new.setMinimumWidth(200)
        btn_new.setStyleSheet("""
            QPushButton {
                background-color: #13a4ec;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0d7ab3;
            }
        """)
        btn_new.clicked.connect(self.new_project)
        
        btn_open = QPushButton("📂 Ouvrir projet")
        btn_open.setMinimumWidth(200)
        btn_open.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d8b40;
            }
        """)
        btn_open.clicked.connect(self.open_project)
        
        btn_import = QPushButton("📥 Importer données")
        btn_import.setMinimumWidth(200)
        btn_import.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
        """)
        
        buttons_layout.addWidget(btn_new)
        buttons_layout.addWidget(btn_open)
        buttons_layout.addWidget(btn_import)
        buttons_layout.addStretch()
        
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addSpacing(20)
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_data_tab(self):
        """Onglet gestion des données"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Section importation
        import_group = QGroupBox("📥 Importation de données")
        import_layout = QVBoxLayout()
        
        btn_import = QPushButton("Sélectionner fichier...")
        btn_import.clicked.connect(self.import_file)
        
        self.import_status = QLabel("Aucun fichier importé")
        self.import_status.setStyleSheet("color: #999;")
        
        import_layout.addWidget(btn_import)
        import_layout.addWidget(self.import_status)
        import_group.setLayout(import_layout)
        
        # Section aperçu des données
        data_group = QGroupBox("📊 Aperçu des données")
        data_layout = QVBoxLayout()
        
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels(["X", "Y", "Z", "Charge", "Conductivité"])
        self.data_table.setMaximumHeight(300)
        
        data_layout.addWidget(self.data_table)
        data_group.setLayout(data_layout)
        
        # Section statistiques
        stats_group = QGroupBox("📈 Statistiques")
        stats_layout = QVBoxLayout()
        
        self.stats_label = QLabel("Aucune donnée")
        self.stats_label.setStyleSheet("font-family: monospace; font-size: 10px;")
        
        stats_layout.addWidget(self.stats_label)
        stats_group.setLayout(stats_layout)
        
        layout.addWidget(import_group)
        layout.addWidget(data_group)
        layout.addWidget(stats_group)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_geometry_tab(self):
        """Onglet géométrie et maillage"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Section domaine
        domain_group = QGroupBox("🗺️ Définition du domaine")
        domain_layout = QFormLayout()
        
        domain_layout.addRow("Projection:", QLineEdit("EPSG:32632"))
        domain_layout.addRow("Xmin (m):", QDoubleSpinBox())
        domain_layout.addRow("Xmax (m):", QDoubleSpinBox())
        domain_layout.addRow("Ymin (m):", QDoubleSpinBox())
        domain_layout.addRow("Ymax (m):", QDoubleSpinBox())
        
        domain_group.setLayout(domain_layout)
        
        # Section maillage
        mesh_group = QGroupBox("🔲 Paramètres de maillage")
        mesh_layout = QFormLayout()
        
        mesh_type = QComboBox()
        mesh_type.addItems(["Triangulation 2D", "Extrusion 3D par couches"])
        mesh_layout.addRow("Type de maillage:", mesh_type)
        
        mesh_layout.addRow("Taille min éléments (m):", QDoubleSpinBox())
        mesh_layout.addRow("Taille max éléments (m):", QDoubleSpinBox())
        mesh_layout.addRow("Nombre de couches (3D):", QSpinBox())
        
        btn_generate = QPushButton("🔧 Générer maillage")
        btn_generate.setStyleSheet("""
            QPushButton {
                background-color: #13a4ec;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
        """)
        mesh_layout.addRow(btn_generate)
        
        mesh_group.setLayout(mesh_layout)
        
        # Section aperçu
        preview_group = QGroupBox("👁️ Aperçu")
        preview_layout = QVBoxLayout()
        preview_label = QLabel("Aperçu du maillage (à implémenter)")
        preview_label.setStyleSheet("border: 1px solid #ccc; padding: 20px; background-color: #f9f9f9;")
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_label.setMinimumHeight(300)
        preview_layout.addWidget(preview_label)
        preview_group.setLayout(preview_layout)
        
        layout.addWidget(domain_group)
        layout.addWidget(mesh_group)
        layout.addWidget(preview_group)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_simulation_tab(self):
        """Onglet simulation"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Section conditions aux limites
        bc_group = QGroupBox("🚧 Conditions aux limites")
        bc_layout = QVBoxLayout()
        
        bc_table = QTableWidget()
        bc_table.setColumnCount(4)
        bc_table.setHorizontalHeaderLabels(["Type", "Valeur", "Unité", "Description"])
        bc_table.setMaximumHeight(200)
        bc_layout.addWidget(bc_table)
        
        bc_group.setLayout(bc_layout)
        
        # Section paramètres
        param_group = QGroupBox("⚙️ Paramètres hydrodynamiques")
        param_layout = QFormLayout()
        
        param_layout.addRow("Conductivité K (m/s):", QLineEdit("1e-5"))
        param_layout.addRow("Porosité (%):", QDoubleSpinBox())
        param_layout.addRow("Coefficient d'emmagasinement:", QLineEdit("0.001"))
        param_layout.addRow("Temps de simulation (jours):", QSpinBox())
        param_layout.addRow("Pas de temps (jours):", QDoubleSpinBox())
        
        param_group.setLayout(param_layout)
        
        # Section exécution
        exec_group = QGroupBox("▶️ Exécution")
        exec_layout = QVBoxLayout()
        
        btn_run = QPushButton("▶️ Lancer simulation")
        btn_run.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3d8b40;
            }
        """)
        
        self.progress = QProgressBar()
        self.progress.setValue(0)
        
        exec_layout.addWidget(btn_run)
        exec_layout.addWidget(self.progress)
        
        exec_group.setLayout(exec_layout)
        
        layout.addWidget(bc_group)
        layout.addWidget(param_group)
        layout.addWidget(exec_group)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_ia_tab(self):
        """Onglet IA"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Section analyse IA
        analysis_group = QGroupBox("🤖 Analyse IA des données")
        analysis_layout = QVBoxLayout()
        
        btn_analyze = QPushButton("🔍 Analyser les données")
        btn_analyze.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        
        self.ia_results = QLabel(
            "Fonctionnalités IA:\n"
            "✓ Détection d'anomalies dans les données\n"
            "✓ Estimation de valeurs manquantes\n"
            "✓ Suggestion de plages de paramètres\n"
            "✓ Validation pré-calcul\n"
            "✓ Score de confiance explicable"
        )
        self.ia_results.setWordWrap(True)
        self.ia_results.setStyleSheet("border: 1px solid #ccc; padding: 10px; background-color: #f9f9f9;")
        
        analysis_layout.addWidget(btn_analyze)
        analysis_layout.addWidget(self.ia_results)
        
        analysis_group.setLayout(analysis_layout)
        
        # Section aide paramétrisation
        help_group = QGroupBox("💡 Aide à la paramétrisation")
        help_layout = QVBoxLayout()
        
        help_text = QLabel(
            "Basé sur l'apprentissage automatique, le module IA propose:\n\n"
            "1. Suggestions de conductivité selon la lithologie\n"
            "2. Détection d'incohérences dans les données\n"
            "3. Complétion automatique de valeurs manquantes\n"
            "4. Validation de cohérence pré-simulation\n"
            "5. Explicabilité des recommandations"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("background-color: #f0f7ff; padding: 10px; border-radius: 5px;")
        
        help_layout.addWidget(help_text)
        help_group.setLayout(help_layout)
        
        layout.addWidget(analysis_group)
        layout.addWidget(help_group)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_results_tab(self):
        """Onglet résultats"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Section visualisation
        viz_group = QGroupBox("📊 Visualisation des résultats")
        viz_layout = QVBoxLayout()
        
        viz_combo = QComboBox()
        viz_combo.addItems([
            "Cartes de charge hydraulique",
            "Panaches de concentration",
            "Coupes verticales",
            "Séries temporelles",
            "Vecteurs de vitesse"
        ])
        
        viz_canvas = QLabel("Zone de visualisation (à implémenter)")
        viz_canvas.setStyleSheet("border: 2px solid #ccc; background-color: #f9f9f9;")
        viz_canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        viz_canvas.setMinimumHeight(400)
        
        viz_layout.addWidget(QLabel("Type de visualisation:"))
        viz_layout.addWidget(viz_combo)
        viz_layout.addWidget(viz_canvas)
        
        viz_group.setLayout(viz_layout)
        
        # Section export
        export_group = QGroupBox("💾 Export des résultats")
        export_layout = QVBoxLayout()
        
        btn_export_png = QPushButton("📷 Exporter en PNG")
        btn_export_pdf = QPushButton("📄 Exporter en PDF")
        btn_export_csv = QPushButton("📊 Exporter en CSV")
        
        for btn in [btn_export_png, btn_export_pdf, btn_export_csv]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    padding: 8px;
                    border-radius: 5px;
                }
            """)
        
        export_layout.addWidget(btn_export_png)
        export_layout.addWidget(btn_export_pdf)
        export_layout.addWidget(btn_export_csv)
        
        export_group.setLayout(export_layout)
        
        layout.addWidget(viz_group)
        layout.addWidget(export_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_watershed_tab(self):
        """Onglet bassin versant"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Section MNT
        dem_group = QGroupBox("🗺️ Modèle Numérique de Terrain")
        dem_layout = QVBoxLayout()
        
        btn_import_dem = QPushButton("📥 Importer MNT (GeoTIFF, Surfer...)")
        dem_layout.addWidget(btn_import_dem)
        
        dem_group.setLayout(dem_layout)
        
        # Section bassin
        basin_group = QGroupBox("💧 Analyse de bassin versant")
        basin_layout = QVBoxLayout()
        
        btn_delineate = QPushButton("🎯 Délimiter bassin versant")
        btn_delineate.setStyleSheet("""
            QPushButton {
                background-color: #13a4ec;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        
        basin_stats = QLabel(
            "Statistiques du bassin:\n"
            "• Surface: -- km²\n"
            "• Pente moyenne: -- %\n"
            "• Altitude moyenne: -- m\n"
            "• Réseau hydrographique: -- km"
        )
        basin_stats.setStyleSheet("border: 1px solid #ccc; padding: 10px; background-color: #f9f9f9; font-family: monospace;")
        
        basin_layout.addWidget(btn_delineate)
        basin_layout.addWidget(basin_stats)
        
        basin_group.setLayout(basin_layout)
        
        # Section export
        export_group = QGroupBox("💾 Export")
        export_layout = QVBoxLayout()
        
        btn_export_shp = QPushButton("📦 Exporter en Shapefile")
        btn_export_shp.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
        """)
        
        export_layout.addWidget(btn_export_shp)
        export_group.setLayout(export_layout)
        
        layout.addWidget(dem_group)
        layout.addWidget(basin_group)
        layout.addWidget(export_group)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def import_file(self):
        """Importe un fichier de données"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un fichier de données",
            "",
            "Tous les fichiers (*.csv *.txt *.xlsx *.xls *.grd *.asc *.tif *.shp *.geojson)"
        )
        
        if filepath:
            result = self.import_manager.import_file(filepath, x_col='X', y_col='Y')
            
            if result.success:
                self.current_data = result
                self.import_status.setText(f"✓ {result.metadata.filename} importé ({result.metadata.rows} lignes)")
                self.import_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
                
                # Remplir la table
                self.update_data_table(result.data)
                
                # Afficher les stats
                self.update_stats_label(result.statistics)
                
                self.statusBar().showMessage(f"Fichier importé: {result.metadata.filename}")
            else:
                QMessageBox.critical(self, "Erreur", "\n".join(result.errors))
    
    def update_data_table(self, data):
        """Met à jour la table de données"""
        self.data_table.setRowCount(len(data))
        
        for row, (_, row_data) in enumerate(data.iterrows()):
            for col, (col_name, value) in enumerate(row_data.items()):
                if col < 5:  # Limiter à 5 colonnes
                    item = QTableWidgetItem(str(value)[:10])
                    self.data_table.setItem(row, col, item)
    
    def update_stats_label(self, stats):
        """Met à jour les statistiques"""
        text = "Statistiques:\n"
        for key, value in list(stats.items())[:10]:
            if isinstance(value, float):
                text += f"• {key}: {value:.4f}\n"
            else:
                text += f"• {key}: {value}\n"
        
        self.stats_label.setText(text)
    
    def new_project(self):
        """Crée un nouveau projet"""
        QMessageBox.information(self, "Nouveau projet", "Fonction en cours de développement")
        self.statusBar().showMessage("Nouveau projet créé")
    
    def open_project(self):
        """Ouvre un projet existant"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir un projet", "", "Projets HydroAI (*.hydroai)"
        )
        if filepath:
            self.statusBar().showMessage(f"Projet ouvert: {filepath}")
    
    def save_project(self):
        """Enregistre le projet"""
        QMessageBox.information(self, "Enregistrement", "Projet enregistré")
        self.statusBar().showMessage("Projet enregistré")
    
    def apply_stylesheet(self):
        """Applique le style global"""
        stylesheet = """
            QMainWindow {
                background-color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 8px 20px;
                border: 1px solid #ccc;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #13a4ec;
                color: white;
            }
            QGroupBox {
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """
        self.setStyleSheet(stylesheet)


def main():
    """Fonction principale"""
    app = __import__('PyQt6.QtWidgets', fromlist=['QApplication']).QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
