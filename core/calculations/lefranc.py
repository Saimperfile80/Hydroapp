"""
Module Lefranc - Test de perméabilité en sondage
================================================

Implémente le test Lefranc (1989) pour estimer la perméabilité K in situ.
Basé sur le principe de charge/décharge dans un tronçon de forage.

Test de charge : augmentation rapide du niveau et suivi de la baisse
Test de décharge : abaissement du niveau et suivi de la remontée

L'équation classique pour géométrie cylindrique:
    K = (Q / (I*A)) en régime permanent
où Q est le débit, I le gradient, A la surface de contact.

References:
- Lefranc, P. et al. (1991). "Soil and Rock Testing" - Chapter on permeability
"""

import numpy as np
from scipy.optimize import curve_fit
from typing import Tuple, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class LeffrancTest:
    """
    Test Lefranc pour estimation de perméabilité.
    
    Géométries supportées:
        - Cylindre fermé au fond (géométrie classique)
        - Packer test (test entre deux packers)
    """
    
    def __init__(self, initial_head: float, geometry: str = 'cylinder'):
        """
        Initialise un test Lefranc.
        
        Args:
            initial_head (float): Charge initiale dans le forage (m)
            geometry (str): Type de géométrie ('cylinder', 'packer')
        """
        self.initial_head = initial_head
        self.geometry = geometry
        self.times = None
        self.heads = None  # Charge h(t)
        self.K = None
        self.K_unit = 'm/s'
        
    def _exponential_decay(self, t: np.ndarray, h0: float, h_infty: float, tau: float) -> np.ndarray:
        """
        Modèle exponentiel : h(t) = h_infty + (h0 - h_infty) * exp(-t/tau)
        
        Pour un test en charge:
            h0 = charge initiale (élevée)
            h_infty = charge stationnaire (aquifère)
            tau = constante de temps
        """
        return h_infty + (h0 - h_infty) * np.exp(-t / tau)
    
    def fit_exponential(self, times: np.ndarray, heads: np.ndarray,
                        aquifer_head: Optional[float] = None) -> Dict:
        """
        Estime K par ajustement exponentiel.
        
        Args:
            times (np.ndarray): Temps (s)
            heads (np.ndarray): Charges mesurées (m)
            aquifer_head (float): Charge de l'aquifère (m) - auto-détection si None
            
        Returns:
            Dict avec K, tau, rmse
        """
        self.times = np.asarray(times, dtype=float)
        self.heads = np.asarray(heads, dtype=float)
        
        # Auto-détection charge stationnaire = dernière mesure
        if aquifer_head is None:
            aquifer_head = self.heads[-1]
        
        # Fit exponentiel
        try:
            params, _ = curve_fit(
                self._exponential_decay,
                self.times,
                self.heads,
                p0=[self.heads[0], aquifer_head, self.times[-1] / 10],
                maxfev=2000
            )
            h0, h_infty, tau = params
        except Exception as e:
            logger.error(f"Fit exponentiel échoué: {e}")
            return {'success': False, 'error': str(e)}
        
        # Calcul de K dépend de la géométrie
        if self.geometry == 'cylinder':
            # Pour un cylindre : K ≈ ln(2) * r² / (τ * L)
            # où r est le rayon du forage, L la longueur du tronçon actif
            # En pratique : K = 0.693 * r² / (τ * L)
            # Hypothèse : diamètre 50mm, longueur 2m (valeurs typiques)
            r = 0.025  # 50 mm -> 25 mm rayon
            L = 2.0
            self.K = (np.log(2) * r**2) / (tau * L)
        
        elif self.geometry == 'packer':
            # Pour test entre packers : K ≈ r_screen / (2 * τ * L)
            r_screen = 0.025  # Rayon écran
            L = 1.0  # Distance entre packers
            self.K = r_screen / (2 * tau * L)
        
        # Résidus
        h_calc = self._exponential_decay(self.times, h0, h_infty, tau)
        residuals = self.heads - h_calc
        rmse = np.sqrt(np.mean(residuals**2))
        
        logger.info(f"Lefranc: K={self.K:.2e} m/s, tau={tau:.2f} s, RMSE={rmse:.4f} m")
        
        return {
            'K': self.K,
            'K_unit': 'm/s',
            'tau': tau,
            'rmse': rmse,
            'h0': h0,
            'h_infty': h_infty,
            'success': True,
            'params': {
                'geometry': self.geometry,
                'num_points': len(self.times)
            }
        }
    
    def calculate_permeability(self, tau: float, radius: float = 0.025, length: float = 2.0) -> float:
        """
        Calcule K directement à partir de tau.
        
        Args:
            tau (float): Constante de temps (s)
            radius (float): Rayon forage (m)
            length (float): Longueur zone d'essai (m)
            
        Returns:
            float: Perméabilité K (m/s)
        """
        if self.geometry == 'cylinder':
            self.K = (np.log(2) * radius**2) / (tau * length)
        elif self.geometry == 'packer':
            self.K = radius / (2 * tau * length)
        return self.K
    
    def generate_curve(self, t_range: np.ndarray, h0: float, h_infty: float, tau: float) -> Dict:
        """Génère courbe théorique Lefranc."""
        h = self._exponential_decay(t_range, h0, h_infty, tau)
        return {
            'time': t_range,
            'head': h,
            'tau': tau,
            'K': self.K
        }
    
    def get_summary(self) -> str:
        """Résumé texte."""
        if self.K is None:
            return "Test non effectué"
        
        return f"""
Résultats Test Lefranc
=====================
Géométrie:            {self.geometry}
Perméabilité (K):     {self.K:.2e} m/s
Perméabilité:         {self.K*86400:.2e} m/jour
Nombre de points:     {len(self.times)}
        """


def lefranc_permeability(times: np.ndarray, heads: np.ndarray, 
                         geometry: str = 'cylinder', radius: float = 0.025) -> float:
    """
    Estime K Lefranc.
    
    Args:
        times: Temps (s)
        heads: Charges (m)
        geometry: 'cylinder' ou 'packer'
        radius: Rayon forage/écran (m)
        
    Returns:
        K (m/s)
    """
    test = LeffrancTest(heads[0], geometry)
    result = test.fit_exponential(times, heads)
    if result['success']:
        return result['K']
    else:
        raise ValueError(result['error'])
