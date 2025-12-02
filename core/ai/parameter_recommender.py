"""
Recommandeur de paramètres - Module IA
======================================

Suggère plages plausibles de paramètres hydrogéologiques
basé sur contexte géologique (lithologie, profondeur, région).

Pédagogique : explique pourquoi cette plage est recommandée.
"""

import numpy as np
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ParameterRecommender:
    """
    Suggère paramètres hydrogéologiques avec justifications pédagogiques.
    """
    
    # Base de données simplifiée de plages typiques par lithologie
    LITHOLOGY_DATABASE = {
        'graviers': {
            'K_ms': (1e-2, 1e-3),  # m/s
            'porosite': (0.30, 0.45),
            'storage': (1e-3, 1e-2),
            'description': 'Formation très perméable (aquifère libre)'
        },
        'sables': {
            'K_ms': (1e-3, 1e-5),
            'porosite': (0.25, 0.40),
            'storage': (1e-3, 1e-4),
            'description': 'Aquifère libre typique'
        },
        'silt_limon': {
            'K_ms': (1e-5, 1e-7),
            'porosite': (0.35, 0.50),
            'storage': (1e-4, 1e-5),
            'description': 'Formation semi-perméable, aquitard'
        },
        'argile': {
            'K_ms': (1e-7, 1e-9),
            'porosite': (0.40, 0.60),
            'storage': (1e-5, 1e-6),
            'description': 'Formation imperméable, confinage'
        },
        'calcaire_fissure': {
            'K_ms': (1e-4, 1e-7),
            'porosite': (0.05, 0.20),
            'storage': (1e-5, 1e-4),
            'description': 'Karst ou calcaire fissure'
        },
        'granite_fissure': {
            'K_ms': (1e-6, 1e-9),
            'porosite': (0.01, 0.05),
            'storage': (1e-6, 1e-5),
            'description': 'Rocher dur avec fissures'
        },
    }
    
    def __init__(self):
        self.recommendations = {}
        
    def recommend_from_lithology(self, lithology: str) -> Dict:
        """
        Recommande paramètres basés sur lithologie.
        
        Args:
            lithology (str): Type de roche/sol
            
        Returns:
            Dict avec plages recommandées et explications
        """
        if lithology not in self.LITHOLOGY_DATABASE:
            return {
                'success': False,
                'error': f"Lithologie '{lithology}' inconnue",
                'available': list(self.LITHOLOGY_DATABASE.keys())
            }
        
        db = self.LITHOLOGY_DATABASE[lithology]
        
        K_min, K_max = db['K_ms']
        K_mid = (K_min + K_max) ** 0.5  # Moyenne géométrique
        
        return {
            'success': True,
            'lithology': lithology,
            'description': db['description'],
            'K_ms': {
                'min': K_min,
                'max': K_max,
                'typical': K_mid,
                'unit': 'm/s'
            },
            'K_md': {
                'min': K_min * 86400,
                'max': K_max * 86400,
                'typical': K_mid * 86400,
                'unit': 'm/day'
            },
            'porosity': {
                'min': db['porosite'][0],
                'max': db['porosite'][1],
                'unit': 'fraction',
                'percent': {
                    'min': db['porosite'][0] * 100,
                    'max': db['porosite'][1] * 100,
                    'unit': '%'
                }
            },
            'storage_coefficient': {
                'min': db['storage'][0],
                'max': db['storage'][1],
                'unit': 'dimensionless'
            },
            'explanation': f"""
Recommandation pour {lithology.upper()}
{'='*40}

Type d'aquifère: {db['description']}

Paramètres typiques :
  • Conductivité K: {K_min:.2e} - {K_max:.2e} m/s
                    ({K_min*86400:.2e} - {K_max*86400:.2e} m/jour)
  • Porosité: {db['porosite'][0]*100:.0f} - {db['porosite'][1]*100:.0f}%
  • Coefficient emmagasinement: {db['storage'][0]:.2e} - {db['storage'][1]:.2e}

Conseil pédagogique:
  → Utiliser la valeur typique pour les calculs préalables
  → Tester la sensibilité avec min et max
  → Affiner avec mesures in situ (Lefranc, Lugeon, Theis)
            """
        }
    
    def recommend_from_measured_data(self, measured_values: Dict) -> Dict:
        """
        Suggère paramètres inconnus à partir de mesures partielles.
        
        Args:
            measured_values: Dict ex. {'K_ms': 1e-4, 'lithology': 'sables'}
            
        Returns:
            Dict avec estimations des paramètres manquants
        """
        recommendations = {}
        explanations = []
        
        # Si K est connu, estimer les autres
        if 'K_ms' in measured_values and measured_values['K_ms'] is not None:
            K = measured_values['K_ms']
            
            # Estimer lithologie probable
            lithology_guess = self._guess_lithology_from_k(K)
            recommendations['lithology_guess'] = lithology_guess
            explanations.append(f"✓ Basé sur K={K:.2e} m/s → lithologie probable: {lithology_guess}")
            
            # Estimer porosité
            if 'porosity' not in measured_values:
                porosity_guess = self._estimate_porosity_from_k(K)
                recommendations['porosity_guess'] = porosity_guess
                explanations.append(f"✓ Porosité estimée: {porosity_guess*100:.1f}%")
        
        # Si lithologie est connue, recommander K, porosité, S
        if 'lithology' in measured_values and measured_values['lithology'] is not None:
            litho_rec = self.recommend_from_lithology(measured_values['lithology'])
            if litho_rec['success']:
                recommendations['from_lithology'] = litho_rec
                explanations.append(f"✓ Plages basées sur lithologie: {measured_values['lithology']}")
        
        return {
            'recommendations': recommendations,
            'explanations': explanations,
            'confidence': self._compute_confidence(measured_values)
        }
    
    def _guess_lithology_from_k(self, K_ms: float) -> str:
        """Estime lithologie probable à partir de K."""
        K = K_ms
        
        if K > 1e-3:
            return 'graviers'
        elif K > 1e-5:
            return 'sables'
        elif K > 1e-7:
            return 'silt_limon'
        elif K > 1e-9:
            return 'argile'
        else:
            return 'roche_massive'
    
    def _estimate_porosity_from_k(self, K_ms: float) -> float:
        """Estime porosité moyenne à partir de K (corrélation empirique)."""
        # Corrélation simplifiée
        if K_ms > 1e-3:
            return 0.38
        elif K_ms > 1e-5:
            return 0.32
        elif K_ms > 1e-7:
            return 0.42
        else:
            return 0.05
    
    def _compute_confidence(self, measured_values: Dict) -> float:
        """Calcule confiance en recommandations (0-100)."""
        if measured_values.get('K_ms'):
            return 85
        elif measured_values.get('lithology'):
            return 70
        else:
            return 40


def get_lithology_list() -> Dict[str, str]:
    """Retourne liste lithologies disponibles."""
    return {
        k: v['description']
        for k, v in ParameterRecommender.LITHOLOGY_DATABASE.items()
    }
