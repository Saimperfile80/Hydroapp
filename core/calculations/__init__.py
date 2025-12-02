"""
Modules de calcul hydrogéologiques
==================================

Ensemble des fonctions de calcul scientifiques pour HydroAI.
Ces modules implémentent les méthodes standard utilisées en hydrogéologie :
- Essais de pompage (Theis, Cooper-Jacob)
- Tests de perméabilité (Lefranc, Lugeon, Porchet)
- Analyse piézométrique
- Etc.

Chaque méthode a son propre fichier pour une meilleure maintenabilité et testabilité.
"""

from .theis import *
from .cooper_jacob import *
from .lefranc import *
from .lugeon import *
from .porchet import *
from .piezo import *

__all__ = [
    'theis',
    'cooper_jacob',
    'lefranc',
    'lugeon',
    'porchet',
    'piezo',
]
