"""
Module Lugeon - Test de perméabilité à la Lugeon
=================================================

Test standard en génie civil pour qualifier les formations rocheuses
et le succès de traitements d'injection/scellement.

La Lugeon (UL) = unité de perméabilité = débit en L/min sous 10 bar
par unité de longueur testée (m).

1 UL ≈ 10^-7 m/s

Référence:
- Lugeon, A. (1933). Barrages et géologie
"""

import numpy as np
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class LugeonTest:
    """
    Test d'injectivité à la Lugeon.
    
    Principe :
        - Injection d'eau à pression progressive (5 bar -> 10 bar -> 5 bar)
        - Mesure du débit à chaque palier (3 min chacun)
        - Calcul de perméabilité moyenne
    """
    
    # Constante de conversion : 1 UL = 1 L/min/m à 10 bar
    # En SI : 10 bar = 1 MPa = 1e6 Pa
    LUGEON_TO_MS = 1.0e-7  # m/s
    
    def __init__(self, test_length: float):
        """
        Args:
            test_length (float): Longueur du tronçon testé (m)
        """
        self.test_length = test_length
        self.pressure_steps = []  # Pressions (bar)
        self.discharge_rates = []  # Débits (L/min)
        self.lugeon_values = []  # Lugeons (UL)
        self.K_values = []  # K (m/s)
        self.K_mean = None
        self.K_unit = 'm/s'
        
    def add_measurement(self, pressure_bar: float, discharge_lpm: float):
        """
        Ajoute une mesure de débit à une pression donnée.
        
        Args:
            pressure_bar (float): Pression (bar)
            discharge_lpm (float): Débit (L/min)
        """
        self.pressure_steps.append(pressure_bar)
        self.discharge_rates.append(discharge_lpm)
        
        # Calcul Lugeon : UL = (Q_lpm / L_m) * (10 / P_bar)
        # Ramené à 10 bar pour normalisation
        lugeon = (discharge_lpm / self.test_length) * (10.0 / pressure_bar)
        self.lugeon_values.append(lugeon)
        
        # Conversion m/s : K = UL * 10^-7
        K_ms = lugeon * self.LUGEON_TO_MS
        self.K_values.append(K_ms)
        
        logger.debug(f"Lugeon: P={pressure_bar} bar, Q={discharge_lpm} L/min, "
                     f"UL={lugeon:.2f}, K={K_ms:.2e} m/s")
    
    def compute_mean_k(self) -> Dict:
        """
        Calcule perméabilité moyenne (typiquement palier 10 bar).
        
        Returns:
            Dict avec K_mean, lugeon_mean, rmse_variation
        """
        if not self.K_values:
            raise ValueError("Aucune mesure effectuée")
        
        # Filtrer mesures à 10 bar
        idx_10bar = [i for i, p in enumerate(self.pressure_steps) if abs(p - 10.0) < 1.0]
        
        if idx_10bar:
            # Moyenne à 10 bar (plus fiable)
            self.K_mean = np.mean([self.K_values[i] for i in idx_10bar])
            lugeon_mean = np.mean([self.lugeon_values[i] for i in idx_10bar])
        else:
            # Sinon moyenne globale (moins fiable)
            self.K_mean = np.mean(self.K_values)
            lugeon_mean = np.mean(self.lugeon_values)
        
        # Variation (indicateur de qualité du test)
        std_K = np.std(self.K_values)
        cv = std_K / self.K_mean if self.K_mean > 0 else 0  # Coefficient de variation
        
        return {
            'K_mean': self.K_mean,
            'K_unit': 'm/s',
            'lugeon_mean': lugeon_mean,
            'std_K': std_K,
            'cv': cv,  # Coefficient de variation
            'num_steps': len(self.K_values),
            'success': True
        }
    
    def get_quality_assessment(self) -> str:
        """Évalue la qualité du test."""
        if not self.K_values:
            return "Aucune donnée"
        
        result = self.compute_mean_k()
        cv = result['cv']
        
        if cv < 0.15:
            return "Excellent - Très reproductible"
        elif cv < 0.30:
            return "Bon - Reproductible"
        elif cv < 0.50:
            return "Moyen - Acceptable"
        else:
            return "Mauvais - Trop variable (vérifier le test)"
    
    def get_summary(self) -> str:
        """Résumé texte complet."""
        if not self.K_values:
            return "Test non effectué"
        
        result = self.compute_mean_k()
        
        return f"""
Résultats Test Lugeon
====================
Longueur du tronçon (L): {self.test_length:.2f} m
Perméabilité moyenne (K): {result['K_mean']:.2e} m/s
Perméabilité moyenne:     {result['K_mean']*86400:.2e} m/jour
Lugeons moyens (UL):      {result['lugeon_mean']:.2f}
Coefficient de variation: {result['cv']*100:.1f}%
Qualité test:             {self.get_quality_assessment()}
Nombre de paliers:        {result['num_steps']}

Détail par palier:
"""+ "\n".join([f"  P={p:.0f} bar: Q={q:.1f} L/min, UL={ul:.2f}, K={k:.2e} m/s"
              for p, q, ul, k in zip(self.pressure_steps, self.discharge_rates,
                                      self.lugeon_values, self.K_values)])
    
    def export_results(self) -> Dict:
        """Exporte résultats complets."""
        result = self.compute_mean_k()
        result['pressure_steps'] = self.pressure_steps
        result['discharge_rates'] = self.discharge_rates
        result['lugeon_values'] = self.lugeon_values
        result['K_values'] = self.K_values
        result['quality'] = self.get_quality_assessment()
        return result


def lugeon_to_ms(lugeon: float) -> float:
    """Convertit Lugeons en m/s."""
    return lugeon * LugeonTest.LUGEON_TO_MS


def ms_to_lugeon(k_ms: float) -> float:
    """Convertit m/s en Lugeons."""
    return k_ms / LugeonTest.LUGEON_TO_MS
