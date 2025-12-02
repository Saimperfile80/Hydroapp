"""
Validation pré-calcul - Module IA
==================================

Vérifie cohérence et plausibilité des paramètres AVANT lancement simulation.

Scores: OK / ATTENTION / BLOQUÉ
"""

import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class PreComputeValidator:
    """
    Valide cohérence paramètres hydrogéologiques avant calcul.
    """
    
    def __init__(self):
        self.validation_results = {}
        self.severity_levels = {
            'OK': 0,
            'ATTENTION': 1,
            'BLOQUÉ': 2
        }
    
    def validate_theis_parameters(self, Q: float, T: float, S: float, 
                                  distance: float, time_max: float) -> Dict:
        """
        Valide cohérence paramètres essai Theis.
        
        Returns:
            Dict avec status (OK/ATTENTION/BLOQUÉ) et explications
        """
        issues = []
        warnings = []
        
        # Vérifications basiques
        if Q <= 0:
            issues.append("❌ Débit Q doit être positif")
        
        if T <= 0:
            issues.append("❌ Transmissivité T doit être positive")
        
        if S <= 0 or S >= 1:
            issues.append("❌ Coefficient emmagasinement S doit être entre 0 et 1")
        
        if distance <= 0:
            issues.append("❌ Distance r doit être positive")
        
        # Vérifications de plausibilité
        if T > 1e-2:  # T > 10^-2 très haut
            warnings.append(f"⚠ Transmissivité très élevée: T={T:.2e} (atypique)")
        
        if S < 1e-6:  # S < 10^-6 très bas
            warnings.append(f"⚠ Emmagasinement très faible: S={S:.2e} (captif profond?)")
        
        # Vérifier cohérence T-S : ratio raisonnable?
        if distance and time_max:
            u_min = (distance**2 * S) / (4 * T * time_max)
            
            if u_min > 10:
                warnings.append(f"⚠ u={u_min:.2f} >> 1 : temps observation trop court?")
            elif u_min < 1e-4:
                warnings.append(f"⚠ u={u_min:.2e} << 1 : temps observation très long")
        
        # Débit cohérent avec T?
        if Q > T * distance / 100:  # Heuristique simple
            warnings.append(f"⚠ Débit semble élevé pour T donnée")
        
        # Résumé
        if issues:
            status = 'BLOQUÉ'
            severity = 2
        elif warnings:
            status = 'ATTENTION'
            severity = 1
        else:
            status = 'OK'
            severity = 0
        
        return {
            'status': status,
            'severity': severity,
            'issues': issues,
            'warnings': warnings,
            'confidence_score': max(0, 100 - len(issues)*20 - len(warnings)*5),
            'can_proceed': len(issues) == 0
        }
    
    def validate_geology_parameters(self, K: float, porosity: float, 
                                     S: float, lithology: str = '') -> Dict:
        """
        Valide cohérence paramètres géologiques.
        """
        issues = []
        warnings = []
        
        # Vérifications basiques
        if K <= 0 or K > 1:
            issues.append("❌ Conductivité K hors limites (0 < K < 1 m/s)")
        
        if porosity <= 0 or porosity >= 1:
            issues.append("❌ Porosité hors limites (0 < φ < 1)")
        
        if S <= 0 or S >= porosity:
            issues.append("❌ Coefficient emmagasinement incohérent (0 < S < φ)")
        
        # Cohérences K-lithologie
        if lithology:
            K_expected = {
                'graviers': (1e-2, 1e-3),
                'sables': (1e-3, 1e-5),
                'silt': (1e-5, 1e-7),
                'argile': (1e-7, 1e-9),
            }
            
            if lithology in K_expected:
                K_min, K_max = K_expected[lithology]
                if K < K_min or K > K_max:
                    warnings.append(
                        f"⚠ K={K:.2e} en dehors plage {lithology} "
                        f"({K_min:.2e}-{K_max:.2e})"
                    )
        
        # Cohérence S-porosité pour aquifère captif
        if S / porosity < 1e-6:
            warnings.append(f"⚠ Aquifère très captif (S/φ={S/porosity:.2e})")
        elif S / porosity > 0.1:
            warnings.append(f"⚠ Aquifère très libre (S/φ={S/porosity:.2f})")
        
        if issues:
            status = 'BLOQUÉ'
            severity = 2
        elif warnings:
            status = 'ATTENTION'
            severity = 1
        else:
            status = 'OK'
            severity = 0
        
        return {
            'status': status,
            'severity': severity,
            'issues': issues,
            'warnings': warnings,
            'confidence_score': max(0, 100 - len(issues)*20 - len(warnings)*5),
            'can_proceed': len(issues) == 0
        }
    
    def validate_boundary_conditions(self, BCs: Dict) -> Dict:
        """
        Valide cohérence conditions aux limites.
        
        Args:
            BCs: Dict {location: {'type': 'Dirichlet'|'Neumann'|..., 'value': ...}}
        """
        issues = []
        warnings = []
        
        if not BCs:
            issues.append("❌ Aucune condition aux limites définie")
        
        # Vérifier au moins 1 Dirichlet ou Neumann par bord
        bc_types = [bc.get('type', '') for bc in BCs.values()]
        
        if not any('Dirichlet' in t or 'Neumann' in t for t in bc_types):
            issues.append("❌ Au moins une condition Dirichlet ou Neumann requise")
        
        # Vérifier cohérence valeurs
        for loc, bc in BCs.items():
            val = bc.get('value', 0)
            if bc.get('type') == 'Neumann' and abs(val) > 1:  # Heuristique
                warnings.append(f"⚠ Flux Neumann {val} très élevé en {loc}")
        
        if issues:
            status = 'BLOQUÉ'
        elif warnings:
            status = 'ATTENTION'
        else:
            status = 'OK'
        
        return {
            'status': status,
            'issues': issues,
            'warnings': warnings,
            'can_proceed': len(issues) == 0
        }
    
    def global_check(self, params: Dict) -> Dict:
        """
        Check global avant simulation.
        
        Args:
            params: Dict complet avec tous les paramètres
            
        Returns:
            Rapport de validation complet
        """
        all_issues = []
        all_warnings = []
        overall_confidence = 100
        
        # Check Theis
        if 'theis' in params:
            result = self.validate_theis_parameters(
                params['theis'].get('Q', 0),
                params['theis'].get('T', 0),
                params['theis'].get('S', 0),
                params['theis'].get('distance', 0),
                params['theis'].get('time_max', 1)
            )
            all_issues.extend(result['issues'])
            all_warnings.extend(result['warnings'])
            overall_confidence = min(overall_confidence, result['confidence_score'])
        
        # Check géologie
        if 'geology' in params:
            result = self.validate_geology_parameters(
                params['geology'].get('K', 0),
                params['geology'].get('porosity', 0.3),
                params['geology'].get('S', 0),
                params['geology'].get('lithology', '')
            )
            all_issues.extend(result['issues'])
            all_warnings.extend(result['warnings'])
            overall_confidence = min(overall_confidence, result['confidence_score'])
        
        # Déterminer status global
        if all_issues:
            overall_status = 'BLOQUÉ'
        elif all_warnings:
            overall_status = 'ATTENTION'
        else:
            overall_status = 'OK'
        
        return {
            'overall_status': overall_status,
            'confidence_score': overall_confidence,
            'can_proceed': overall_status != 'BLOQUÉ',
            'issues': all_issues,
            'warnings': all_warnings,
            'num_issues': len(all_issues),
            'num_warnings': len(all_warnings),
            'message': f"[{overall_status}] {len(all_issues)} problème(s) bloquant(s), "
                      f"{len(all_warnings)} attention(s)"
        }
