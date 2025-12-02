"""
Module Porchet - Test de perméabilité pour formations meubles
==============================================================

Test Porchet (ou "perméabilité de Porchet") utilisé pour estimé K
dans les formations superficielles non consolidées (sables, graviers, limons).

Principe : creuser un puits peu profond, remplir d'eau, mesurer la
vitesse de baisse du niveau avec le temps.

References:
- Porchet, G. (1991). Diagraphies et essais en forage
- Baize, D. (2000). Petit traité de pédologie des sols
"""

import numpy as np
from scipy.optimize import curve_fit
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PorchetTest:
    """
    Test Porchet pour formation meuble (graviers, sables).
    
    Équation générale :
        dH/dt = -(2*K / r) * sqrt(H)  où r = rayon du puits
        
    Solution analytique (hypothèse géométrie cylindrique):
        H(t) = [H0*sqrt(H0) - (3*K/r)*t]^(2/3)
    """
    
    def __init__(self, radius_m: float, initial_head_m: float):
        """
        Args:
            radius_m (float): Rayon du puits (m)
            initial_head_m (float): Hauteur d'eau initiale (m)
        """
        self.radius = radius_m
        self.initial_head = initial_head_m
        self.times = None
        self.heads = None
        self.K = None
        self.K_unit = 'm/s'
        
    def _porchet_analytical(self, t: np.ndarray, K: float) -> np.ndarray:
        """
        Solution analytique Porchet.
        
        H(t) = [sqrt(H0)^2 - (3*K/r)*t]^(2/3)  *approximativement*
        
        Pour simplification numérique :
        H(t) = (H0^(2/3) - (2*K/r)*t)^(3/2)
        """
        H0_2_3 = self.initial_head ** (2.0/3.0)
        coeff = 2 * K / self.radius
        term = H0_2_3 - coeff * t
        
        # Éviter racine de nombre négatif
        term = np.maximum(term, 0)
        return term ** (3.0/2.0)
    
    def fit(self, times: np.ndarray, heads: np.ndarray) -> Dict:
        """
        Estime K par ajustement à la courbe Porchet.
        
        Args:
            times (np.ndarray): Temps (s)
            heads (np.ndarray): Hauteurs d'eau (m)
            
        Returns:
            Dict avec K, rmse, parameters
        """
        self.times = np.asarray(times, dtype=float)
        self.heads = np.asarray(heads, dtype=float)
        
        try:
            # Fit avec K comme paramètre
            params, _ = curve_fit(
                self._porchet_analytical,
                self.times,
                self.heads,
                p0=[1e-4],  # Initialisation K
                maxfev=2000,
                bounds=(1e-7, 1e-2)
            )
            self.K = params[0]
        except Exception as e:
            logger.error(f"Fit Porchet échoué: {e}")
            return {'success': False, 'error': str(e)}
        
        # Résidus
        h_calc = self._porchet_analytical(self.times, self.K)
        residuals = self.heads - h_calc
        rmse = np.sqrt(np.mean(residuals**2))
        
        logger.info(f"Porchet: K={self.K:.2e} m/s, RMSE={rmse:.4f} m")
        
        return {
            'K': self.K,
            'K_unit': 'm/s',
            'rmse': rmse,
            'success': True,
            'params': {
                'radius': self.radius,
                'initial_head': self.initial_head,
                'num_points': len(self.times)
            }
        }
    
    def generate_curve(self, t_range: np.ndarray) -> Dict:
        """Génère la courbe théorique."""
        if self.K is None:
            raise ValueError("Fit non effectué")
        
        h = self._porchet_analytical(t_range, self.K)
        return {
            'time': t_range,
            'head': h,
            'K': self.K,
            'radius': self.radius
        }
    
    def get_summary(self) -> str:
        """Résumé texte."""
        if self.K is None:
            return "Test non effectué"
        
        return f"""
Résultats Test Porchet
=====================
Rayon du puits (r):   {self.radius:.3f} m
Charge initiale (H₀): {self.initial_head:.3f} m
Perméabilité (K):     {self.K:.2e} m/s
Perméabilité:         {self.K*86400:.2e} m/jour
Nombre de points:     {len(self.times)}
        """


def porchet_permeability(times: np.ndarray, heads: np.ndarray,
                         radius: float) -> float:
    """
    Estime K Porchet.
    
    Args:
        times: Temps (s)
        heads: Hauteurs d'eau (m)
        radius: Rayon puits (m)
        
    Returns:
        K (m/s)
    """
    test = PorchetTest(radius, heads[0])
    result = test.fit(times, heads)
    if result['success']:
        return result['K']
    else:
        raise ValueError(result['error'])
