"""
Module Cooper-Jacob - Approximation semi-log de Theis
======================================================

Implémente la méthode de Cooper-Jacob (1946) pour essais de pompage.
Valide pour u < 0.05, permet une analyse graphique simple via linéarisation semi-log.

Utilisée en pratique car plus simple que Theis pour les temps tardifs.

Références:
- Cooper, H.H. & Jacob, C.E. (1946). "A generalized graphical method for 
  evaluating formation constants and summarizing well-field history"
"""

import numpy as np
from scipy.optimize import curve_fit, linear_sum_assignment
from typing import Tuple, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class CooperJacobAnalysis:
    """
    Analyse Cooper-Jacob (approximation semi-log de Theis).
    
    Valide pour :
        u = r²*S / (4*T*t) < 0.05
        
    Équation : s ≈ (Q / 4πT) * [ln(2.25*T*t / (r²*S))]
              = (Q / 4πT) * ln(t) + cte
    """
    
    def __init__(self, Q: float, distance: float, times: np.ndarray, drawdowns: np.ndarray):
        """
        Initialise l'analyse Cooper-Jacob.
        
        Args:
            Q (float): Débit de pompage (m³/s)
            distance (float): Distance puits-piézomètre (m)
            times (np.ndarray): Temps (s)
            drawdowns (np.ndarray): Rabattements (m)
        """
        self.Q = Q
        self.distance = distance
        self.times = np.asarray(times, dtype=float)
        self.drawdowns = np.asarray(drawdowns, dtype=float)
        
        self.T = None
        self.S = None
        self.slope = None  # Pente de la droite (Δs / Δlog(t))
        self.intercept = None
        self.t0 = None  # Temps d'intersection (s = 0)
        self.rmse = None
        self.validity_range = None  # (t_min, t_max) pour u < 0.05
        
    def cooper_jacob_linear(self, log10_t: np.ndarray, slope: float, intercept: float) -> np.ndarray:
        """
        Fonction linéaire en log10(t).
        
        s = slope * log10(t) + intercept
        """
        return slope * log10_t + intercept
    
    def fit_linear(self) -> Dict:
        """
        Estime T et S par ajustement linéaire semi-log.
        
        La droite s = a*log10(t) + b permet de calculer :
            T = Q / (4π * a)  où a = slope (m)
            S = 2.25 * T * t0 / r²  où t0 est trouvé par extrapolation à s=0
            
        Returns:
            Dict avec T, S, rmse, parameters
        """
        
        # Ajustement linéaire : s = slope * log10(t) + intercept
        log10_t = np.log10(self.times)
        
        # Fit linéaire
        try:
            coeffs = np.polyfit(log10_t, self.drawdowns, 1)
            self.slope = coeffs[0]  # Δs / Δlog10(t)
            self.intercept = coeffs[1]
        except Exception as e:
            logger.error(f"Erreur lors du fit linéaire: {e}")
            return {'success': False, 'error': str(e)}
        
        # Calcul de T
        # s = (Q / 4πT) * ln(t) + cte
        # En log10 : s = (Q / 4π*T*ln(10)) * log10(t)
        # Donc : slope = Q / (4π * T * ln(10))
        # D'où : T = Q / (4π * slope * ln(10))
        self.T = self.Q / (4 * np.pi * self.slope * np.log(10))
        
        # Calcul du temps d'intersection (s = 0)
        # 0 = slope * log10(t0) + intercept
        # log10(t0) = -intercept / slope
        log10_t0 = -self.intercept / self.slope
        self.t0 = 10 ** log10_t0
        
        # Calcul de S : S = 2.25 * T * t0 / r²
        self.S = (2.25 * self.T * self.t0) / (self.distance ** 2)
        
        # Validation : vérifier que u < 0.05 pour au moins 50% des points
        u_values = (self.distance**2 * self.S) / (4 * self.T * self.times)
        valid_points = np.sum(u_values < 0.05)
        validity = valid_points / len(self.times)
        
        self.validity_range = (np.min(self.times[u_values < 0.05]),
                               np.max(self.times[u_values < 0.05]))
        
        # Résidus
        s_calc = self.cooper_jacob_linear(log10_t, self.slope, self.intercept)
        self.residuals = self.drawdowns - s_calc
        self.rmse = np.sqrt(np.mean(self.residuals**2))
        
        logger.info(f"Cooper-Jacob: T={self.T:.2e} m²/s, S={self.S:.2e}, "
                    f"RMSE={self.rmse:.4f} m, validity={validity*100:.1f}%")
        
        return {
            'T': self.T,
            'S': self.S,
            'rmse': self.rmse,
            'slope': self.slope,
            'intercept': self.intercept,
            't0': self.t0,
            'validity_percentage': validity * 100,
            'validity_range': self.validity_range,
            'success': True
        }
    
    def generate_curve(self, t_range: np.ndarray) -> Dict:
        """Génère la courbe Cooper-Jacob pour une plage de temps."""
        if self.slope is None:
            raise ValueError("Fit linéaire non effectué. Appelez fit_linear() d'abord.")
        
        log10_t = np.log10(t_range)
        s = self.cooper_jacob_linear(log10_t, self.slope, self.intercept)
        
        u_values = (self.distance**2 * self.S) / (4 * self.T * t_range)
        
        return {
            'time': t_range,
            'drawdown': s,
            'u': u_values,
            'log10_time': log10_t,
            'T': self.T,
            'S': self.S,
            'slope': self.slope
        }
    
    def get_summary(self) -> str:
        """Résumé texte des résultats."""
        if self.T is None:
            return "Analyse non effectuée"
        
        return f"""
Résultats Cooper-Jacob
======================
Débit (Q):                 {self.Q:.2e} m³/s
Distance (r):              {self.distance:.2f} m
Transmissivité (T):        {self.T:.2e} m²/s
Coefficient emmagasinement: {self.S:.2e}
Pente (Δs/Δlog₁₀t):        {self.slope:.4f} m
Temps d'intersection (t₀): {self.t0:.2e} s
RMSE:                      {self.rmse:.4f} m
Validité (u<0.05):         {self.validity_range[0]:.2e} - {self.validity_range[1]:.2e} s
        """


def cooper_jacob_drawdown(Q: float, T: float, S: float, distance: float, time: float) -> float:
    """
    Approximation semi-log pour le rabattement.
    
    s ≈ (Q / 4πT) * ln(2.25*T*t / (r²*S))
    """
    term = (2.25 * T * time) / (distance**2 * S)
    return (Q / (4 * np.pi * T)) * np.log(term)


def estimate_transmissivity_cooper_jacob(Q: float, distance: float, times: np.ndarray,
                                          drawdowns: np.ndarray) -> Tuple[float, float]:
    """
    Estime T et S via Cooper-Jacob.
    
    Returns:
        (T, S)
    """
    analysis = CooperJacobAnalysis(Q, distance, times, drawdowns)
    result = analysis.fit_linear()
    if result['success']:
        return result['T'], result['S']
    else:
        raise ValueError(f"Fit échoué: {result.get('error', 'Erreur inconnue')}")
