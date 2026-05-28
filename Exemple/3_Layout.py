"""GENERACIÓ DE CARTOGRAFIA"""

# Importació de les funcions definides en els scripts de simbologia
import sys
sys.path.append("C:/projectes_git/PyQGIS_practic/Exemple")

from simbologia_unica_2_1 import simbologia_unica, simbologia_unica_linia
from simbologia_categorica_2_2 import simbologia_categorica
from simbologia_graduada_2_3 import simbologia_graduada_QGIS
from simbologia_graduada_manual_2_4 import simbologia_graduada_manual


# QUINS LAYOUTS VULL CREAR?
## simbologia única per tenir de fons les divisions administratives
## simbologia categòrica --> ús dels edificis / barris,districtes
## simbologia graduada --> altura dels edificis / àrea barris,districtes / població (CAL AFEGIR-LA)
## simbologia regles --> els barris amb més,menys àrea o població / edificis amb més,menys plantes

# Aplicació de les funcions per generar la cartografia



# Generació del layout 