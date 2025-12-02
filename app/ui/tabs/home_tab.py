#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Onglet d'accueil - Présentation HydroAI
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGroupBox, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap


class HomeTab(QWidget):
    """Onglet d'accueil avec présentation et guide rapide"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Titre principal
        title = QLabel("Bienvenue dans HydroAI")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel(
            "Plateforme pédagogique pour modélisation hydrogéologique\n"
            "Outil scientifique rigoreux + Assistant IA"
        )
        subtitle_font = QFont()
        subtitle_font.setPointSize(11)
        subtitle_font.setItalic(True)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #666666;")
        layout.addWidget(subtitle)
        
        # Ligne de séparation
        separator = QLabel("-" * 60)
        separator.setStyleSheet("color: #cccccc;")
        layout.addWidget(separator)
        
        # Scroll area pour contenu
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Section 1 : Modules disponibles
        modules_group = QGroupBox("📦 Modules disponibles")
        modules_layout = QGridLayout(modules_group)
        
        modules = [
            ("💧 Essais de Pompage", "Theis & Cooper-Jacob pour aquifères confinés"),
            ("🔬 Tests de Perméabilité", "Lefranc, Lugeon, Porchet pour K"),
            ("📊 Piézométrie", "Analyse séries temporelles niveaux d'eau"),
            ("🤖 Assistant IA", "Validation, anomalies, recommandations"),
        ]
        
        for i, (title, desc) in enumerate(modules):
            title_label = QLabel(title)
            title_label.setStyleSheet("font-weight: bold; color: #0066cc;")
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("color: #666666;")
            
            modules_layout.addWidget(title_label, i, 0)
            modules_layout.addWidget(desc_label, i, 1)
        
        scroll_layout.addWidget(modules_group)
        
        # Section 2 : Guide rapide
        guide_group = QGroupBox("🚀 Guide rapide")
        guide_layout = QVBoxLayout(guide_group)
        
        steps = [
            "1️⃣  Sélectionner le test à analyser (Theis, Lefranc, etc.)",
            "2️⃣  Importer données CSV ou saisir manuellement",
            "3️⃣  Consulter l'IA pour recommandations de paramètres",
            "4️⃣  Valider les paramètres (status OK/ATTENTION/BLOQUÉ)",
            "5️⃣  Exécuter le calcul et visualiser résultats",
            "6️⃣  Exporter rapport PDF ou données CSV",
        ]
        
        for step in steps:
            step_label = QLabel(step)
            step_label.setStyleSheet("padding: 5px; border-left: 3px solid #0066cc;")
            guide_layout.addWidget(step_label)
        
        scroll_layout.addWidget(guide_group)
        
        # Section 3 : Ressources
        resources_group = QGroupBox("📚 Ressources")
        resources_layout = QVBoxLayout(resources_group)
        
        resources_text = QLabel(
            "📖 Documentation complète : ARCHITECTURE.md\n"
            "📋 Guide étudiant avec cas d'étude : GUIDE_ETUDIANT.py\n"
            "⚙️  Configuration : requirements.txt\n"
            "💡 Pour toute question : voir onglet 'Aide'"
        )
        resources_text.setStyleSheet("color: #333333; line-height: 1.6;")
        resources_layout.addWidget(resources_text)
        
        scroll_layout.addWidget(resources_group)
        
        # Section 4 : Version
        version_group = QGroupBox("ℹ️  Informations")
        version_layout = QVBoxLayout(version_group)
        
        info_text = QLabel(
            "Version : 0.1.0-alpha (MVP)\n"
            "Statut : En développement actif\n"
            "Licence : MIT\n"
            "Basée sur : Theis (1935), Cooper-Jacob (1946), etc."
        )
        info_text.setStyleSheet("color: #666666; font-size: 9pt;")
        version_layout.addWidget(info_text)
        
        scroll_layout.addWidget(version_group)
        
        # Stretch pour remplir
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Boutons d'action en bas
        button_layout = QHBoxLayout()
        
        btn_start = QPushButton("▶ Commencer (Essais Pompage)")
        btn_start.setMinimumHeight(40)
        btn_start.setStyleSheet("""
            QPushButton {
                background-color: #00aa00;
                color: white;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #008800;
            }
        """)
        btn_start.clicked.connect(lambda: self.parent().setCurrentIndex(1))
        button_layout.addWidget(btn_start)
        
        btn_docs = QPushButton("📖 Documentation")
        btn_docs.setMinimumHeight(40)
        button_layout.addWidget(btn_docs)
        
        layout.addLayout(button_layout)
