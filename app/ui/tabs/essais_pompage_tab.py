#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Onglet Essais de Pompage - Theis & Cooper-Jacob
Interface pour entrée données, calcul, visualisation
"""

import numpy as np
import logging
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QSpinBox, QDoubleSpinBox, QFileDialog, QGroupBox,
    QGridLayout, QTextEdit, QTabWidget, QMessageBox, QProgressBar,
    QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Import modules HydroAI
from core.calculations import theis, cooper_jacob
from core.ai import PreComputeValidator
from app.data.io_manager import DataIOManager

logger = logging.getLogger(__name__)


class EssaisPompageTab(QWidget):
    """Onglet pour analyse essais de pompage (transitoire)"""
    
    def __init__(self):
        super().__init__()
        self.data = None  # Données chargées
        self.result = None  # Résultats dernière analyse
        self.init_ui()
    
    def get_data(self):
        """Retourner les données actuelles (pour simulation)"""
        if self.data is None:
            return None
        
        # Ajouter les paramètres d'entrée aux données
        data = self.data.copy() if isinstance(self.data, dict) else {'data': self.data}
        
        # Ajouter les paramètres de l'interface
        data['Q'] = self.Q_input.value()  # Débit (m³/s)
        data['distance'] = self.r_input.value()  # Distance (m)
        data['method'] = self.method_combo.currentText()
        
        # Si résultat disponible, l'inclure
        if self.result:
            data['T'] = self.result.get('T', None)  # Transmissivité
            data['S'] = self.result.get('S', None)  # Emmagasinement
        
        return data
    
    def init_ui(self):
        """Initialiser interface"""
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Panneau gauche: Saisie + Contrôles
        left_layout = QVBoxLayout()
        
        # Onglets: Manuel vs Fichier
        input_tabs = QTabWidget()
        
        # Tab 1: Saisie manuelle
        manual_widget = self.create_manual_input()
        input_tabs.addTab(manual_widget, "📝 Saisie manuelle")
        
        # Tab 2: Import fichier
        file_widget = self.create_file_input()
        input_tabs.addTab(file_widget, "📂 Importer CSV")
        
        left_layout.addWidget(QLabel("📥 Données d'entrée"))
        left_layout.addWidget(input_tabs)
        
        # Paramètres analyse
        params_group = QGroupBox("⚙️  Paramètres d'analyse")
        params_layout = QGridLayout(params_group)
        
        params_layout.addWidget(QLabel("Débit Q (m³/s):"), 0, 0)
        self.Q_input = QDoubleSpinBox()
        self.Q_input.setMinimum(0.00001)
        self.Q_input.setMaximum(10)
        self.Q_input.setValue(0.001)
        self.Q_input.setDecimals(6)
        params_layout.addWidget(self.Q_input, 0, 1)
        
        params_layout.addWidget(QLabel("Distance r (m):"), 1, 0)
        self.r_input = QDoubleSpinBox()
        self.r_input.setMinimum(0.1)
        self.r_input.setMaximum(1000)
        self.r_input.setValue(50)
        self.r_input.setDecimals(2)
        params_layout.addWidget(self.r_input, 1, 1)
        
        params_layout.addWidget(QLabel("Méthode:"), 2, 0)
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Theis (complet)", "Cooper-Jacob (semi-log)"])
        params_layout.addWidget(self.method_combo, 2, 1)
        
        left_layout.addWidget(params_group)
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        
        self.btn_validate = QPushButton("✓ Valider")
        self.btn_validate.clicked.connect(self.validate_params)
        button_layout.addWidget(self.btn_validate)
        
        self.btn_analyze = QPushButton("▶ Analyser")
        self.btn_analyze.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: white;
                font-weight: bold;
                padding: 10px;
            }
        """)
        self.btn_analyze.clicked.connect(self.run_analysis)
        button_layout.addWidget(self.btn_analyze)
        
        left_layout.addLayout(button_layout)
        
        # Validation status
        self.validation_text = QTextEdit()
        self.validation_text.setReadOnly(True)
        self.validation_text.setMaximumHeight(100)
        self.validation_text.setPlaceholderText("Statut validation ici...")
        left_layout.addWidget(QLabel("🔍 Validation (IA)"))
        left_layout.addWidget(self.validation_text)
        
        left_layout.addStretch()
        
        # Panneau droit: Résultats + Visualisation
        right_layout = QVBoxLayout()
        
        # Résultats texte
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("Résultats ici...")
        right_layout.addWidget(QLabel("📊 Résultats"))
        right_layout.addWidget(self.results_text, 1)
        
        # Canvas matplotlib
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        right_layout.addWidget(QLabel("📈 Graphique"))
        right_layout.addWidget(self.canvas, 2)
        
        # Boutons export
        export_layout = QHBoxLayout()
        
        btn_export_csv = QPushButton("💾 Export CSV")
        btn_export_csv.clicked.connect(self.export_csv)
        export_layout.addWidget(btn_export_csv)
        
        btn_export_pdf = QPushButton("📄 Export PDF")
        btn_export_pdf.clicked.connect(self.export_pdf)
        export_layout.addWidget(btn_export_pdf)
        
        export_layout.addStretch()
        right_layout.addLayout(export_layout)
        
        # Combiner panneaux
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 1)
        
        self.setLayout(main_layout)
        
        # Afficher graphe vide au démarrage
        self.plot_empty_graph()
    
    def create_manual_input(self):
        """Créer widget saisie manuelle"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("📝 Saisir temps (s) et rabattements (m)"))
        layout.addWidget(QLabel("<small>Format: temps,rabattement (une ligne par mesure)</small>"))
        
        self.manual_data_text = QTextEdit()
        self.manual_data_text.setPlaceholderText(
            "Exemple:\n10,0.020\n50,0.045\n100,0.062\n500,0.115\n1000,0.145"
        )
        self.manual_data_text.setMaximumHeight(120)
        self.manual_data_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                padding: 5px;
            }
        """)
        layout.addWidget(self.manual_data_text)
        
        btn_layout = QHBoxLayout()
        
        btn_load_manual = QPushButton("✓ Charger")
        btn_load_manual.clicked.connect(self.load_manual_data)
        btn_load_manual.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                padding: 6px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        btn_layout.addWidget(btn_load_manual)
        
        btn_clear = QPushButton("🗑️  Effacer")
        btn_clear.clicked.connect(self.clear_manual_data)
        btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                padding: 6px;
            }
            QPushButton:hover { background-color: #da190b; }
        """)
        btn_layout.addWidget(btn_clear)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        return widget
    
    def clear_manual_data(self):
        """Effacer données manuelle"""
        self.manual_data_text.clear()
        self.data = None
        self.result = None
        self.plot_empty_graph()
        QMessageBox.information(self, "Succès", "Données effacées")
    
    def create_file_input(self):
        """Créer widget import fichier"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Importer données depuis fichier CSV"))
        layout.addWidget(QLabel("Format CSV: temps (col 1), rabattement (col 2)"))
        
        self.file_path_label = QLabel("Aucun fichier chargé")
        self.file_path_label.setStyleSheet("color: #666666; font-size: 9pt;")
        layout.addWidget(self.file_path_label)
        
        btn_layout = QVBoxLayout()
        
        btn_browse = QPushButton("📂 Parcourir...")
        btn_browse.clicked.connect(self.browse_file)
        btn_layout.addWidget(btn_browse)
        
        # Boutons exemples
        layout.addWidget(QLabel("Ou charger un exemple:"))
        
        example_layout = QHBoxLayout()
        btn_example = QPushButton("📊 Exemple Theis")
        btn_example.clicked.connect(lambda: self.load_example('theis'))
        example_layout.addWidget(btn_example)
        
        btn_example2 = QPushButton("📊 Exemple simple")
        btn_example2.clicked.connect(lambda: self.load_example('simple'))
        example_layout.addWidget(btn_example2)
        
        layout.addLayout(example_layout)
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        return widget
    
    def load_manual_data(self):
        """Charger données saisies manuellement"""
        try:
            text = self.manual_data_text.toPlainText()
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            
            times = []
            drawdowns = []
            for line in lines:
                parts = line.split(',')
                times.append(float(parts[0].strip()))
                drawdowns.append(float(parts[1].strip()))
            
            self.data = {
                'times': np.array(times),
                'drawdowns': np.array(drawdowns)
            }
            
            msg = f"✓ Données chargées: {len(times)} points"
            logger.info(msg)
            QMessageBox.information(self, "Succès", msg)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Format invalide: {e}")
    
    def browse_file(self):
        """Ouvrir dialog parcours fichier"""
        path, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir fichier CSV", "", "CSV Files (*.csv);;All Files (*)"
        )
        if path:
            self.load_file(path)
    
    def load_file(self, filepath):
        """Charger fichier CSV"""
        try:
            data = np.genfromtxt(filepath, delimiter=',', skip_header=1)
            self.data = {
                'times': data[:, 0],
                'drawdowns': data[:, 1]
            }
            self.file_path_label.setText(f"✓ Fichier: {Path(filepath).name} ({len(data)} points)")
            logger.info(f"Fichier chargé: {filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lecture fichier: {e}")
    
    def validate_params(self):
        """Valider paramètres avec IA"""
        if self.data is None:
            QMessageBox.warning(self, "Attention", "Veuillez charger les données d'abord")
            return
        
        try:
            Q = self.Q_input.value()
            r = self.r_input.value()
            
            validator = PreComputeValidator()
            result = validator.validate_theis_parameters(
                Q=Q,
                T=1e-3,  # Estimation approximative
                S=1e-4,
                distance=r,
                time_max=self.data['times'].max()
            )
            
            status_color = {
                'OK': '#00aa00',
                'ATTENTION': '#ffaa00',
                'BLOQUÉ': '#cc0000'
            }
            
            text = f"""
<b>Status: {result['status']}</b> (Confiance: {result['confidence_score']:.0f}%)
<hr>
<b>Paramètres:</b>
• Q = {Q:.2e} m³/s
• r = {r} m
• Temps max = {self.data['times'].max():.0f} s

<b>Résumé validation:</b>
"""
            
            for issue in result['issues']:
                text += f"❌ {issue}\n"
            for warning in result['warnings']:
                text += f"⚠️  {warning}\n"
            
            if not result['issues'] and not result['warnings']:
                text += "✓ Tous les paramètres sont cohérents"
            
            self.validation_text.setText(text)
            
        except Exception as e:
            logger.error(f"Erreur validation: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur validation: {e}")
    
    def run_analysis(self):
        """Exécuter analyse"""
        if self.data is None:
            QMessageBox.warning(self, "Attention", "Veuillez charger les données")
            return
        
        try:
            Q = self.Q_input.value()
            r = self.r_input.value()
            method = self.method_combo.currentText()
            
            # Lancer analyse
            if "Theis" in method:
                analysis = theis.TheisAnalysis(
                    Q=Q,
                    distance=r,
                    times=self.data['times'],
                    drawdowns=self.data['drawdowns']
                )
            else:
                analysis = cooper_jacob.CooperJacobAnalysis(
                    Q=Q,
                    distance=r,
                    times=self.data['times'],
                    drawdowns=self.data['drawdowns']
                )
            
            self.result = analysis.fit()
            
            # Afficher résultats
            results_text = f"""
<b>Résultats - {method}</b>
<hr>
<b>Paramètres hydrauliques:</b>
• Transmissivité (T) = {self.result['T']:.2e} m²/s
• Emmagasinement (S) = {self.result['S']:.2e}

<b>Qualité ajustement:</b>
• RMSE = {self.result.get('rmse', 'N/A')}
• R² = {self.result.get('r_squared', 'N/A')}

<b>Données:</b>
• Points mesurés: {len(self.data['times'])}
• Rabattement min: {self.data['drawdowns'].min():.4f} m
• Rabattement max: {self.data['drawdowns'].max():.4f} m
"""
            self.results_text.setText(results_text)
            
            # Tracer courbe
            self.plot_results(analysis, method)
            
            logger.info(f"Analyse complétée: T={self.result['T']:.2e}, S={self.result['S']:.2e}")
            
        except Exception as e:
            logger.error(f"Erreur analyse: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur analyse: {e}")
    
    def plot_results(self, analysis, method):
        """Tracer courbes résultats - Style Fiflo Hydro"""
        self.figure.clear()
        self.figure.patch.set_facecolor('#ffffff')
        
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#f8f9fa')
        
        # Données mesurées
        ax.scatter(self.data['times'], self.data['drawdowns'], 
                  s=80, color='#e74c3c', label='Mesures', 
                  zorder=3, edgecolors='#c0392b', linewidth=1.5, alpha=0.8)
        
        # Courbe théorique
        # Générer t_range pour la courbe lissée
        t_min = self.data['times'].min()
        t_max = self.data['times'].max()
        t_range = np.logspace(np.log10(t_min), np.log10(t_max), 100)
        
        curve = analysis.generate_curve(T=analysis.T, S=analysis.S, t_range=t_range)
        ax.plot(curve['time'], curve['drawdown'], 
               color='#3498db', linewidth=2.5, label='Ajustement',
               zorder=2, alpha=0.9)
        
        # Styling
        ax.set_xlabel('Temps (s)', fontsize=11, fontweight='bold', color='#2c3e50')
        ax.set_ylabel('Rabattement (m)', fontsize=11, fontweight='bold', color='#2c3e50')
        ax.set_xscale('log')
        
        # Grille épurée
        ax.grid(True, alpha=0.2, linestyle='--', color='#bdc3c7', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # Legend
        legend = ax.legend(loc='upper left', fontsize=10, framealpha=0.95,
                          edgecolor='#bdc3c7', fancybox=True, shadow=False)
        legend.get_frame().set_facecolor('#ffffff')
        
        # Titre
        ax.set_title(f'📊 Essai de pompage - {method}', 
                    fontsize=12, fontweight='bold', color='#2c3e50', pad=15)
        
        # Spines
        for spine in ax.spines.values():
            spine.set_edgecolor('#bdc3c7')
            spine.set_linewidth(1)
        
        ax.tick_params(colors='#2c3e50', labelsize=9)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_empty_graph(self):
        """Tracer graphe vide avec instructions"""
        self.figure.clear()
        self.figure.patch.set_facecolor('#ffffff')
        
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#f8f9fa')
        
        # Message
        ax.text(0.5, 0.6, '📊 Graphe vide', 
               ha='center', va='center', fontsize=14, fontweight='bold',
               color='#95a5a6', transform=ax.transAxes)
        
        ax.text(0.5, 0.45, 'Chargez des données pour afficher le graphe',
               ha='center', va='center', fontsize=10, color='#7f8c8d',
               transform=ax.transAxes, style='italic')
        
        ax.text(0.5, 0.3, 'Options:\n• 📝 Saisie manuelle\n• 📂 Import CSV\n• 📊 Exemple Theis',
               ha='center', va='center', fontsize=9, color='#34495e',
               transform=ax.transAxes, 
               bbox=dict(boxstyle='round', facecolor='#ecf0f1', alpha=0.8))
        
        # Désactiver axes
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    
    def load_example(self, example_type):
        """Charger données d'exemple"""
        try:
            from app.data.io_manager import get_example_data
            
            times, drawdowns = get_example_data(example_type)
            
            self.data = {
                'times': times,
                'drawdowns': drawdowns
            }
            
            msg = f"✓ Exemple {example_type} chargé: {len(times)} points"
            self.file_path_label.setText(f"Example: {example_type}")
            logger.info(msg)
            QMessageBox.information(self, "Succès", msg)
        except Exception as e:
            logger.error(f"Erreur chargement exemple: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible charger exemple: {e}")
    
    def export_csv(self):
        """Exporter résultats en CSV"""
        if self.data is None:
            QMessageBox.warning(self, "Attention", "Pas de données à exporter")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(self, "Exporter CSV", "", "CSV (*.csv)")
        if filepath:
            try:
                success, error = DataIOManager.save_csv(
                    filepath,
                    self.data['times'],
                    self.data['drawdowns'],
                    headers=['time(s)', 'drawdown(m)']
                )
                if success:
                    QMessageBox.information(self, "Succès", f"Fichier exporté:\n{filepath}")
                else:
                    QMessageBox.critical(self, "Erreur", error)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")
    
    def export_pdf(self):
        """Exporter rapport PDF"""
        if self.result is None:
            QMessageBox.warning(self, "Attention", "Pas de résultats à exporter")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(self, "Exporter PDF", "", "PDF (*.pdf)")
        if filepath:
            try:
                success, error = DataIOManager.export_pdf(
                    filepath,
                    self.result,
                    title=f"Analyse Essai de Pompage - {self.method_combo.currentText()}"
                )
                if success:
                    QMessageBox.information(self, "Succès", f"PDF exporté:\n{filepath}")
                else:
                    QMessageBox.warning(self, "Avertissement", error)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur export PDF: {e}")
            try:
                # À implémenter: créer rapport PDF
                QMessageBox.information(self, "Succès", "Rapport généré")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")
