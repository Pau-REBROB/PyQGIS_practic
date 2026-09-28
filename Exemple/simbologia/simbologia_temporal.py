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


def simbologia_temporal_antiguitat_relativa_barris(barris, breaks):
    """
    """
    layer = simbologies.simbologia_graduada_manual(
        layer=barris,
        intervals=breaks,
        **config.SIMBOLOGIA["Temporal"]["Antiguitat_relativa"]
    )

    layer.setName("Antiguitat edificis industrials respecte la resta")

    return layer

