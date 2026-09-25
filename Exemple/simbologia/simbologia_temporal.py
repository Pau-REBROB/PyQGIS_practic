"""
"""

import simbologia.simbologies as simbologies
import config

def simbologia_temporal_parc_edificis(edificis, breaks, tipus):
    """
    """
    layer = simbologies.simbologia_graduada_manual(
        layer=edificis,
        intervals=breaks,
        **config.SIMBOLOGIA["Temporal"]["General"][tipus]
    )

    layer.setName(f"Antiguitat dels edificis {tipus}")

    return layer