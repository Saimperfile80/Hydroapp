"""
Détection d'anomalies - Module IA
==================================

Identifie les données aberrantes/incohérentes pour guidance utilisateur.
Méthodes simples et explicables (pas de boîte noire).
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Détection d'anomalies basée sur statistiques simples et explicables.
    """
    
    def __init__(self, confidence_threshold: float = 0.95):
        """
        Args:
            confidence_threshold: Seuil de confiance (0-1) pour détecter anomalies
        """
        self.confidence_threshold = confidence_threshold
        self.anomalies = []
        self.explanations = []
        
    def detect_outliers_zscore(self, data: np.ndarray, threshold: float = 3.0) -> Tuple[np.ndarray, List[str]]:
        """
        Détection par Z-score (écart à la moyenne en écarts-types).
        
        Un point avec |Z| > threshold est considéré anomalie.
        Explicable : "Valeur à X écarts-types de la moyenne"
        
        Args:
            data (np.ndarray): Données 1D
            threshold (float): Seuil Z (typiquement 2-3 sigmas)
            
        Returns:
            (indices_anomalies, explications)
        """
        data = np.asarray(data, dtype=float)
        
        mean = np.mean(data)
        std = np.std(data)
        
        if std < 1e-10:
            return np.array([]), []
        
        z_scores = np.abs((data - mean) / std)
        anomaly_indices = np.where(z_scores > threshold)[0]
        
        explanations = [
            f"Point {idx}: valeur={data[idx]:.2f}, Z-score={z_scores[idx]:.2f} "
            f"(à {z_scores[idx]:.1f}σ de la moyenne {mean:.2f})"
            for idx in anomaly_indices
        ]
        
        return anomaly_indices, explanations
    
    def detect_outliers_iqr(self, data: np.ndarray) -> Tuple[np.ndarray, List[str]]:
        """
        Détection par IQR (InterQuartile Range).
        
        Points < Q1-1.5*IQR ou > Q3+1.5*IQR sont anomalies.
        Explicable : "En dehors de l'intervalle plausible [min-max]"
        
        Args:
            data (np.ndarray): Données 1D
            
        Returns:
            (indices_anomalies, explications)
        """
        data = np.asarray(data, dtype=float)
        
        Q1 = np.percentile(data, 25)
        Q3 = np.percentile(data, 75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        anomaly_indices = np.where((data < lower_bound) | (data > upper_bound))[0]
        
        explanations = [
            f"Point {idx}: valeur={data[idx]:.2f} en dehors [{lower_bound:.2f}, {upper_bound:.2f}]"
            for idx in anomaly_indices
        ]
        
        return anomaly_indices, explanations
    
    def detect_spatial_outliers(self, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                                 threshold_neighbors: int = 5) -> Tuple[np.ndarray, List[str]]:
        """
        Détection spatiale : isolé de ses voisins.
        
        Un point est anomalie s'il diffère grandement de ses k plus proches voisins.
        Explicable : "Valeur isolée dans le voisinage spatial"
        
        Args:
            x, y, z : Coordonnées + propriété
            threshold_neighbors: Nombre de voisins pour comparaison
            
        Returns:
            (indices_anomalies, explications)
        """
        from scipy.spatial.distance import cdist
        
        x, y, z = np.asarray(x), np.asarray(y), np.asarray(z, dtype=float)
        
        # Distance euclidienne en (x,y)
        coords = np.column_stack([x, y])
        distances = cdist(coords, coords, metric='euclidean')
        
        anomaly_indices = []
        explanations = []
        
        for i in range(len(z)):
            # k plus proches voisins (excl. le point lui-même)
            nearest = np.argsort(distances[i])[1:threshold_neighbors+1]
            
            z_neighbors = z[nearest]
            z_mean_neighbors = np.mean(z_neighbors)
            z_std_neighbors = np.std(z_neighbors)
            
            if z_std_neighbors > 1e-10:
                z_dev = np.abs(z[i] - z_mean_neighbors) / z_std_neighbors
                
                if z_dev > 3.0:  # 3 sigma par rapport au voisinage
                    anomaly_indices.append(i)
                    explanations.append(
                        f"Point {i} (x={x[i]:.1f}, y={y[i]:.1f}): z={z[i]:.2f} "
                        f"vs voisins moyen={z_mean_neighbors:.2f} (écart: {z_dev:.1f}σ)"
                    )
        
        return np.array(anomaly_indices), explanations
    
    def comprehensive_check(self, data_dict: Dict) -> Dict:
        """
        Check complet d'une série de données (multidimensionnelle).
        
        Args:
            data_dict: Dict {variable_name: np.ndarray}
            
        Returns:
            Dict avec résumé anomalies et confiance globale
        """
        all_anomalies = []
        all_explanations = []
        
        for var_name, data in data_dict.items():
            if data is None or len(data) == 0:
                continue
            
            data = np.asarray(data, dtype=float)
            
            # Z-score
            idx_z, exp_z = self.detect_outliers_zscore(data, threshold=2.5)
            for i, e in zip(idx_z, exp_z):
                all_anomalies.append((var_name, i, e))
                all_explanations.append(e)
            
            # IQR
            idx_iqr, exp_iqr = self.detect_outliers_iqr(data)
            for i, e in zip(idx_iqr, exp_iqr):
                if (var_name, i) not in [(a[0], a[1]) for a in all_anomalies]:
                    all_anomalies.append((var_name, i, e))
                    all_explanations.append(e)
        
        # Confiance globale
        num_points = sum(len(v) for v in data_dict.values() if v is not None)
        contamination_rate = len(all_anomalies) / max(num_points, 1)
        
        if contamination_rate < 0.05:
            confidence_score = 95
            status = "EXCELLENT"
        elif contamination_rate < 0.10:
            confidence_score = 85
            status = "BON"
        elif contamination_rate < 0.20:
            confidence_score = 70
            status = "ATTENTION"
        else:
            confidence_score = 50
            status = "RÉVISER"
        
        return {
            'num_anomalies': len(all_anomalies),
            'contamination_rate': contamination_rate * 100,
            'confidence_score': confidence_score,
            'status': status,
            'anomalies': all_anomalies,
            'explanations': all_explanations
        }
    
    def get_recommendations(self, anomaly_report: Dict) -> List[str]:
        """Recommandations basées sur détection."""
        recommendations = []
        
        if anomaly_report['num_anomalies'] == 0:
            recommendations.append("✓ Aucune anomalie détectée - Données cohérentes")
        else:
            recommendations.append(f"⚠ {anomaly_report['num_anomalies']} anomalie(s) détectée(s)")
            recommendations.append("  → Vérifier ces points, éventuellement les exclure ou corriger")
        
        if anomaly_report['contamination_rate'] > 10:
            recommendations.append("  → Forte contamination : revoir la qualité de la campagne")
        
        return recommendations


def simple_anomaly_score(data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Score simple 0-100 pour chaque point (0=normal, 100=anomalie certaine).
    
    Returns:
        (scores, explanations)
    """
    detector = AnomalyDetector()
    
    z_scores = np.abs((data - np.mean(data)) / (np.std(data) + 1e-10))
    
    # Mappage : Z~3 -> score 50%, Z~5 -> score 100%
    scores = np.minimum(100 * z_scores / 3, 100)
    
    explanations = [
        f"Point {i}: Z-score={z:.2f}, score anomalie={s:.0f}/100"
        for i, (z, s) in enumerate(zip(z_scores, scores))
    ]
    
    return scores, explanations
