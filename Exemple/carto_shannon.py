# Representació de l'índex Shannon

# Importació de mòduls i funcions
import sys
sys.path.append("C:/projectes_git/PyQGIS_practic/Exemple")
import importlib
import os

# Forçar la recàrrega dels mòduls de simbologia
mods_a_recarregar = [
    "simbologia_unica_2_1",
    "simbologia_shannon"
]

for mod in mods_a_recarregar:
    if mod in sys.modules:
        importlib.reload(sys.modules[mod])

from simbologia.simbologia_unica import simbologia_unica, simbologia_unica_linia
from simbologia_shannon import simbologia_shannon


layer_diversitat = simbologia_shannon(
    districtes,
    num_classes = 5,
    color_ramp = "Viridis",
    mode = "Jenks",
    stroke_color = "black",
    stroke_width = 0.3
)

layer_diversitat_barris = simbologia_shannon(
    barris,
    num_classes = 5,
    color_ramp = "Greens",
    mode = "Jenks",
    stroke_color = "white",
    stroke_width = 0.3
)
