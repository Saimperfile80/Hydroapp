#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HydroAI Main Application (PySide6)
Plateforme pedagogique pour modelisation hydrogeologique

Modules integres:
- Essais de pompage (Theis, Cooper-Jacob)
- Tests de permeabilite (Lefranc, Lugeon, Porchet)
- Analyse piezo metrique
- Assistant IA (validation, recommandations, anomalies)
"""

import sys
import logging
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QFileDialog, QMessageBox, QSplitter, QComboBox,
    QGroupBox, QSlider, QSpinBox, QDoubleSpinBox, QCheckBox, QScrollArea
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QIcon, QFont

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import tempfile
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import tabs
from app.ui.tabs.home_tab import HomeTab
from app.ui.tabs.essais_pompage_tab import EssaisPompageTab
from app.ui.tabs.permeabilite_tab import PermeabiliteTab
from app.ui.tabs.piezo_tab import PiezoTab
from app.ui.tabs.projets_tab import ProjetsTab


class FifloSimulationWindow(QMainWindow):
    """Fenetre de simulation style Fiflo - plein ecran avec menu lateral"""
    
    def __init__(self, simulation_type, parent=None):
        super().__init__(parent)
        
        self.simulation_type = simulation_type
        self.parent_app = parent
        
        # Camera controls
        self.azim = 30
        self.elev = 20
        self.zoom = 1.0
        
        # Récupérer les données de l'onglet actif du parent
        self.student_data = self._fetch_student_data()
        
        self.setup_window()
    
    def _fetch_student_data(self):
        """Récupérer les données étudiantes de l'onglet actif"""
        if not self.parent_app:
            return None
        
        try:
            # Récupérer l'onglet actif
            if hasattr(self.parent_app, 'tab_widget'):
                current_tab = self.parent_app.tab_widget.currentWidget()
                
                # Appeler get_data() si disponible
                if hasattr(current_tab, 'get_data'):
                    data = current_tab.get_data()
                    if data:
                        logger.info(f"Données étudiantes récupérées pour {self.simulation_type}")
                        return data
        except Exception as e:
            logger.warning(f"Impossible de récupérer données étudiantes: {e}")
        
        return None
    
    def setup_window(self):
        """Configurer la fenetre style Fiflo"""
        self.setWindowTitle(f"HydroAI - Simulation {self.simulation_type} (Fiflo Mode)")
        self.setGeometry(100, 100, 1800, 1000)
        
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ===== MENU GAUCHE (Style Fiflo) =====
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 25)  # 25% de largeur
        
        # Separateur
        separator = QWidget()
        separator.setFixedWidth(2)
        separator.setStyleSheet("background-color: #cccccc;")
        main_layout.addWidget(separator)
        
        # ===== VISUALISATIONS CENTRALES (Onglets) =====
        self.view_tabs_center = QTabWidget()
        self.view_tabs_center.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 20px;
                margin-right: 2px;
                border: 1px solid #999;
            }
            QTabBar::tab:selected {
                background-color: #0066cc;
                color: white;
                font-weight: bold;
            }
        """)
        
        # Onglet 1: 3D Surface
        self.figure_3d = Figure(figsize=(12, 8), dpi=100, facecolor='white')
        self.canvas_3d = FigureCanvas(self.figure_3d)
        self.view_tabs_center.addTab(self.canvas_3d, "3D Surface")
        
        # Onglet 2: Rabattement 2D
        self.figure_2d = Figure(figsize=(12, 8), dpi=100, facecolor='white')
        self.canvas_2d = FigureCanvas(self.figure_2d)
        self.view_tabs_center.addTab(self.canvas_2d, "Rabattement 2D")
        
        # Onglet 3: Piézométrie
        self.figure_piezo = Figure(figsize=(12, 8), dpi=100, facecolor='white')
        self.canvas_piezo = FigureCanvas(self.figure_piezo)
        self.view_tabs_center.addTab(self.canvas_piezo, "Piézométrie")
        
        # Onglet 4: Coupe Verticale
        self.figure_coupe = Figure(figsize=(12, 8), dpi=100, facecolor='white')
        self.canvas_coupe = FigureCanvas(self.figure_coupe)
        self.view_tabs_center.addTab(self.canvas_coupe, "Coupe Verticale")
        
        # Connection du changement d'onglet
        self.view_tabs_center.currentChanged.connect(self.on_view_changed)
        
        main_layout.addWidget(self.view_tabs_center, 75)  # 75% de largeur
        
        # Style
        self.apply_stylesheet()
        
        # Afficher visualisations initiales
        self.update_all_views()
    
    def on_view_changed(self, index):
        """Callback quand on change d'onglet"""
        if index == 0:
            self.update_3d_view()
        elif index == 1:
            self.plot_rabattement_2d()
        elif index == 2:
            self.plot_piezo_map()
        elif index == 3:
            self.plot_coupe_verticale()
    
    def update_all_views(self):
        """Mettre a jour toutes les vues"""
        self.update_3d_view()
        self.plot_rabattement_2d()
        self.plot_piezo_map()
        self.plot_coupe_verticale()
    
    def create_left_panel(self):
        """Creer le menu lateral style Fiflo"""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget { background-color: #f5f5f5; }
            QGroupBox { 
                border: 1px solid #ddd; 
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QLabel { color: #333; font-size: 10px; }
            QSlider { height: 8px; }
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 5px 10px;
                margin-right: 2px;
            }
            QTabBar::tab:selected { background-color: #0066cc; color: white; }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # === Onglets de visualisation ===
        self.view_tabs = QTabWidget()
        self.view_tabs.addTab(self.create_3d_controls(), "3D Interaction")
        self.view_tabs.addTab(self.create_display_controls(), "Affichage")
        self.view_tabs.addTab(self.create_advanced_controls(), "Avance")
        self.view_tabs.addTab(self.create_actions_controls(), "Actions")
        
        layout.addWidget(self.view_tabs)
        
        return panel
    
    def create_3d_controls(self):
        """Controles d'interaction 3D"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Azimuth
        layout.addWidget(QLabel("Azimuth (Rotation Horizontale):"))
        self.slider_azim = QSlider(Qt.Horizontal)
        self.slider_azim.setMinimum(0)
        self.slider_azim.setMaximum(360)
        self.slider_azim.setValue(30)
        self.slider_azim.setTickPosition(QSlider.TicksBelow)
        self.slider_azim.setTickInterval(30)
        self.slider_azim.sliderMoved.connect(self.update_3d_view)
        self.slider_azim.setSliderPosition(30)
        layout.addWidget(self.slider_azim)
        
        self.spin_azim = QSpinBox()
        self.spin_azim.setMinimum(0)
        self.spin_azim.setMaximum(360)
        self.spin_azim.setValue(30)
        self.spin_azim.valueChanged.connect(lambda v: (self.slider_azim.setValue(v), self.update_3d_view()))
        layout.addWidget(self.spin_azim)
        
        # Elevation
        layout.addWidget(QLabel("Elevation (Inclinaison):"))
        self.slider_elev = QSlider(Qt.Horizontal)
        self.slider_elev.setMinimum(0)
        self.slider_elev.setMaximum(90)
        self.slider_elev.setValue(20)
        self.slider_elev.setTickPosition(QSlider.TicksBelow)
        self.slider_elev.setTickInterval(10)
        self.slider_elev.sliderMoved.connect(self.update_3d_view)
        self.slider_elev.setSliderPosition(20)
        layout.addWidget(self.slider_elev)
        
        self.spin_elev = QSpinBox()
        self.spin_elev.setMinimum(0)
        self.spin_elev.setMaximum(90)
        self.spin_elev.setValue(20)
        self.spin_elev.valueChanged.connect(lambda v: (self.slider_elev.setValue(v), self.update_3d_view()))
        layout.addWidget(self.spin_elev)
        
        # Distance Camera
        layout.addWidget(QLabel("Distance Camera (Zoom):"))
        self.slider_distance = QSlider(Qt.Horizontal)
        self.slider_distance.setMinimum(1)
        self.slider_distance.setMaximum(50)
        self.slider_distance.setValue(10)
        self.slider_distance.sliderMoved.connect(self.update_3d_view)
        layout.addWidget(self.slider_distance)
        
        # Vues presets
        layout.addWidget(QLabel("Vues Presets:"))
        btn_top = QPushButton("De Dessus (Z)")
        btn_top.clicked.connect(lambda: self.set_view(0, 90, 10))
        layout.addWidget(btn_top)
        
        btn_front = QPushButton("De Face (Y)")
        btn_front.clicked.connect(lambda: self.set_view(0, 0, 10))
        layout.addWidget(btn_front)
        
        btn_side = QPushButton("Laterale (X)")
        btn_side.clicked.connect(lambda: self.set_view(90, 0, 10))
        layout.addWidget(btn_side)
        
        btn_iso = QPushButton("Isometrique")
        btn_iso.clicked.connect(lambda: self.set_view(30, 20, 10))
        layout.addWidget(btn_iso)
        
        btn_45 = QPushButton("45 Degres")
        btn_45.clicked.connect(lambda: self.set_view(45, 45, 10))
        layout.addWidget(btn_45)
        
        layout.addStretch()
        return widget
    
    def create_display_controls(self):
        """Controles d'affichage"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Style de Surface:"))
        self.check_wireframe = QCheckBox("Mode Wireframe")
        self.check_wireframe.stateChanged.connect(self.update_3d_view)
        layout.addWidget(self.check_wireframe)
        
        self.check_contours = QCheckBox("Courbes d'Isochores/Isopiezes")
        self.check_contours.setChecked(True)
        self.check_contours.stateChanged.connect(self.update_3d_view)
        layout.addWidget(self.check_contours)
        
        self.check_alpha = QCheckBox("Transparence (Alpha)")
        self.check_alpha.setChecked(True)
        self.check_alpha.stateChanged.connect(self.update_3d_view)
        layout.addWidget(self.check_alpha)
        
        self.check_antialiased = QCheckBox("Anti-aliasing")
        self.check_antialiased.setChecked(True)
        self.check_antialiased.stateChanged.connect(self.update_3d_view)
        layout.addWidget(self.check_antialiased)
        
        layout.addWidget(QLabel("Palette de Couleur:"))
        self.combo_cmap = QComboBox()
        self.combo_cmap.addItems(['viridis', 'plasma', 'inferno', 'magma', 'cividis', 
                                  'twilight', 'twilight_shifted', 'terrain', 'RdYlBu_r', 
                                  'coolwarm', 'RdBu', 'ocean', 'summer'])
        self.combo_cmap.currentTextChanged.connect(self.update_3d_view)
        layout.addWidget(self.combo_cmap)
        
        layout.addWidget(QLabel("Eclairage:"))
        self.check_lighting = QCheckBox("Eclairage 3D")
        self.check_lighting.setChecked(True)
        layout.addWidget(self.check_lighting)
        
        layout.addStretch()
        return widget
    
    def create_advanced_controls(self):
        """Controles avances"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Resolution de la Grille:"))
        self.spin_resolution = QSpinBox()
        self.spin_resolution.setMinimum(10)
        self.spin_resolution.setMaximum(200)
        self.spin_resolution.setValue(100)
        self.spin_resolution.setSingleStep(10)
        self.spin_resolution.valueChanged.connect(self.update_3d_view)
        layout.addWidget(self.spin_resolution)
        
        layout.addWidget(QLabel("Nombre de Contours:"))
        self.spin_contours = QSpinBox()
        self.spin_contours.setMinimum(3)
        self.spin_contours.setMaximum(50)
        self.spin_contours.setValue(10)
        self.spin_contours.valueChanged.connect(self.update_3d_view)
        layout.addWidget(self.spin_contours)
        
        layout.addWidget(QLabel("Transparence Surface (%):"))
        self.slider_alpha = QSlider(Qt.Horizontal)
        self.slider_alpha.setMinimum(10)
        self.slider_alpha.setMaximum(100)
        self.slider_alpha.setValue(90)
        self.slider_alpha.sliderMoved.connect(self.update_3d_view)
        layout.addWidget(self.slider_alpha)
        
        self.check_colorbar = QCheckBox("Afficher Echelle de Couleur")
        self.check_colorbar.setChecked(True)
        self.check_colorbar.stateChanged.connect(self.update_3d_view)
        layout.addWidget(self.check_colorbar)
        
        self.check_grid = QCheckBox("Afficher Grille")
        self.check_grid.setChecked(True)
        self.check_grid.stateChanged.connect(self.update_3d_view)
        layout.addWidget(self.check_grid)
        
        layout.addStretch()
        return widget
    
    def create_actions_controls(self):
        """Controles d'actions"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        btn_refresh = QPushButton("Rafraichir")
        btn_refresh.clicked.connect(self.update_3d_view)
        layout.addWidget(btn_refresh)
        
        btn_export = QPushButton("Exporter PNG")
        btn_export.clicked.connect(self.export_png)
        layout.addWidget(btn_export)
        
        btn_reset = QPushButton("Reinitialiser Vue")
        btn_reset.clicked.connect(self.reset_view)
        layout.addWidget(btn_reset)
        
        # Affichage info
        layout.addWidget(QLabel("Information:"))
        self.label_info = QLabel("Vue: Isometrique\nResolution: 100x100")
        self.label_info.setStyleSheet("background-color: white; padding: 5px; border: 1px solid #ddd;")
        layout.addWidget(self.label_info)
        
        layout.addStretch()
        return widget
    
    def set_view(self, azim, elev):
        """Definir angle de vue predefini"""
        self.slider_azim.setValue(azim)
        self.slider_elev.setValue(elev)
        self.spin_azim.setValue(azim)
        self.spin_elev.setValue(elev)
        self.update_3d_view()
    
    def reset_view(self):
        """Reinitialiser la vue"""
        self.slider_azim.setValue(30)
        self.slider_elev.setValue(20)
        self.slider_distance.setValue(10)
        self.check_wireframe.setChecked(False)
        self.check_contours.setChecked(True)
        self.check_alpha.setChecked(True)
        self.combo_cmap.setCurrentText('viridis')
        self.spin_resolution.setValue(100)
        self.update_3d_view()
    
    def update_3d_view(self):
        """Mettre a jour la visualisation 3D avec parametres avances"""
        self.figure_3d.clear()
        
        # Recuperer les parametres
        wireframe = self.check_wireframe.isChecked()
        cmap = self.combo_cmap.currentText()
        azim = self.slider_azim.value()
        elev = self.slider_elev.value()
        distance = self.slider_distance.value()
        resolution = self.spin_resolution.value()
        num_contours = self.spin_contours.value()
        alpha = self.slider_alpha.value() / 100.0
        antialiased = self.check_antialiased.isChecked()
        show_colorbar = self.check_colorbar.isChecked()
        show_grid = self.check_grid.isChecked()
        
        # Creer grille 3D
        x = np.linspace(0, 1000, resolution)
        y = np.linspace(0, 1000, resolution)
        X, Y = np.meshgrid(x, y)
        
        # Generer donnees selon type de simulation
        if self.simulation_type == "Essais Pompage":
            puit_x, puit_y = 500, 500
            distance_puit = np.sqrt((X - puit_x)**2 + (Y - puit_y)**2)
            Z = 2.0 / (1 + distance_puit / 100)
            title = "Rabattement - Essai de Pompage Theis"
            zlabel = "Rabattement (m)"
        elif self.simulation_type == "Permeabilite":
            Z = 1e-4 * np.exp(-((X - 500)**2 + (Y - 500)**2) / 50000)
            title = "Champ de Permeabilite"
            zlabel = "Coefficient k (m/s)"
        elif self.simulation_type == "Piezometrie":
            Z = 150 - (X / 1000) * 5 - (Y / 1000) * 3
            title = "Elevation Piezometrique"
            zlabel = "Elevation (m NGF)"
        else:
            Z = np.sin(X/100) * np.cos(Y/100)
            title = "Visualisation 3D"
            zlabel = "Valeur"
        
        # Creer subplot 3D
        ax = self.figure_3d.add_subplot(111, projection='3d')
        
        if wireframe:
            ax.plot_wireframe(X, Y, Z, cmap=cmap, alpha=alpha, rstride=max(1, resolution//30), 
                            cstride=max(1, resolution//30), linewidth=0.5)
        else:
            surf = ax.plot_surface(X, Y, Z, cmap=cmap, alpha=alpha, edgecolor='none', 
                                  rstride=max(1, resolution//50), cstride=max(1, resolution//50), 
                                  antialiased=antialiased, linewidth=0)
        
        # Contours
        if self.check_contours.isChecked():
            ax.contour(X, Y, Z, levels=num_contours, colors='black', linewidths=0.3, alpha=0.3)
        
        # Colorbar
        if show_colorbar:
            try:
                cbar = self.figure_3d.colorbar(ax.collections[0] if not wireframe else ax.collections[0], 
                                           ax=ax, label=zlabel, pad=0.1, shrink=0.8)
            except:
                pass
        
        # Configuration axes
        ax.set_xlabel('X (m)', fontweight='bold', fontsize=10)
        ax.set_ylabel('Y (m)', fontweight='bold', fontsize=10)
        ax.set_zlabel(zlabel, fontweight='bold', fontsize=10)
        ax.set_title(title, fontweight='bold', fontsize=13, pad=20)
        
        # Grille
        if show_grid:
            ax.grid(True, alpha=0.3)
        else:
            ax.grid(False)
        
        # Appliquer rotation et distance camera
        ax.view_init(elev=elev, azim=azim)
        zoom_factor = 12 / distance
        ax.set_xlim([500 - 500*zoom_factor, 500 + 500*zoom_factor])
        ax.set_ylim([500 - 500*zoom_factor, 500 + 500*zoom_factor])
        
        # Mettre a jour label info
        self.label_info.setText(f"Vue: ({azim}°, {elev}°)\nResolution: {resolution}x{resolution}\nContours: {num_contours}")
        
        self.figure_3d.tight_layout()
        self.canvas_3d.draw()
    
    def plot_rabattement_2d(self):
        """Afficher carte 2D des rabattements"""
        self.figure_2d.clear()
        ax = self.figure_2d.add_subplot(111)
        
        # Generer grille
        x = np.linspace(0, 1000, 100)
        y = np.linspace(0, 1000, 100)
        X, Y = np.meshgrid(x, y)
        
        # Puits de pompage
        puit_x, puit_y = 500, 500
        distance = np.sqrt((X - puit_x)**2 + (Y - puit_y)**2)
        rabattement = 2.0 / (1 + distance / 100)
        
        # Afficher comme carte thermique
        im = ax.contourf(X, Y, rabattement, levels=20, cmap='RdYlBu_r', alpha=0.8)
        contours = ax.contour(X, Y, rabattement, levels=10, colors='black', linewidths=0.5, alpha=0.3)
        ax.clabel(contours, inline=True, fontsize=8, fmt='%.2f m')
        
        # Marquer le puits
        ax.plot(puit_x, puit_y, 'k*', markersize=20, label='Puits de pompage')
        
        # Colorbar
        cbar = self.figure_2d.colorbar(im, ax=ax, label='Rabattement (m)')
        
        ax.set_xlabel('Distance Est-Ouest (m)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Distance Nord-Sud (m)', fontsize=11, fontweight='bold')
        ax.set_title('Carte de Rabattement 2D', fontsize=13, fontweight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.2, linestyle='--')
        
        self.figure_2d.tight_layout()
        self.canvas_2d.draw()
    
    def plot_piezo_map(self):
        """Afficher carte piezometrique"""
        self.figure_piezo.clear()
        ax = self.figure_piezo.add_subplot(111)
        
        # Generer pente piezometrique
        x = np.linspace(0, 1000, 100)
        y = np.linspace(0, 1000, 100)
        X, Y = np.meshgrid(x, y)
        piezo = 150 - (X / 1000) * 5 - (Y / 1000) * 3
        
        # Afficher courbes d'isopiezes
        im = ax.contourf(X, Y, piezo, levels=15, cmap='terrain', alpha=0.8)
        contours = ax.contour(X, Y, piezo, levels=15, colors='blue', linewidths=0.8, alpha=0.6)
        ax.clabel(contours, inline=True, fontsize=8, fmt='%.1f m NGF')
        
        # Fleches de flux
        grad_x, grad_y = np.gradient(piezo)
        skip = 8
        ax.quiver(X[::skip, ::skip], Y[::skip, ::skip], -grad_x[::skip, ::skip], -grad_y[::skip, ::skip], 
                 alpha=0.5, scale=100, width=0.003, headwidth=4)
        
        cbar = self.figure_piezo.colorbar(im, ax=ax, label='Elevation Piezometrique (m NGF)')
        
        ax.set_xlabel('Distance Est-Ouest (m)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Distance Nord-Sud (m)', fontsize=11, fontweight='bold')
        ax.set_title('Carte Piezometrique avec Flux', fontsize=13, fontweight='bold')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.2, linestyle='--')
        
        self.figure_piezo.tight_layout()
        self.canvas_piezo.draw()
    
    def plot_coupe_verticale(self):
        """Afficher coupe verticale"""
        self.figure_coupe.clear()
        ax = self.figure_coupe.add_subplot(111)
        
        # Profondeur
        x = np.linspace(0, 1000, 100)
        z = np.linspace(-100, 0, 50)
        X, Z = np.meshgrid(x, z)
        
        # Concentration polluant
        pollution = 100 * np.exp(-((X - 300)**2 / 50000 + (Z + 20)**2 / 400))
        
        # Afficher coupe
        im = ax.contourf(X, Z, pollution, levels=20, cmap='hot_r', alpha=0.8)
        contours = ax.contour(X, Z, pollution, levels=8, colors='white', linewidths=0.5, alpha=0.5)
        
        # Zone saturee
        ax.axhline(y=-30, color='cyan', linewidth=3, linestyle='--', label='Nappe phreатique', alpha=0.7)
        ax.fill_between([0, 1000], -100, -30, color='cyan', alpha=0.1)
        
        cbar = self.figure_coupe.colorbar(im, ax=ax, label='Concentration (mg/L)')
        
        ax.set_xlabel('Distance Horizontale (m)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Profondeur (m)', fontsize=11, fontweight='bold')
        ax.set_title('Coupe Verticale - Panache de Pollution', fontsize=13, fontweight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.2, linestyle='--')
        
        self.figure_coupe.tight_layout()
        self.canvas_coupe.draw()
    
    def export_png(self):
        """Exporter la vue en PNG"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Exporter en PNG", "", "PNG Files (*.png)"
        )
        if filepath:
            # Exporter la figure de l'onglet actuellement visible
            current_index = self.view_tabs_center.currentIndex()
            if current_index == 0:
                self.figure_3d.savefig(filepath, dpi=300, bbox_inches='tight')
            elif current_index == 1:
                self.figure_2d.savefig(filepath, dpi=300, bbox_inches='tight')
            elif current_index == 2:
                self.figure_piezo.savefig(filepath, dpi=300, bbox_inches='tight')
            elif current_index == 3:
                self.figure_coupe.savefig(filepath, dpi=300, bbox_inches='tight')
            
            QMessageBox.information(self, "Succes", f"Image exportee:\n{filepath}")
    
    def apply_stylesheet(self):
        """Appliquer le theme professionnel"""
        stylesheet = """
        QMainWindow { background-color: #ffffff; }
        QPushButton {
            background-color: #0066cc;
            color: white;
            border: none;
            padding: 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 10px;
        }
        QPushButton:hover { background-color: #0052a3; }
        QPushButton:pressed { background-color: #003d7a; }
        """
        self.setStyleSheet(stylesheet)


class SimulationWindow(QMainWindow):
    """Fenetre de simulation independante avec graphique"""
    
    def __init__(self, simulation_type, parent=None):
        super().__init__(parent)
        
        self.simulation_type = simulation_type
        self.parent_app = parent
        self.setup_window()
    
    def setup_window(self):
        """Configurer la fenetre"""
        self.setWindowTitle("HydroAI - Simulation: " + self.simulation_type)
        self.setGeometry(150, 150, 1600, 900)
        
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Toolbar avec options
        toolbar_layout = QHBoxLayout()
        
        view_label = QLabel("Visualisation:")
        toolbar_layout.addWidget(view_label)
        
        self.view_combo = QComboBox()
        self.view_combo.addItems(["Rabattement 2D", "Vitesse 3D", "Piézométrie", "Coupe Verticale"])
        self.view_combo.currentTextChanged.connect(self.update_visualization)
        toolbar_layout.addWidget(self.view_combo)
        
        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)
        
        # Splitter: gauche = parametres, droite = visualisation
        splitter = QSplitter(Qt.Horizontal)
        
        # Panel gauche: widget de saisie des parametres
        self.sim_widget = self.create_tab_widget()
        splitter.addWidget(self.sim_widget)
        
        # Panel droit: visualisation interactive
        self.figure = Figure(figsize=(10, 8), dpi=100, facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        splitter.addWidget(self.canvas)
        
        # Taille par defaut: 35% gauche, 65% droite
        splitter.setStretchFactor(0, 35)
        splitter.setStretchFactor(1, 65)
        
        main_layout.addWidget(splitter)
        
        # Barre inferieure avec boutons
        btn_layout = QHBoxLayout()
        
        btn_run = QPushButton("▶ Lancer Simulation")
        btn_run.setMaximumWidth(180)
        btn_run.clicked.connect(self.run_simulation)
        btn_layout.addWidget(btn_run)
        
        btn_export = QPushButton("💾 Exporter PDF")
        btn_export.setMaximumWidth(150)
        btn_export.clicked.connect(self.export_results)
        btn_layout.addWidget(btn_export)
        
        btn_layout.addStretch()
        
        btn_close = QPushButton("Fermer")
        btn_close.setMaximumWidth(100)
        btn_close.clicked.connect(self.close)
        btn_layout.addWidget(btn_close)
        
        main_layout.addLayout(btn_layout)
        
        # Style
        self.apply_stylesheet()
    
    def update_visualization(self):
        """Mettre a jour la visualisation selon le choix"""
        view_type = self.view_combo.currentText()
        if view_type == "Rabattement 2D":
            self.plot_rabattement_2d()
        elif view_type == "Vitesse 3D":
            self.plot_vitesse_3d()
        elif view_type == "Piézométrie":
            self.plot_piezo_map()
        elif view_type == "Coupe Verticale":
            self.plot_coupe_verticale()
    
    def create_tab_widget(self):
        """Creer le widget d'onglet approprie"""
        if self.simulation_type == "Essais Pompage":
            return EssaisPompageTab()
        elif self.simulation_type == "Permeabilite":
            return PermeabiliteTab()
        elif self.simulation_type == "Piezometrie":
            return PiezoTab()
        else:
            return QLabel("Simulation inconnue")
    
    def run_simulation(self):
        """Lancer la simulation et afficher les resultats"""
        try:
            # Afficher la visualisation par defaut
            view_type = self.view_combo.currentText()
            self.update_visualization()
            logger.info(f"Simulation {self.simulation_type} lancee")
        except Exception as e:
            logger.error(f"Erreur simulation: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la simulation:\n{str(e)}")
    
    def get_data_from_tab(self):
        """Recuperer les donnees du tab actif"""
        try:
            if self.simulation_type == "Essais Pompage":
                # Recuperer depuis EssaisPompageTab
                if hasattr(self.sim_widget, 'data') and self.sim_widget.data:
                    return self.sim_widget.data
                # Ou extraire des widgets d'entree
                return self.extract_theis_data()
            elif self.simulation_type == "Permeabilite":
                return self.extract_permeabilite_data()
            elif self.simulation_type == "Piezometrie":
                return self.extract_piezo_data()
        except Exception as e:
            logger.warning(f"Donnees non disponibles: {e}")
            return None
    
    def extract_theis_data(self):
        """Extraire donnees Theis depuis les widgets"""
        data = {}
        try:
            # Essayer de recuperer les valeurs des inputs du tab
            if hasattr(self.sim_widget, 'data_table'):
                # Lire depuis le tableau de donnees
                table = self.sim_widget.data_table
                rows = table.rowCount()
                distances = []
                rabattements = []
                for row in range(rows):
                    try:
                        dist = float(table.item(row, 0).text())
                        rabat = float(table.item(row, 1).text())
                        distances.append(dist)
                        rabattements.append(rabat)
                    except:
                        pass
                if distances:
                    data['distances'] = np.array(distances)
                    data['rabattements'] = np.array(rabattements)
        except:
            pass
        return data if data else None
    
    def extract_permeabilite_data(self):
        """Extraire donnees permeabilite"""
        data = {}
        try:
            if hasattr(self.sim_widget, 'results_table'):
                table = self.sim_widget.results_table
                rows = table.rowCount()
                depths = []
                k_values = []
                for row in range(rows):
                    try:
                        depth = float(table.item(row, 0).text())
                        k = float(table.item(row, 3).text())  # Colonne k
                        depths.append(depth)
                        k_values.append(k)
                    except:
                        pass
                if depths:
                    data['depths'] = np.array(depths)
                    data['k_values'] = np.array(k_values)
        except:
            pass
        return data if data else None
    
    def extract_piezo_data(self):
        """Extraire donnees piezo"""
        data = {}
        try:
            if hasattr(self.sim_widget, 'piezo_table'):
                table = self.sim_widget.piezo_table
                rows = table.rowCount()
                x_coords = []
                z_coords = []
                for row in range(rows):
                    try:
                        x = float(table.item(row, 0).text())
                        z = float(table.item(row, 1).text())
                        x_coords.append(x)
                        z_coords.append(z)
                    except:
                        pass
                if x_coords:
                    data['x'] = np.array(x_coords)
                    data['z'] = np.array(z_coords)
        except:
            pass
        return data if data else None
    
    def plot_rabattement_2d(self):
        """Afficher carte 2D des rabattements (style Fiflo) avec vraies donnees"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Essayer de recuperer les donnees
        data = self.get_data_from_tab()
        
        if data and 'distances' in data and 'rabattements' in data:
            # Utiliser les vraies donnees de l'etudiant
            distances = data['distances']
            rabattements = data['rabattements']
            
            # Tracer les points observes
            ax.scatter(distances, rabattements, s=100, color='red', marker='o', 
                      label='Points observes', zorder=5, edgecolors='darkred', linewidth=1.5)
            
            # Courbe de tendance
            if len(distances) > 1:
                z = np.polyfit(np.log10(distances + 1), rabattements, 1)
                p = np.poly1d(z)
                x_fit = np.logspace(np.log10(distances.min()), np.log10(distances.max()), 100)
                y_fit = p(np.log10(x_fit + 1))
                ax.semilogx(x_fit, y_fit, 'b--', linewidth=2, label='Courbe ajustee', alpha=0.7)
            
            ax.scatter(distances, rabattements, s=100, color='red', marker='o', zorder=5)
            ax.set_xlabel('Distance (m)', fontsize=11, fontweight='bold')
            ax.set_ylabel('Rabattement (m)', fontsize=11, fontweight='bold')
            ax.set_title('Donnees Essai de Pompage - Theis', fontsize=13, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend(fontsize=10)
        else:
            # Afficher donnees synthétiques si pas de donnees reelles
            # Generer une grille de donnees
            x = np.linspace(0, 1000, 100)
            y = np.linspace(0, 1000, 100)
            X, Y = np.meshgrid(x, y)
            
            # Puits de pompage au centre
            puit_x, puit_y = 500, 500
            distance = np.sqrt((X - puit_x)**2 + (Y - puit_y)**2)
            
            # Rabattement (loi de Theis simplifie)
            rabattement = 2.0 / (1 + distance / 100) 
            rabattement[distance < 10] = 2.0
            
            # Afficher comme une carte thermique (colormap Fiflo-like)
            im = ax.contourf(X, Y, rabattement, levels=20, cmap='RdYlBu_r', alpha=0.8)
            contours = ax.contour(X, Y, rabattement, levels=10, colors='black', linewidths=0.5, alpha=0.3)
            ax.clabel(contours, inline=True, fontsize=8, fmt='%.2f m')
            
            # Marquer le puits
            ax.plot(puit_x, puit_y, 'k*', markersize=20, label='Puits de pompage')
            
            # Colorbar
            cbar = self.figure.colorbar(im, ax=ax, label='Rabattement (m)')
            ax.set_xlabel('Distance Est-Ouest (m)', fontsize=11, fontweight='bold')
            ax.set_ylabel('Distance Nord-Sud (m)', fontsize=11, fontweight='bold')
            ax.set_title('Carte de Rabattement - Essai de Pompage Theis (Exemple)', fontsize=13, fontweight='bold')
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.2, linestyle='--')
            ax.legend(loc='upper right', fontsize=10)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_vitesse_3d(self):
        """Afficher champ de vitesses 3D avec vraies donnees"""
        self.figure.clear()
        ax = self.figure.add_subplot(111, projection='3d')
        
        data = self.get_data_from_tab()
        
        if data and 'k_values' in data and 'depths' in data:
            # Utiliser donnees reelles
            depths = data['depths']
            k_values = data['k_values']
            
            # Creer grille 3D
            y_vals = np.arange(len(depths))
            x_vals = np.arange(10)
            X, Y = np.meshgrid(x_vals, y_vals)
            Z = np.tile(k_values[:, np.newaxis], (1, 10))
            
            surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
            ax.set_zlabel('Permeabilite (m/s)', fontweight='bold')
        else:
            # Donnees synthétiques
            x = np.linspace(0, 1000, 50)
            y = np.linspace(0, 1000, 50)
            X, Y = np.meshgrid(x, y)
            
            # Puits au centre
            puit_x, puit_y = 500, 500
            distance = np.sqrt((X - puit_x)**2 + (Y - puit_y)**2)
            
            # Vitesses radiales
            Z = 2.0 / (1 + distance / 100)
            
            # Plot 3D avec coloration
            surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8, edgecolor='none')
            ax.set_zlabel('Vitesse (m/jour)', fontweight='bold')
        
        ax.set_xlabel('X (m)', fontweight='bold')
        ax.set_ylabel('Y (m)', fontweight='bold')
        ax.set_title('Champ de Vitesses 3D', fontsize=13, fontweight='bold')
        
        self.figure.colorbar(surf, ax=ax, label='Valeur', pad=0.1)
        self.canvas.draw()
    
    def plot_piezo_map(self):
        """Afficher carte piezometrique avec vraies donnees"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        data = self.get_data_from_tab()
        
        if data and 'x' in data and 'z' in data:
            # Utiliser donnees reelles
            x_coords = data['x']
            z_coords = data['z']
            
            # Tracer les points
            ax.scatter(x_coords, z_coords, s=80, color='blue', marker='o', 
                      label='Points piezometriques', zorder=5, edgecolors='darkblue')
            
            # Ligne de tendance
            if len(x_coords) > 1:
                z_fit = np.polyfit(x_coords, z_coords, 1)
                p = np.poly1d(z_fit)
                x_line = np.linspace(x_coords.min(), x_coords.max(), 100)
                ax.plot(x_line, p(x_line), 'r--', linewidth=2, label='Gradient piezometrique', alpha=0.7)
            
            # Zone saturee
            z_min = z_coords.min() - 5
            ax.fill_between(x_coords, z_coords, z_min, alpha=0.2, color='cyan', label='Zone saturee')
            
            ax.set_xlabel('Distance (m)', fontsize=11, fontweight='bold')
            ax.set_ylabel('Elevation Piezometrique (m NGF)', fontsize=11, fontweight='bold')
            ax.set_title('Carte Piezometrique - Donnees Reelles', fontsize=13, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend(fontsize=10)
        else:
            # Donnees synthétiques
            x = np.linspace(0, 1000, 100)
            y = np.linspace(0, 1000, 100)
            X, Y = np.meshgrid(x, y)
            
            # Elevation piezometrique avec gradient
            piezo = 150 - (X / 1000) * 5 - (Y / 1000) * 3
            
            # Afficher les courbes d'isopiezes
            im = ax.contourf(X, Y, piezo, levels=15, cmap='terrain', alpha=0.8)
            contours = ax.contour(X, Y, piezo, levels=15, colors='blue', linewidths=0.8, alpha=0.6)
            ax.clabel(contours, inline=True, fontsize=8, fmt='%.1f m NGF')
            
            # Fleches de flux
            grad_x, grad_y = np.gradient(piezo)
            skip = 8
            ax.quiver(X[::skip, ::skip], Y[::skip, ::skip], -grad_x[::skip, ::skip], -grad_y[::skip, ::skip], 
                     alpha=0.5, scale=100, width=0.003, headwidth=4)
            
            cbar = self.figure.colorbar(im, ax=ax, label='Elevation Piezometrique (m NGF)')
            ax.set_xlabel('Distance Est-Ouest (m)', fontsize=11, fontweight='bold')
            ax.set_ylabel('Distance Nord-Sud (m)', fontsize=11, fontweight='bold')
            ax.set_title('Carte Piezometrique - Flux Souterrain (Exemple)', fontsize=13, fontweight='bold')
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.2, linestyle='--')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_coupe_verticale(self):
        """Afficher coupe verticale (cross-section) avec vraies donnees"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        data = self.get_data_from_tab()
        
        if data:
            # Si donnees, afficher coupe avec donnees reelles
            if 'depths' in data and 'k_values' in data:
                depths = data['depths']
                k_values = data['k_values']
                
                # Profondeurs negatives
                z_coords = -depths
                x_coords = np.arange(len(depths))
                
                ax.bar(x_coords, k_values, width=0.6, color='steelblue', alpha=0.7, edgecolor='black')
                ax.set_ylabel('Permeabilite (m/s)', fontsize=11, fontweight='bold')
                ax.set_xlabel('Profondeur (m)', fontsize=11, fontweight='bold')
                ax.set_yscale('log')
                ax.set_title('Coupe Verticale - Permeabilite en Profondeur', fontsize=13, fontweight='bold')
        else:
            # Donnees synthétiques
            x = np.linspace(0, 1000, 100)
            z = np.linspace(-100, 0, 50)
            X, Z = np.meshgrid(x, z)
            
            # Concentration polluant en coupe
            pollution = 100 * np.exp(-((X - 300)**2 / 50000 + (Z + 20)**2 / 400))
            
            # Afficher coupe
            im = ax.contourf(X, Z, pollution, levels=20, cmap='hot_r', alpha=0.8)
            contours = ax.contour(X, Z, pollution, levels=8, colors='white', linewidths=0.5, alpha=0.5)
            
            # Zone saturee
            ax.axhline(y=-30, color='cyan', linewidth=3, linestyle='--', label='Nappe phreатique', alpha=0.7)
            ax.fill_between([0, 1000], -100, -30, color='cyan', alpha=0.1)
            
            cbar = self.figure.colorbar(im, ax=ax, label='Concentration (mg/L)')
            ax.set_xlabel('Distance Horizontale (m)', fontsize=11, fontweight='bold')
            ax.set_ylabel('Profondeur (m)', fontsize=11, fontweight='bold')
            ax.set_title('Coupe Verticale - Panache de Pollution (Exemple)', fontsize=13, fontweight='bold')
            ax.legend(loc='upper right', fontsize=10)
        
        ax.grid(True, alpha=0.2, linestyle='--')
        self.figure.tight_layout()
        self.canvas.draw()
    
    def export_results(self):
        """Exporter les resultats"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Exporter resultats", "", "PDF (*.pdf);;PNG (*.png);;CSV (*.csv)"
        )
        if filepath:
            if filepath.endswith('.pdf') or filepath.endswith('.png'):
                self.figure.savefig(filepath, dpi=300, bbox_inches='tight')
            logger.info(f"Resultats exportes: {filepath}")
    
    def apply_stylesheet(self):
        """Appliquer le theme professionnel"""
        stylesheet = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        QWidget {
            background-color: #f5f5f5;
        }
        QPushButton {
            background-color: #0066cc;
            color: white;
            border: none;
            padding: 10px 16px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 11px;
        }
        QPushButton:hover {
            background-color: #0052a3;
        }
        QPushButton:pressed {
            background-color: #003d7a;
        }
        QLabel {
            color: #333333;
        }
        """
        self.setStyleSheet(stylesheet)


class HydroAIApp(QMainWindow):
    """Application principale HydroAI avec interface tabbed"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("HydroAI - Plateforme Hydrogeologique")
        self.setGeometry(100, 100, 1200, 800)
        
        # Fenetre de simulation ouverte
        self.sim_windows = {}
        
        # Appliquer stylesheet
        self.apply_stylesheet()
        
        # Creer interface
        self.init_ui()
        
        logger.info("Application HydroAI demarree")
    
    def apply_stylesheet(self):
        """Appliquer theme global"""
        stylesheet = """
        QMainWindow {
            background-color: #f0f0f0;
        }
        QTabWidget::pane {
            border: 1px solid #cccccc;
        }
        QTabBar::tab {
            background-color: #e0e0e0;
            color: #333333;
            padding: 8px 20px;
            margin-right: 2px;
            border: 1px solid #999999;
            border-bottom: none;
        }
        QTabBar::tab:selected {
            background-color: #ffffff;
            color: #0066cc;
            font-weight: bold;
        }
        QTabBar::tab:hover {
            background-color: #f5f5f5;
        }
        QPushButton {
            background-color: #0066cc;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #0052a3;
        }
        QPushButton:pressed {
            background-color: #003d7a;
        }
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            padding: 6px;
            border: 1px solid #cccccc;
            border-radius: 3px;
            background-color: #ffffff;
        }
        QLineEdit:focus, QComboBox:focus {
            border: 2px solid #0066cc;
        }
        QGroupBox {
            border: 2px solid #cccccc;
            border-radius: 4px;
            margin-top: 8px;
            padding-top: 8px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }
        """
        self.setStyleSheet(stylesheet)
    
    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Barre d'outils (titre)
        title_bar = QWidget()
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(20, 10, 20, 10)
        
        title_label = QLabel("HydroAI - Modelisation Hydrogeologique")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        version_label = QLabel("v0.1.0-alpha")
        version_label.setStyleSheet("color: #666666; font-size: 10px;")
        title_layout.addWidget(version_label)
        
        layout.addWidget(title_bar)
        
        # Barre de menu
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("Fichier")
        new_action = file_menu.addAction("Nouveau Projet")
        open_action = file_menu.addAction("Ouvrir Projet")
        save_action = file_menu.addAction("Sauvegarder")
        file_menu.addSeparator()
        exit_action = file_menu.addAction("Quitter")
        exit_action.triggered.connect(self.close)
        
        sim_menu = menu_bar.addMenu("Simulations")
        theis_action = sim_menu.addAction("Essais Pompage (Theis)")
        theis_action.triggered.connect(lambda: self.open_simulation_window("Essais Pompage"))
        
        perm_action = sim_menu.addAction("Permeabilite (Lefranc, Lugeon, Porchet)")
        perm_action.triggered.connect(lambda: self.open_simulation_window("Permeabilite"))
        
        piezo_action = sim_menu.addAction("Piezometrie")
        piezo_action.triggered.connect(lambda: self.open_simulation_window("Piezometrie"))
        
        help_menu = menu_bar.addMenu("Aide")
        about_action = help_menu.addAction("A propos")
        about_action.triggered.connect(self.show_about)
        
        # Toolbar
        toolbar = self.addToolBar("Main")
        
        btn_sim1 = QPushButton("Theis")
        btn_sim1.setMaximumWidth(100)
        btn_sim1.clicked.connect(lambda: self.open_simulation_window("Essais Pompage"))
        toolbar.addWidget(btn_sim1)
        
        btn_sim2 = QPushButton("Permeabilite")
        btn_sim2.setMaximumWidth(100)
        btn_sim2.clicked.connect(lambda: self.open_simulation_window("Permeabilite"))
        toolbar.addWidget(btn_sim2)
        
        btn_sim3 = QPushButton("Piezometrie")
        btn_sim3.setMaximumWidth(100)
        btn_sim3.clicked.connect(lambda: self.open_simulation_window("Piezometrie"))
        toolbar.addWidget(btn_sim3)
        
        # Onglets principaux
        self.tabs = QTabWidget()
        
        # Creer les onglets
        self.home_tab = HomeTab()
        self.essais_pompage_tab = EssaisPompageTab()
        self.permeabilite_tab = PermeabiliteTab()
        self.piezo_tab = PiezoTab()
        self.projets_tab = ProjetsTab()
        
        self.tabs.addTab(self.home_tab, "Accueil")
        self.tabs.addTab(self.essais_pompage_tab, "Essais Pompage")
        self.tabs.addTab(self.permeabilite_tab, "Permeabilite")
        self.tabs.addTab(self.piezo_tab, "Piezometrie")
        self.tabs.addTab(self.projets_tab, "Projets")
        
        layout.addWidget(self.tabs)
        
        # Barre d'etat
        self.status_label = QLabel("Pret")
        self.statusBar().addWidget(self.status_label)
    
    def open_simulation_window(self, sim_type):
        """Ouvrir une fenetre de simulation style Fiflo"""
        # Si la fenetre existe deja, la ramener au premier plan
        if sim_type in self.sim_windows:
            self.sim_windows[sim_type].raise_()
            self.sim_windows[sim_type].activateWindow()
        else:
            # Creer une nouvelle fenetre FIFLO
            sim_window = FifloSimulationWindow(sim_type, self)
            self.sim_windows[sim_type] = sim_window
            sim_window.show()
            
            # Supprimer de la liste quand fermee
            sim_window.destroyed.connect(lambda: self.sim_windows.pop(sim_type, None))
        
        self.update_status("Simulation: " + sim_type + " ouverte")
    
    def show_about(self):
        """Afficher dialog A propos"""
        QMessageBox.about(
            self,
            "A propos de HydroAI",
            "HydroAI v0.1.0-alpha\n\n"
            "Plateforme pedagogique pour modelisation hydrogeologique\n\n"
            "Modules scientifiques:\n"
            "- Theis (essais de pompage)\n"
            "- Lefranc, Lugeon, Porchet (permeabilite)\n"
            "- Analyse piezometrique\n\n"
            "Modules IA:\n"
            "- Detection d'anomalies\n"
            "- Recommandations de parametres\n"
            "- Validation pre-calcul\n\n"
            "2024-2025 HydroAI Project"
        )
    
    def update_status(self, message):
        """Mettre a jour message d'etat"""
        self.status_label.setText(message)
        QTimer.singleShot(3000, lambda: self.status_label.setText("Pret"))
    
    def closeEvent(self, event):
        """Fermer toutes les fenetres de simulation avant de quitter"""
        for window in list(self.sim_windows.values()):
            window.close()
        event.accept()


def main():
    """Point d'entree principal"""
    app = QApplication(sys.argv)
    
    window = HydroAIApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
