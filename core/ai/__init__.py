"""
Module IA - Assistant Pédagogique pour HydroAI
==============================================

L'IA n'est PAS un moteur de calcul. Elle accompagne l'utilisateur :

1. DÉTECTION D'ANOMALIES - Identifier les données aberrantes
2. COMPLÉTION - Suggérer valeurs manquantes avec confiance
3. RECOMMANDATIONS - Guider choix de paramètres
4. VALIDATION PRÉ-CALCUL - Vérifier cohérence avant simulation
5. EXPLICATION - Justifier recommandations (pédagogie)
"""

from .anomaly_detection import AnomalyDetector
from .parameter_recommender import ParameterRecommender
from .validation_engine import PreComputeValidator

__all__ = [
    'AnomalyDetector',
    'ParameterRecommender',
    'PreComputeValidator',
]
