#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Onglet Piézométrie - Analyse séries temporelles
"""

import numpy as np
import logging

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QGroupBox, QGridLayout, QTextEdit, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from core.calculations import piezo

logger = logging.getLogger(__name__)


class PiezoTab(QWidget):
    """Onglet pour analyse piézométrie"""
    
    def __init__(self):
        super().__init__()
        self.data = None
        self.piezo_data = {}  # Points piézométriques (x, z)
        self.init_ui()
    
    def get_data(self):
        """Retourner les données piézométriques actuelles"""
        data = {}
        
        if self.data:
            data.update(self.data)
        
        if self.piezo_data:
            data.update(self.piezo_data)
        
        # Ajouter paramètres d'analyse
        try:
            data['dt'] = float(self.dt_input.text()) if self.dt_input.text() else 1.0
        except:
            data['dt'] = 1.0
        
        return data if data else None
    
    def init_ui(self):
        """Initialiser interface"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Onglets: Manuel vs Import
        from PySide6.QtWidgets import QTabWidget, QTextEdit
        input_tabs = QTabWidget()
        
        # Tab 1: Saisie manuelle
        manual_widget = QWidget()
        manual_layout = QVBoxLayout(manual_widget)
        manual_layout.addWidget(QLabel("📝 Entrez niveaux d'eau (m)"))
        manual_layout.addWidget(QLabel("<small>Format: jour,niveau (une ligne par mesure)</small>"))
        
        self.manual_piezo_text = QTextEdit()
        self.manual_piezo_text.setPlaceholderText(
            "Exemple:\n1,100.5\n5,102.3\n10,103.1\n15,101.8\n20,100.2"
        )
        self.manual_piezo_text.setMaximumHeight(120)
        self.manual_piezo_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                padding: 5px;
            }
        """)
        manual_layout.addWidget(self.manual_piezo_text)
        
        btn_load_manual = QPushButton("✓ Charger")
        btn_load_manual.clicked.connect(self.load_manual_piezo)
        manual_layout.addWidget(btn_load_manual)
        manual_layout.addStretch()
        
        input_tabs.addTab(manual_widget, "📝 Saisie manuelle")
        
        # Tab 2: Import fichier
        import_widget = QWidget()
        import_layout = QVBoxLayout(import_widget)
        
        import_info = QLabel("📂 Importer fichier CSV\nFormat: jour, niveau_eau (m)")
        import_layout.addWidget(import_info)
        
        btn_import = QPushButton("📂 Importer CSV")
        btn_import.clicked.connect(self.import_data)
        import_layout.addWidget(btn_import)
        
        self.file_label = QLabel("Aucun fichier")
        self.file_label.setStyleSheet("color: #666666; font-size: 9pt;")
        import_layout.addWidget(self.file_label)
        
        import_layout.addStretch()
        input_tabs.addTab(import_widget, "📂 Importer CSV")
        
        layout.addWidget(input_tabs)
        
        # Paramètres analyse
        params_group = QGroupBox("⚙️  Paramètres d'analyse")
        params_layout = QGridLayout(params_group)
        
        params_layout.addWidget(QLabel("Pas de temps (jours):"), 0, 0)
        self.dt_input = QLineEdit()
        self.dt_input.setText("1")
        params_layout.addWidget(self.dt_input, 0, 1)
        
        layout.addWidget(params_group)
        
        # Bouton analyse
        btn_analyze = QPushButton("▶ Analyser")
        btn_analyze.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: white;
                font-weight: bold;
                padding: 10px;
            }
        """)
        btn_analyze.clicked.connect(self.run_analysis)
        layout.addWidget(btn_analyze)
        
        # Résultats
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(QLabel("📊 Résultats statistiques"))
        layout.addWidget(self.results_text, 1)
        
        # Canvas
        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(QLabel("📈 Graphique"))
        layout.addWidget(self.canvas, 1)
    
    def import_data(self):
        """Importer données CSV"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Importer piézométrie", "", "CSV (*.csv)"
        )
        if filepath:
            try:
                data = np.genfromtxt(filepath, delimiter=',', skip_header=1)
                self.data = data[:, 1]  # Prendre colonne niveaux
                self.file_label.setText(f"✓ {len(self.data)} mesures importées")
                logger.info(f"Données piézométriques importées: {len(self.data)} points")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur import: {e}")
    
    def load_manual_piezo(self):
        """Charger données piézométriques saisies manuellement"""
        try:
            text = self.manual_piezo_text.toPlainText()
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            
            data = []
            for line in lines:
                parts = line.split(',')
                try:
                    niveau = float(parts[1].strip())
                    data.append(niveau)
                except (IndexError, ValueError):
                    continue
            
            if not data:
                QMessageBox.warning(self, "Erreur", "Aucune donnée valide trouvée")
                return
            
            self.data = np.array(data)
            msg = f"✓ Données chargées: {len(data)} points"
            self.file_label.setText(msg)
            logger.info(msg)
            QMessageBox.information(self, "Succès", msg)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {e}")
    
    def run_analysis(self):
        """Exécuter analyse"""
        if self.data is None:
            QMessageBox.warning(self, "Attention", "Importer données d'abord")
            return
        
        try:
            # Créer dates (jours depuis J0)
            from datetime import datetime, timedelta
            dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(len(self.data))]
            
            analysis = piezo.PiezoAnalysis(dates=dates, levels=self.data)
            stats = analysis.get_statistics()
            
            # Afficher résultats
            text = """
<b>Statistiques piézométriques</b>
<hr>
<b>Résumé données:</b>
"""
            text += f"• Nombre mesures: {stats['n_points']}\n"
            text += f"• Minimum: {stats['min']:.4f} m\n"
            text += f"• Maximum: {stats['max']:.4f} m\n"
            text += f"• Moyenne: {stats['mean']:.4f} m\n"
            text += f"• Écart-type: {stats['std']:.4f} m\n"
            text += f"• Amplitude: {stats['amplitude']:.4f} m\n"
            
            # Tendance
            trend = analysis.compute_trend()
            text += f"""
<b>Tendance:</b>
• Pente: {trend['slope_m_day']:.6f} m/jour ({trend['slope_m_year']:.3f} m/an)
• Intercept: {trend['intercept']:.4f} m
• R²: {trend['r_squared']:.4f}
• Interprétation: {trend['interpretation']}
"""
            
            # Classification aquifère
            aquifer = analysis.identify_aquifer_type()
            text += f"""
<b>Type aquifère:</b>
• Comportement: {aquifer['behavior']}
• Réactivité: {aquifer['reactivity']}
• Amplitude: {aquifer['amplitude_m']:.4f} m
"""
            
            self.results_text.setText(text)
            
            # Tracer
            self.plot_piezo(analysis)
            
        except Exception as e:
            logger.error(f"Erreur analyse: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur analyse: {e}")
    
    def plot_piezo(self, analysis):
        """Tracer graphiques"""
        self.figure.clear()
        
        ax1 = self.figure.add_subplot(211)
        ax1.plot(self.data, 'b-', linewidth=2, label='Niveau mesuré')
        ax1.set_ylabel('Niveau d\'eau (m)', fontsize=10)
        ax1.set_title('Série temporelle piézométrique', fontsize=11, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Histogramme
        ax2 = self.figure.add_subplot(212)
        ax2.hist(self.data, bins=20, color='lightblue', edgecolor='black')
        ax2.set_xlabel('Niveau d\'eau (m)', fontsize=10)
        ax2.set_ylabel('Fréquence', fontsize=10)
        ax2.grid(True, alpha=0.3, axis='y')
        
        self.figure.tight_layout()
        self.canvas.draw()
