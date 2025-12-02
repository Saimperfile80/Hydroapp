"""
HydroAI - Plateforme de modélisation hydrogéologique avec IA
============================================================

Architecture modulaire pour simulations hydrogéologiques fiables et pédagogiques.

Modules principaux:
  - core.calculations : Calculs hydrogéologiques standard (Theis, Cooper-Jacob, etc.)
  - core.solver : Solveur EF pour écoulement saturé
  - core.mesh : Génération de maillages
  - core.io : Import/export de données
  - core.ai : Assistant IA pédagogique
  - core.post : Post-traitement et visualisation
  - core.project : Gestion de projets
"""

__version__ = "0.1.0-alpha"
__author__ = "HydroAI Team"

import logging

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from . import calculations
from . import solver
from . import mesh
from . import io
from . import ai
from . import post
from . import project

__all__ = [
    'calculations',
    'solver',
    'mesh',
    'io',
    'ai',
    'post',
    'project',
]
