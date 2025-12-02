"""
Module Piézométrie - Analyse de données piézométriques
=======================================================

Outils pour analyse des niveaux piézométriques, tendances, variations saisonnières
et interprétations hydrogéologiques standard.
"""

import numpy as np
from scipy import stats
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, List
import logging

logger = logging.getLogger(__name__)


class PiezoAnalysis:
    """
    Analyse complète de données piézométriques.
    """
    
    def __init__(self, dates: List[datetime], levels: np.ndarray):
        """
        Args:
            dates (List[datetime]): Dates des mesures
            levels (np.ndarray): Niveaux piézométriques (m NGF ou relatif)
        """
        self.dates = dates
        self.levels = np.asarray(levels, dtype=float)
        self.n_points = len(self.levels)
        
        # Calcul de paramètres basiques
        self.min_level = np.min(self.levels)
        self.max_level = np.max(self.levels)
        self.mean_level = np.mean(self.levels)
        self.std_level = np.std(self.levels)
        self.amplitude = self.max_level - self.min_level
        
    def get_statistics(self) -> Dict:
        """Statistiques descriptives."""
        return {
            'n_points': self.n_points,
            'min': self.min_level,
            'max': self.max_level,
            'mean': self.mean_level,
            'std': self.std_level,
            'amplitude': self.amplitude,
            'range': (self.min_level, self.max_level)
        }
    
    def compute_trend(self) -> Dict:
        """
        Calcule la tendance linéaire long terme.
        
        Returns:
            Dict avec slope (m/year), intercept, r², interpretation
        """
        # Convertir dates en jours depuis première mesure
        t_days = np.array([(d - self.dates[0]).days for d in self.dates], dtype=float)
        
        # Fit linéaire
        slope_days, intercept, r_value, p_value, std_err = stats.linregress(t_days, self.levels)
        
        # Conversion en m/year
        slope_year = slope_days * 365.25
        
        # Interprétation
        if abs(slope_year) < 0.01:
            trend_type = "Stable"
        elif slope_year > 0.01:
            trend_type = f"Hausse ({slope_year:.3f} m/an)"
        else:
            trend_type = f"Baisse ({slope_year:.3f} m/an)"
        
        return {
            'slope_m_day': slope_days,
            'slope_m_year': slope_year,
            'intercept': intercept,
            'r_squared': r_value**2,
            'p_value': p_value,
            'std_error': std_err,
            'interpretation': trend_type,
            't_days': t_days,
            'trend_line': intercept + slope_days * t_days
        }
    
    def identify_aquifer_type(self) -> Dict:
        """
        Classifie le type d'aquifère selon les caractéristiques.
        """
        # Critères qualitatifs
        if self.amplitude > 1.0:
            behavior = "Fort amplitude - Aquifère libre / semi-libre"
        elif self.amplitude > 0.3:
            behavior = "Amplitude modérée - Aquifère captif/libre"
        else:
            behavior = "Faible amplitude - Aquifère captif / profond"
        
        # Réaction aux pluies / saisonnalité
        std_norm = self.std_level / self.mean_level if self.mean_level > 0 else 0
        
        if std_norm > 0.1:
            reactivity = "Très réactif - Aquifère proche surface"
        elif std_norm > 0.05:
            reactivity = "Réactif - Aquifère peu profond"
        else:
            reactivity = "Peu réactif - Aquifère profond/captif"
        
        return {
            'behavior': behavior,
            'reactivity': reactivity,
            'amplitude_m': self.amplitude,
            'std_normalized': std_norm
        }
    
    def get_summary(self) -> str:
        """Résumé texte complet."""
        stats = self.get_statistics()
        trend = self.compute_trend()
        aquifer = self.identify_aquifer_type()
        
        return f"""
Résultats Analyse Piézométrique
==============================
Statistiques:
  Nombre de points:    {stats['n_points']}
  Niveau min:          {stats['min']:.3f} m
  Niveau max:          {stats['max']:.3f} m
  Niveau moyen:        {stats['mean']:.3f} m
  Écart-type:          {stats['std']:.3f} m
  Amplitude:           {stats['amplitude']:.3f} m

Tendance long terme:
  Pente:               {trend['slope_m_year']:.4f} m/an
  R²:                  {trend['r_squared']:.3f}
  Interprétation:      {trend['interpretation']}

Type d'aquifère:
  Comportement:        {aquifer['behavior']}
  Réactivité:          {aquifer['reactivity']}
        """


def compute_recovery_curve(time: np.ndarray, head: np.ndarray) -> Dict:
    """
    Analyse courbe de remontée (fin d'un essai de pompage).
    
    Returns:
        Dict avec paramètres de remontée
    """
    # Fit exponentiel
    from scipy.optimize import curve_fit
    
    def recovery(t, h_final, alpha):
        return h_final * (1 - np.exp(-alpha * t))
    
    try:
        params, _ = curve_fit(recovery, time, head, p0=[head[-1], 0.1], maxfev=1000)
        h_final, alpha = params
        
        return {
            'h_final': h_final,
            'alpha': alpha,
            'tau_recovery': 1.0 / alpha,  # Temps caractéristique
            'success': True
        }
    except Exception as e:
        logger.error(f"Fit courbe remontée échoué: {e}")
        return {'success': False, 'error': str(e)}


def compute_drawdown_derivative(time: np.ndarray, drawdown: np.ndarray) -> np.ndarray:
    """
    Calcule la dérivée du rabattement (outil diagnostic).
    
    d(s)/d(log t) utile pour identifier régimes d'écoulement.
    """
    log_t = np.log10(time)
    ds_dlogt = np.gradient(drawdown, log_t)
    return ds_dlogt
