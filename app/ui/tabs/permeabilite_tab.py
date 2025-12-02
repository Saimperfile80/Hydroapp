#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Onglet Perméabilité - Lefranc, Lugeon, Porchet
"""

import numpy as np
import logging

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QDoubleSpinBox, QGroupBox, QGridLayout, QTextEdit, QTabWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)


class PermeabiliteTab(QWidget):
    """Onglet pour tests de perméabilité"""
    
    def __init__(self):
        super().__init__()
        self.test_type = "Lefranc"
        self.result = None
        self.init_ui()
    
    def get_data(self):
        """Retourner les données actuelles (pour simulation)"""
        test_type = self.test_combo.currentText()
        
        data = {
            'test_type': test_type,
        }
        
        # Récupérer paramètres selon le type de test
        try:
            if test_type == "Lefranc":
                data['radius'] = self.r_input.value()
                data['length'] = self.L_input.value()
                data['tau'] = self.tau_input.value()
                data['q'] = self.q_input.value()
            elif test_type == "Lugeon":
                data['stages'] = int(self.stages_input.value())
                data['pressure'] = self.pressure_input.value()
                data['flow'] = self.flow_input.value()
            elif test_type == "Porchet":
                data['radius'] = self.r_input.value()
                data['depth'] = self.depth_input.value()
                data['time'] = self.time_input.value()
        except:
            pass
        
        # Ajouter résultat si disponible
        if self.result:
            data['permeability'] = self.result.get('k', None)
        
        return data
    
    def init_ui(self):
        """Initialiser interface"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Sélection type test
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Type de test:"))
        
        self.test_combo = QComboBox()
        self.test_combo.addItems(["Lefranc", "Lugeon", "Porchet"])
        self.test_combo.currentTextChanged.connect(self.on_test_changed)
        selector_layout.addWidget(self.test_combo)
        selector_layout.addStretch()
        
        layout.addLayout(selector_layout)
        
        # Paramètres test
        self.params_group = QGroupBox("⚙️  Paramètres du test")
        self.params_layout = QGridLayout(self.params_group)
        layout.addWidget(self.params_group)
        
        # Zone résultats
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(QLabel("📊 Résultats"))
        layout.addWidget(self.results_text, 1)
        
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
        
        # Initialiser avec Lefranc
        self.on_test_changed("Lefranc")
    
    def on_test_changed(self, test_name):
        """Gérer changement de test"""
        
        # Nettoyer layout
        for i in reversed(range(self.params_layout.count())):
            self.params_layout.itemAt(i).widget().setParent(None)
        
        if test_name == "Lefranc":
            self.setup_lefranc_params()
        elif test_name == "Lugeon":
            self.setup_lugeon_params()
        else:  # Porchet
            self.setup_porchet_params()
    
    def setup_lefranc_params(self):
        """Paramètres Lefranc"""
        self.params_layout.addWidget(QLabel("Rayon forage (m):"), 0, 0)
        self.r_input = QDoubleSpinBox()
        self.r_input.setValue(0.05)
        self.params_layout.addWidget(self.r_input, 0, 1)
        
        self.params_layout.addWidget(QLabel("Longueur zone d'essai (m):"), 1, 0)
        self.L_input = QDoubleSpinBox()
        self.L_input.setValue(1.0)
        self.params_layout.addWidget(self.L_input, 1, 1)
        
        self.params_layout.addWidget(QLabel("Constante de temps τ (s):"), 2, 0)
        self.tau_input = QDoubleSpinBox()
        self.tau_input.setValue(100)
        self.params_layout.addWidget(self.tau_input, 2, 1)
    
    def setup_lugeon_params(self):
        """Paramètres Lugeon"""
        self.params_layout.addWidget(QLabel("Longueur zone d'essai (m):"), 0, 0)
        self.L_input = QDoubleSpinBox()
        self.L_input.setValue(1.0)
        self.params_layout.addWidget(self.L_input, 0, 1)
        
        self.params_layout.addWidget(QLabel("Perméabilité moyenne (m/s):"), 1, 0)
        self.K_input = QDoubleSpinBox()
        self.K_input.setMinimum(1e-9)
        self.K_input.setMaximum(1e-2)
        self.K_input.setValue(1e-6)
        self.K_input.setDecimals(9)
        self.params_layout.addWidget(self.K_input, 1, 1)
    
    def setup_porchet_params(self):
        """Paramètres Porchet"""
        self.params_layout.addWidget(QLabel("Rayon puits (m):"), 0, 0)
        self.r_input = QDoubleSpinBox()
        self.r_input.setValue(0.3)
        self.params_layout.addWidget(self.r_input, 0, 1)
        
        self.params_layout.addWidget(QLabel("Hauteur initiale eau (m):"), 1, 0)
        self.H0_input = QDoubleSpinBox()
        self.H0_input.setValue(1.0)
        self.params_layout.addWidget(self.H0_input, 1, 1)
        
        self.params_layout.addWidget(QLabel("Temps observation (s):"), 2, 0)
        self.t_max_input = QDoubleSpinBox()
        self.t_max_input.setValue(3600)
        self.params_layout.addWidget(self.t_max_input, 2, 1)
    
    def run_analysis(self):
        """Exécuter analyse"""
        test = self.test_combo.currentText()
        
        if test == "Lefranc":
            result = self.analyze_lefranc()
        elif test == "Lugeon":
            result = self.analyze_lugeon()
        else:
            result = self.analyze_porchet()
        
        if result:
            self.display_results(result, test)
    
    def analyze_lefranc(self):
        """Analyser test Lefranc"""
        try:
            from core.calculations import lefranc
            
            r = self.r_input.value()
            L = self.L_input.value()
            tau = self.tau_input.value()
            
            test = lefranc.LeffrancTest(1.0)
            K = test.calculate_permeability(tau, radius=r, length=L)
            
            return {
                'K_ms': K,
                'K_day': K * 86400,
                'tau': tau,
                'r': r,
                'L': L
            }
        except Exception as e:
            logger.error(f"Erreur Lefranc: {e}")
            return None
    
    def analyze_lugeon(self):
        """Analyser test Lugeon"""
        try:
            from core.calculations import lugeon
            
            L = self.L_input.value()
            K = self.K_input.value()
            
            test = lugeon.LugeonTest(L)
            lugeons = K / 1e-7  # Conversion en Lugeons
            
            return {
                'K_ms': K,
                'lugeons': lugeons,
                'L': L
            }
        except Exception as e:
            logger.error(f"Erreur Lugeon: {e}")
            return None
    
    def analyze_porchet(self):
        """Analyser test Porchet"""
        try:
            from core.calculations import porchet
            
            r = self.r_input.value()
            H0 = self.H0_input.value()
            
            test = porchet.PorchetTest(r)
            # À implémenter: calcul K à partir H0 et t
            
            return {
                'r': r,
                'H0': H0,
                'comment': 'Analyse simplifiée - Voir GUIDE_ETUDIANT.py pour exemple complet'
            }
        except Exception as e:
            logger.error(f"Erreur Porchet: {e}")
            return None
    
    def display_results(self, result, test_name):
        """Afficher résultats - Style Fiflo Hydro"""
        
        html = f"""
        <html>
        <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #2c3e50; }}
            .header {{ background-color: #3498db; color: white; padding: 10px; border-radius: 4px; }}
            .section {{ margin: 10px 0; padding: 8px; background-color: #f8f9fa; border-left: 3px solid #3498db; }}
            .value {{ color: #e74c3c; font-weight: bold; }}
            .unit {{ color: #7f8c8d; font-size: 0.9em; }}
        </style>
        </head>
        <body>
        <div class="header"><h3>🔬 Résultats - {test_name}</h3></div>
        """
        
        if test_name == "Lefranc":
            html += f"""
        <div class="section">
            <b>Perméabilité:</b><br>
            K = <span class="value">{result['K_ms']:.2e}</span> <span class="unit">m/s</span><br>
            K = <span class="value">{result['K_day']:.2e}</span> <span class="unit">m/jour</span>
        </div>
        <div class="section">
            <b>Paramètres du test:</b><br>
            • Rayon forage: {result['r']} m<br>
            • Longueur zone: {result['L']} m<br>
            • Constante temps (τ): {result['tau']} s
        </div>
        """
        elif test_name == "Lugeon":
            html += f"""
        <div class="section">
            <b>Perméabilité:</b><br>
            K = <span class="value">{result['K_ms']:.2e}</span> <span class="unit">m/s</span><br>
            <span class="value">{result['lugeons']:.1f}</span> <span class="unit">Lugeons</span>
        </div>
        <div class="section">
            <b>Paramètres:</b><br>
            • Longueur zone: {result['L']} m
        </div>
        """
        else:  # Porchet
            html += f"""
        <div class="section">
            <b>Test Porchet:</b><br>
            • Rayon puits: {result['r']} m<br>
            • Hauteur initiale: {result['H0']} m<br>
            • Note: {result['comment']}
        </div>
        """
        
        html += "</body></html>"
        self.results_text.setHtml(html)
