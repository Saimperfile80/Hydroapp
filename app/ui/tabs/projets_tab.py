#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Onglet Gestion Projets - Sauvegarde, chargement, historique
"""

import logging
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QListWidget, QListWidgetItem, QMessageBox, QGroupBox, QGridLayout,
    QTextEdit, QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon

from app.project_manager import ProjectManager

logger = logging.getLogger(__name__)


class ProjectDialog(QDialog):
    """Dialog pour créer/éditer projet"""
    
    def __init__(self, parent=None, mode='create', project_name=''):
        super().__init__(parent)
        self.mode = mode
        self.project_name = project_name
        self.init_ui()
    
    def init_ui(self):
        """Initialiser UI"""
        layout = QVBoxLayout(self)
        
        # Titre
        if self.mode == 'create':
            self.setWindowTitle("Créer nouveau projet")
            title_text = "Nouveau projet"
        else:
            self.setWindowTitle(f"Éditer {self.project_name}")
            title_text = f"Éditer: {self.project_name}"
        
        layout.addWidget(QLabel(title_text))
        
        # Champs
        layout.addWidget(QLabel("Nom du projet:"))
        self.name_input = QLineEdit()
        if self.mode == 'edit':
            self.name_input.setText(self.project_name)
            self.name_input.setReadOnly(True)
        self.name_input.setPlaceholderText("Essai Toulon 2024")
        layout.addWidget(self.name_input)
        
        layout.addWidget(QLabel("Description:"))
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Pompage test dans nappe pliocène...")
        self.desc_input.setMaximumHeight(100)
        layout.addWidget(self.desc_input)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        if self.mode == 'create':
            btn_create = QPushButton("✓ Créer")
            btn_create.clicked.connect(self.accept)
            button_layout.addWidget(btn_create)
        else:
            btn_save = QPushButton("✓ Enregistrer")
            btn_save.clicked.connect(self.accept)
            button_layout.addWidget(btn_save)
        
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)
        
        layout.addLayout(button_layout)
    
    def get_data(self):
        """Retourner données"""
        return {
            'name': self.name_input.text(),
            'description': self.desc_input.toPlainText()
        }


class ProjetsTab(QWidget):
    """Onglet gestion projets"""
    
    def __init__(self):
        super().__init__()
        self.pm = ProjectManager("./projects")
        self.init_ui()
        self.refresh_projects()
    
    def init_ui(self):
        """Initialiser interface"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Titre
        title = QLabel("📁 Gestion des projets")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Boutons actions
        actions_layout = QHBoxLayout()
        
        btn_new = QPushButton("✨ Nouveau projet")
        btn_new.clicked.connect(self.create_project)
        actions_layout.addWidget(btn_new)
        
        btn_open = QPushButton("📂 Ouvrir")
        btn_open.clicked.connect(self.open_project)
        actions_layout.addWidget(btn_open)
        
        btn_delete = QPushButton("🗑️  Supprimer")
        btn_delete.clicked.connect(self.delete_project)
        actions_layout.addWidget(btn_delete)
        
        btn_export = QPushButton("💾 Exporter")
        btn_export.clicked.connect(self.export_project)
        actions_layout.addWidget(btn_export)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Liste projets
        self.project_list = QListWidget()
        self.project_list.itemClicked.connect(self.on_project_selected)
        layout.addWidget(QLabel("Projets:"))
        layout.addWidget(self.project_list)
        
        # Détails projet sélectionné
        details_group = QGroupBox("📊 Détails du projet")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        details_layout.addWidget(self.details_text)
        
        layout.addWidget(details_group)
    
    def refresh_projects(self):
        """Rafraîchir liste projets"""
        self.project_list.clear()
        
        success, projects, error = self.pm.list_projects()
        
        if not success:
            QMessageBox.warning(self, "Erreur", error or "Impossible charger projets")
            return
        
        if not projects:
            self.project_list.addItem("(Aucun projet - créez-en un!)")
            return
        
        for proj in projects:
            item = QListWidgetItem(f"📌 {proj['name']}")
            item.setData(Qt.UserRole, proj)
            self.project_list.addItem(item)
    
    def on_project_selected(self, item):
        """Afficher détails projet sélectionné"""
        proj = item.data(Qt.UserRole)
        if not proj:
            return
        
        text = f"""
<b>{proj['name']}</b>
Description: {proj.get('description', 'N/A')}
Créé: {proj['created_at'][:10]}
Modifié: {proj['modified_at'][:10]}
"""
        self.details_text.setText(text)
    
    def create_project(self):
        """Créer nouveau projet"""
        dialog = ProjectDialog(self, mode='create')
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            
            if not data['name'].strip():
                QMessageBox.warning(self, "Erreur", "Nom du projet requis")
                return
            
            success, error = self.pm.create_project(
                data['name'],
                data['description']
            )
            
            if success:
                QMessageBox.information(self, "Succès", f"Projet '{data['name']}' créé")
                self.refresh_projects()
            else:
                QMessageBox.critical(self, "Erreur", error)
    
    def open_project(self):
        """Ouvrir projet"""
        item = self.project_list.currentItem()
        if not item or not item.data(Qt.UserRole):
            QMessageBox.warning(self, "Attention", "Sélectionnez un projet")
            return
        
        proj = item.data(Qt.UserRole)
        success, data, error = self.pm.load_project(proj['name'])
        
        if success:
            text = f"<b>📂 {proj['name']}</b>\n"
            text += f"<hr>\n"
            text += f"<b>Analyses ({len(data['analyses'])}):</b>\n"
            for i, analysis in enumerate(data['analyses'][:5], 1):
                text += f"{i}. {analysis['method']} - {analysis['timestamp'][:10]}\n"
            
            self.details_text.setText(text)
            QMessageBox.information(self, "Succès", f"Projet ouvert: {proj['name']}\n\nSee details panel →")
        else:
            QMessageBox.critical(self, "Erreur", error)
    
    def delete_project(self):
        """Supprimer projet"""
        item = self.project_list.currentItem()
        if not item or not item.data(Qt.UserRole):
            QMessageBox.warning(self, "Attention", "Sélectionnez un projet")
            return
        
        proj = item.data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Supprimer le projet '{proj['name']}'?\nCette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, error = self.pm.delete_project(proj['name'])
            
            if success:
                QMessageBox.information(self, "Succès", "Projet supprimé")
                self.refresh_projects()
            else:
                QMessageBox.critical(self, "Erreur", error)
    
    def export_project(self):
        """Exporter projet"""
        item = self.project_list.currentItem()
        if not item or not item.data(Qt.UserRole):
            QMessageBox.warning(self, "Attention", "Sélectionnez un projet")
            return
        
        proj = item.data(Qt.UserRole)
        success, data, error = self.pm.load_project(proj['name'])
        
        if not success:
            QMessageBox.critical(self, "Erreur", error)
            return
        
        from PySide6.QtWidgets import QFileDialog
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Exporter projet", proj['name'] + ".json", "JSON (*.json)"
        )
        
        if filepath:
            success, error = ProjectManager.export_project(data, filepath)
            if success:
                QMessageBox.information(self, "Succès", f"Projet exporté:\n{filepath}")
            else:
                QMessageBox.critical(self, "Erreur", error)
