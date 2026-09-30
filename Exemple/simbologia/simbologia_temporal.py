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
        **config.SIMBOLOGIA["Temporal"]["Antiguitat_relativa"]["Barris_categoritzats"]
    )

    renderer = layer.renderer()

    for i, rang in enumerate(renderer.ranges()):
        etiqueta = config.ETIQUETES_ANTIGUITAT.get(i)
        renderer.updateRangeLabel(i, etiqueta)
       
    layer.triggerRepaint()

    layer.setName("Antiguitat edificis industrials respecte la resta")

    return layer


def simbologia_temporal_barris_neutres(barris):
    """
    """
    layer = simbologies.simbologia_unica(
        layer=barris,
        nom="Barris_sense_categoritzar",
        **config.SIMBOLOGIA["Temporal"]["Antiguitat_relativa"]["Barris_neutres"]
    )

    layer.setName("Barris sense categoritzar en antiguitat relativa")

    return layer


def simbologia_temporal_antiguitat_relativa_edificis(edificis, breaks):
    """
    """
    layer = simbologies.simbologia_graduada_manual(
        layer=edificis,
        intervals=breaks,
        **config.SIMBOLOGIA["Temporal"]["Antiguitat_relativa"]["Edificis_categoritzats"]
    )

    renderer = layer.renderer()

    for i, rang in enumerate(renderer.ranges()):
        etiqueta = config.ETIQUETES_ANTIGUITAT.get(i)
        renderer.updateRangeLabel(i, etiqueta)
       
    layer.triggerRepaint()

    layer.setName("Antiguitat edificis industrials respecte la resta del barri")

    return layer


def simbologia_temporal_edificis_neutres(edificis):
    """
    """
    layer = simbologies.simbologia_unica(
        layer=edificis,
        nom="Edificis_sense_categoritzar",
        **config.SIMBOLOGIA["Temporal"]["Antiguitat_relativa"]["Edificis_neutres"]
    )

    layer.setName("Edificis sense categoritzar en antiguitat relativa")

    return layer
