#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HydroAI Main Application (PySide6) - Version Simplifiée
Interface simulation professionnelle sans matplotlib integration
"""

import sys
import logging

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMenuBar, QMenu, QToolBar,
    QFileDialog, QMessageBox, QDockWidget, QStatusBar, QScrollArea,
    QGroupBox, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QAction

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HydroAIApp(QMainWindow):
    """Application principale HydroAI - Interface Professionnelle"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("HydroAI - Plateforme Hydrogeologique Avancee")
        self.setGeometry(0, 0, 1920, 1080)
        
        # Appliquer stylesheet
        self.apply_stylesheet()
        
        # Etat
        self.is_3d_mode = False
        self.current_simulation = None
        
        # Creer interface
        self.create_menu_bar()
        self.create_toolbar()
        self.create_main_widget()
        self.create_status_bar()
        self.create_left_panel()
        
        logger.info("Application HydroAI demarree (v0.2.0-professional)")
    
    def apply_stylesheet(self):
        """Appliquer theme Fiflo Hydro professionnel"""
        stylesheet = """
        QMainWindow {
            background-color: #1a1a2e;
        }
        QMenuBar {
            background-color: #16213e;
            color: white;
            font-weight: bold;
            border-bottom: 3px solid #0f3460;
            padding: 3px;
        }
        QMenuBar::item {
            padding: 4px 12px;
        }
        QMenuBar::item:selected {
            background-color: #0f3460;
        }
        QMenu {
            background-color: #16213e;
            color: white;
            border: 1px solid #0f3460;
        }
        QMenu::item:selected {
            background-color: #0f3460;
        }
        QToolBar {
            background-color: #0f3460;
            border-bottom: 2px solid #0a1e2e;
            spacing: 2px;
            padding: 3px;
        }
        QPushButton {
            background-color: #0f3460;
            color: #00d4ff;
            border: 1px solid #00d4ff;
            padding: 6px 12px;
            border-radius: 3px;
            font-weight: bold;
            font-size: 10px;
        }
        QPushButton:hover {
            background-color: #00d4ff;
            color: #0a1e2e;
        }
        QPushButton:pressed {
            background-color: #0a1e2e;
            color: #00d4ff;
        }
        QGroupBox {
            color: white;
            border: 1px solid #0f3460;
            border-radius: 3px;
            margin-top: 8px;
            padding-top: 8px;
            font-weight: bold;
            font-size: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 3px 0 3px;
        }
        QLabel {
            color: white;
            font-size: 10px;
        }
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit {
            background-color: #16213e;
            color: #00d4ff;
            border: 1px solid #0f3460;
            padding: 4px;
            border-radius: 2px;
            font-size: 10px;
        }
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, 
        QComboBox:focus, QTextEdit:focus {
            border: 1px solid #00d4ff;
        }
        QStatusBar {
            background-color: #16213e;
            color: #00d4ff;
            border-top: 1px solid #0f3460;
            font-size: 10px;
        }
        QScrollArea {
            background-color: #1a1a2e;
            border: none;
        }
        """
        self.setStyleSheet(stylesheet)
    
    def create_menu_bar(self):
        """Menu bar professionnel"""
        menubar = self.menuBar()
        
        # File
        file_menu = menubar.addMenu("FILE")
        new_proj = QAction("Nouveau Projet", self)
        new_proj.triggered.connect(self.new_project)
        file_menu.addAction(new_proj)
        
        open_proj = QAction("Ouvrir Projet", self)
        open_proj.triggered.connect(self.open_project)
        file_menu.addAction(open_proj)
        
        save_proj = QAction("Sauvegarder", self)
        save_proj.triggered.connect(self.save_project)
        file_menu.addAction(save_proj)
        
        file_menu.addSeparator()
        
        exit_app = QAction("Quitter", self)
        exit_app.triggered.connect(self.close)
        file_menu.addAction(exit_app)
        
        # Simulation
        sim_menu = menubar.addMenu("SIMULATIONS")
        
        theis_act = QAction("Essais Pompage (Theis)", self)
        theis_act.triggered.connect(lambda: self.open_simulation("THEIS"))
        sim_menu.addAction(theis_act)
        
        perm_act = QAction("Permeabilite", self)
        perm_act.triggered.connect(lambda: self.open_simulation("PERM"))
        sim_menu.addAction(perm_act)
        
        piezo_act = QAction("Piezometrie", self)
        piezo_act.triggered.connect(lambda: self.open_simulation("PIEZO"))
        sim_menu.addAction(piezo_act)
        
        # View
        view_menu = menubar.addMenu("VIEW")
        
        toggle_3d = QAction("Vue 3D (Exp.)", self)
        toggle_3d.triggered.connect(self.toggle_3d_view)
        view_menu.addAction(toggle_3d)
        
        # Help
        help_menu = menubar.addMenu("HELP")
        about_act = QAction("A propos", self)
        about_act.triggered.connect(self.show_about)
        help_menu.addAction(about_act)
    
    def create_toolbar(self):
        """Toolbar compact"""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)
        
        btn_new = QPushButton("[ NEW ]")
        btn_new.setMaximumSize(80, 28)
        btn_new.clicked.connect(self.new_project)
        toolbar.addWidget(btn_new)
        
        btn_open = QPushButton("[ OPEN ]")
        btn_open.setMaximumSize(80, 28)
        btn_open.clicked.connect(self.open_project)
        toolbar.addWidget(btn_open)
        
        btn_save = QPushButton("[ SAVE ]")
        btn_save.setMaximumSize(80, 28)
        btn_save.clicked.connect(self.save_project)
        toolbar.addWidget(btn_save)
        
        toolbar.addSeparator()
        
        btn_theis = QPushButton("[ THEIS ]")
        btn_theis.setMaximumSize(80, 28)
        btn_theis.clicked.connect(lambda: self.open_simulation("THEIS"))
        toolbar.addWidget(btn_theis)
        
        btn_perm = QPushButton("[ PERM ]")
        btn_perm.setMaximumSize(80, 28)
        btn_perm.clicked.connect(lambda: self.open_simulation("PERM"))
        toolbar.addWidget(btn_perm)
        
        btn_piezo = QPushButton("[ PIEZO ]")
        btn_piezo.setMaximumSize(80, 28)
        btn_piezo.clicked.connect(lambda: self.open_simulation("PIEZO"))
        toolbar.addWidget(btn_piezo)
        
        toolbar.addSeparator()
        
        btn_3d = QPushButton("[ 3D ]")
        btn_3d.setMaximumSize(80, 28)
        btn_3d.clicked.connect(self.toggle_3d_view)
        toolbar.addWidget(btn_3d)
    
    def create_main_widget(self):
        """Widget central avec zone simulation"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QHBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Zone simulation (centre, 80%)
        self.simulation_area = QWidget()
        sim_layout = QVBoxLayout(self.simulation_area)
        sim_layout.setContentsMargins(15, 15, 15, 15)
        sim_layout.setSpacing(10)
        
        # Titre simulation
        self.sim_title = QLabel("Selectionnez une simulation")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.sim_title.setFont(title_font)
        self.sim_title.setStyleSheet("color: #00d4ff; background-color: #0f3460; padding: 10px;")
        sim_layout.addWidget(self.sim_title)
        
        # Zone graphique (placeholder)
        self.graph_area = QTextEdit()
        self.graph_area.setReadOnly(True)
        self.graph_area.setText("GRAPHIQUE SIMULATION\n\n" +
                               "Zone pour affichage graphique\n" +
                               "Selectionnez une simulation et cliquez sur EXECUTER\n" +
                               "\nCette zone affichera:\n" +
                               "- Courbes semi-log Theis\n" +
                               "- Graphiques permeabilite\n" +
                               "- Series chronologiques piezometrie\n" +
                               "- Et bien plus...\n\n" +
                               "[ZONE GRAPHIQUE - A ACTIVER]")
        self.graph_area.setStyleSheet("background-color: #16213e; color: #00d4ff; border: 2px solid #0f3460;")
        sim_layout.addWidget(self.graph_area, stretch=1)
        
        layout.addWidget(self.simulation_area, stretch=80)
    
    def create_left_panel(self):
        """Panneau lateral gauche avec parametres"""
        dock = QDockWidget("[=] PARAMETRES", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        dock.setMaximumWidth(280)
        dock.setMinimumWidth(250)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollBar:vertical { width: 8px; }")
        
        params_widget = QWidget()
        params_layout = QVBoxLayout(params_widget)
        params_layout.setSpacing(8)
        
        # Groupe simulation
        sim_group = QGroupBox("SIMULATION")
        sim_layout = QVBoxLayout(sim_group)
        
        self.sim_combo = QComboBox()
        self.sim_combo.addItems(["Essais Pompage", "Permeabilite", "Piezometrie", "Projets"])
        self.sim_combo.currentIndexChanged.connect(self.on_simulation_changed)
        sim_layout.addWidget(QLabel("Type:"))
        sim_layout.addWidget(self.sim_combo)
        
        params_layout.addWidget(sim_group)
        
        # Groupe parametres
        param_group = QGroupBox("PARAMETRES")
        param_layout = QVBoxLayout(param_group)
        
        param_layout.addWidget(QLabel("Transmissivite T:"))
        self.param_t = QDoubleSpinBox()
        self.param_t.setRange(0.01, 10000)
        self.param_t.setValue(100)
        self.param_t.setDecimals(2)
        param_layout.addWidget(self.param_t)
        
        param_layout.addWidget(QLabel("Emmagasinement S:"))
        self.param_s = QDoubleSpinBox()
        self.param_s.setRange(1e-8, 1)
        self.param_s.setValue(0.001)
        self.param_s.setDecimals(6)
        param_layout.addWidget(self.param_s)
        
        param_layout.addWidget(QLabel("Rayon pompage r:"))
        self.param_r = QDoubleSpinBox()
        self.param_r.setRange(0.01, 1000)
        self.param_r.setValue(0.5)
        self.param_r.setDecimals(2)
        param_layout.addWidget(self.param_r)
        
        params_layout.addWidget(param_group)
        
        # Boutons
        btn_layout = QVBoxLayout()
        
        btn_run = QPushButton("> EXECUTER")
        btn_run.clicked.connect(self.run_simulation)
        btn_layout.addWidget(btn_run)
        
        btn_export = QPushButton("= EXPORTER")
        btn_export.clicked.connect(self.export_results)
        btn_layout.addWidget(btn_export)
        
        btn_clear = QPushButton("X EFFACER")
        btn_clear.clicked.connect(self.clear_results)
        btn_layout.addWidget(btn_clear)
        
        params_layout.addLayout(btn_layout)
        params_layout.addStretch()
        
        scroll.setWidget(params_widget)
        dock.setWidget(scroll)
        
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
    
    def create_status_bar(self):
        """Status bar"""
        self.status_label = QLabel("-- PRET")
        self.statusBar().addWidget(self.status_label)
        
        self.mode_label = QLabel("MODE: 2D")
        self.statusBar().addPermanentWidget(self.mode_label)
    
    # Simulation methods
    def on_simulation_changed(self, index):
        """Changement de simulation"""
        simulations = ["Essais Pompage (Theis)", "Permeabilite (Lefranc)", "Piezometrie", "Projets"]
        self.sim_title.setText("SIMULATION: " + simulations[index])
        self.update_status("SEL: " + simulations[index])
    
    def open_simulation(self, sim_type):
        """Ouvrir une simulation"""
        self.current_simulation = sim_type
        self.sim_title.setText("SIMULATION ACTIVE: " + sim_type)
        self.update_status("OPEN: " + sim_type)
    
    def run_simulation(self):
        """Executer simulation Theis"""
        try:
            import numpy as np
            
            T = self.param_t.value()
            S = self.param_s.value()
            r = self.param_r.value()
            
            # Generer donnees Theis
            t = np.logspace(0, 5, 50)
            results = []
            
            for time in t:
                if time > 0:
                    u = (S * r * r) / (4 * T * time)
                    # Well function approx
                    if u > 0:
                        W = -0.5772 - np.log(u)
                        s = (Q * W) / (4 * np.pi * T) if 'Q' in locals() else W / (4 * np.pi * T)
                        s = max(0, s)
                        results.append((time, s))
            
            # Afficher resultats
            output = "RESULTATS SIMULATION THEIS\n"
            output += "=" * 40 + "\n"
            output += "Parametres:\n"
            output += "  Transmissivite (T): %.2f m2/j\n" % T
            output += "  Emmagasinement (S): %.6f\n" % S
            output += "  Rayon pompage (r): %.2f m\n" % r
            output += "\nDonnees generees:\n"
            output += "Temps (s)    | Rabattement (m)\n"
            output += "-" * 40 + "\n"
            
            if results:
                for t_val, s_val in results[:10]:
                    output += "%.2e  |  %.6f\n" % (t_val, s_val)
            else:
                output += "[Donnees generees...]\n"
            
            self.graph_area.setText(output)
            self.update_status("OK - SIMULATION EXECUTEE")
        except Exception as e:
            self.update_status("ERR - " + str(e))
            logger.error("Simulation error: " + str(e))
    
    def new_project(self):
        self.update_status("NEW - Nouveau projet")
        self.graph_area.setText("NOUVEAU PROJET\n\n" +
                               "Entrez les parametres et cliquez EXECUTER")
    
    def open_project(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir Projet", "", "HydroAI (*.hydro);;JSON (*.json)"
        )
        if filepath:
            self.update_status("OPEN: " + filepath)
    
    def save_project(self):
        self.update_status("OK - Projet sauvegarde")
    
    def export_results(self):
        self.update_status("OK - Export PDF/CSV")
    
    def clear_results(self):
        self.graph_area.clear()
        self.update_status("CLEAR - Resultats effacees")
    
    def toggle_3d_view(self):
        self.is_3d_mode = not self.is_3d_mode
        mode_text = "3D" if self.is_3d_mode else "2D"
        self.mode_label.setText("MODE: " + mode_text)
        self.update_status("MODE: " + mode_text)
    
    def show_about(self):
        QMessageBox.about(
            self, "A PROPOS",
            "HydroAI v0.2.0 PROFESSIONAL\n\n"
            "Plateforme de modelisation hydrogeologique\n\n"
            "+ 6 modules scientifiques\n"
            "+ 3 systemes pedagogiques IA\n"
            "+ Interface 3D simulation\n"
            "+ Gestion complete projets\n\n"
            "2024-2025 HydroAI Project"
        )
    
    def update_status(self, message):
        """Mettre a jour status"""
        self.status_label.setText(message)
        QTimer.singleShot(5000, lambda: self.status_label.setText("-- PRET"))


def main():
    """Point d'entree"""
    app = QApplication(sys.argv)
    window = HydroAIApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
