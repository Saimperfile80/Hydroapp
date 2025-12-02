"""
Module Theis - Analyse d'essais de pompage en conditions transitoires
=====================================================================

Implémente la solution classique de Theis (1935) pour écoulement en milieu confiné.
Utilise la fonction de puits W(u) pour estimer la transmissivité T et le coefficient
d'emmagasinement S à partir des données de rabattement mesuré en fonction du temps.

Références :
- Theis, C.V. (1935). "The relation between the lowering of the piezometric surface 
  and the rate and duration of discharge of a well using ground-water storage"
- Domenico & Schwartz (1998) "Physical and Chemical Hydrogeology"
"""

import numpy as np
from scipy.special import exp1
from scipy.optimize import curve_fit
from typing import Tuple, Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class TheisAnalysis:
    """
    Classe pour l'analyse Theis des essais de pompage.
    
    Attributes:
        Q (float): Débit de pompage constant (m³/s)
        times (np.ndarray): Temps de mesure (s)
        distances (np.ndarray): Distance puits-piézomètre (m)
        drawdowns (np.ndarray): Rabattements mesurés (m)
        T (float): Transmissivité estimée (m²/s)
        S (float): Coefficient d'emmagasinement
        u_values (np.ndarray): Paramètre dimensionnel u = r²S/(4*T*t)
    """
    
    def __init__(self, Q: float, distance: float, times: np.ndarray, drawdowns: np.ndarray):
        """
        Initialise l'analyse Theis.
        
        Args:
            Q (float): Débit de pompage (m³/s)
            distance (float): Distance puits-piézomètre (m)
            times (np.ndarray): Vecteur temps (s)
            drawdowns (np.ndarray): Rabattements mesurés (m)
        """
        self.Q = Q
        self.distance = distance
        self.times = np.asarray(times, dtype=float)
        self.drawdowns = np.asarray(drawdowns, dtype=float)
        
        self.T = None
        self.S = None
        self.u_values = None
        self.calculated_drawdowns = None
        self.residuals = None
        self.rmse = None
        
    @staticmethod
    def well_function(u: np.ndarray) -> np.ndarray:
        """
        Fonction de puits W(u) = -Ei(-u) ≈ exp1(u) pour u < 1.
        
        Utilise scipy.special.exp1 qui évalue -Ei(-u).
        
        Args:
            u (np.ndarray): Paramètre dimensionnel
            
        Returns:
            np.ndarray: W(u) - fonction de puits
        """
        return exp1(u)
    
    def calculate_u(self, T: float) -> np.ndarray:
        """
        Calcule le paramètre u = r²*S / (4*T*t).
        
        Args:
            T (float): Transmissivité (m²/s)
            
        Returns:
            np.ndarray: Vecteur u
        """
        if T <= 0:
            raise ValueError("Transmissivité T doit être positive")
        return (self.distance**2 * self.S) / (4 * T * self.times)
    
    def theis_curve(self, T: float) -> np.ndarray:
        """
        Génère la courbe théorique Theis pour une transmissivité donnée.
        
        s = (Q / (4*π*T)) * W(u)
        
        Args:
            T (float): Transmissivité (m²/s)
            
        Returns:
            np.ndarray: Rabattements théoriques (m)
        """
        u = self.calculate_u(T)
        W_u = self.well_function(u)
        s_theo = (self.Q / (4 * np.pi * T)) * W_u
        return s_theo
    
    def fit(self, initial_T: Optional[float] = None, S_fix: Optional[float] = None) -> Dict:
        """
        Estime T et S par ajustement aux données mesurées.
        
        Args:
            initial_T (float, optional): Valeur initiale de T pour l'optimisation
            S_fix (float, optional): Si fourni, S est fixé à cette valeur et seul T est estimé
            
        Returns:
            Dict: Dictionnaire contenant :
                - 'T' (float): Transmissivité estimée (m²/s)
                - 'S' (float): Coefficient d'emmagasinement
                - 'rmse' (float): Erreur quadratique moyenne
                - 'success' (bool): Convergence de l'optimisation
                - 'params' (dict): Paramètres supplémentaires
        """
        
        if len(self.drawdowns) < 2:
            raise ValueError("Au moins 2 mesures sont nécessaires")
        
        # Initialisation
        if initial_T is None:
            initial_T = 1e-3
        
        # Cas 1 : S est connu, estimer T seul
        if S_fix is not None:
            self.S = S_fix
            
            def objective(T):
                if T <= 0:
                    return 1e10
                return np.sum((self.theis_curve(T) - self.drawdowns)**2)
            
            from scipy.optimize import minimize_scalar
            result = minimize_scalar(objective, bounds=(1e-6, 1), method='bounded')
            self.T = result.x
            
        else:
            # Cas 2 : Estimer T et S ensemble
            # Initialiser S
            self.S = 1e-4
            
            def objective(params):
                T, S = params
                if T <= 0 or S <= 0:
                    return 1e10
                self.S = S
                return np.sum((self.theis_curve(T) - self.drawdowns)**2)
            
            from scipy.optimize import minimize
            result = minimize(objective, [initial_T, 1e-4], method='Nelder-Mead')
            self.T, self.S = result.x
        
        # Calcul des résidus
        self.calculated_drawdowns = self.theis_curve(self.T)
        self.residuals = self.drawdowns - self.calculated_drawdowns
        self.rmse = np.sqrt(np.mean(self.residuals**2))
        
        logger.info(f"Theis fit: T={self.T:.2e} m²/s, S={self.S:.2e}, RMSE={self.rmse:.4f} m")
        
        return {
            'T': self.T,
            'S': self.S,
            'rmse': self.rmse,
            'success': self.rmse < np.mean(self.drawdowns) * 0.1,  # Critère simple
            'params': {
                'Q': self.Q,
                'distance': self.distance,
                'num_points': len(self.times)
            }
        }
    
    def generate_curve(self, T: float, S: float, t_range: np.ndarray) -> Dict:
        """
        Génère la courbe complète Theis pour paramètres donnés.
        
        Args:
            T (float): Transmissivité (m²/s)
            S (float): Coefficient d'emmagasinement
            t_range (np.ndarray): Vecteur temps pour la génération (s)
            
        Returns:
            Dict contenant 't', 's', 'u', 'W_u'
        """
        self.T = T
        self.S = S
        self.times = np.asarray(t_range)
        
        u = self.calculate_u(T)
        W_u = self.well_function(u)
        s = (self.Q / (4 * np.pi * T)) * W_u
        
        return {
            'time': t_range,
            'drawdown': s,
            'u': u,
            'W_u': W_u,
            'T': T,
            'S': S
        }
    
    def get_summary(self) -> str:
        """Résumé texte des résultats."""
        if self.T is None:
            return "Analyse non effectuée"
        
        return f"""
Résultats Theis
===============
Débit de pompage (Q):      {self.Q:.2e} m³/s
Distance (r):              {self.distance:.2f} m
Transmissivité (T):        {self.T:.2e} m²/s
Coefficient emmagasinement: {self.S:.2e}
RMSE:                      {self.rmse:.4f} m
Nombre de points:          {len(self.times)}
        """


# Fonctions simplifiées pour utilisation directe
def estimate_transmissivity_theis(Q: float, distance: float, times: np.ndarray, 
                                   drawdowns: np.ndarray) -> Tuple[float, float]:
    """
    Estime T et S à partir de données Theis.
    
    Args:
        Q: Débit (m³/s)
        distance: Distance puits-piézomètre (m)
        times: Temps (s)
        drawdowns: Rabattements (m)
        
    Returns:
        (T, S) - Transmissivité et coefficient d'emmagasinement
    """
    analysis = TheisAnalysis(Q, distance, times, drawdowns)
    result = analysis.fit()
    return result['T'], result['S']


def theis_drawdown(Q: float, T: float, S: float, distance: float, time: float) -> float:
    """
    Calcule le rabattement Theis à un instant t.
    
    s(r,t) = Q / (4πT) * W(u)  avec  u = r²S / (4Tt)
    
    Args:
        Q: Débit (m³/s)
        T: Transmissivité (m²/s)
        S: Coefficient d'emmagasinement
        distance: Distance (m)
        time: Temps (s)
        
    Returns:
        Rabattement (m)
    """
    u = (distance**2 * S) / (4 * T * time)
    W_u = exp1(u)
    return (Q / (4 * np.pi * T)) * W_u
