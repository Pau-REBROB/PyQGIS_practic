import config
import simbologia.simbologies as simbologies

def simbologia_us_predominant(districtes):
    """
    Aplica una simbologia categòrica als districtes
    segons el seu ús predominant.
    """

    layer = simbologies.simbologia_categorica(
        layer=districtes,
        **config.SIMBOLOGIA["Districtes_us_predominant"]
    )

    layer.setName("Districtes_us_predominant")

    return layer


def simbologia_dominancia(districtes):
    """
    Aplica una simbologia graduada als districtes
    segons el grau de dominància funcional.
    """

    layer = simbologies.simbologia_graduada(
        layer=districtes,
        **config.SIMBOLOGIA["Districtes_dominancia"]
    )

    layer.setName("Districtes_dominancia")

    return layer


def simbologia_shannon(districtes):
    """
    Aplica una simbologia graduada als districtes
    segons l'índex de diversitat de Shannon.
    """

    layer = simbologies.simbologia_graduada(
        layer=districtes,
        **config.SIMBOLOGIA["Districtes_shannon"]
    )

    layer.setName("Districtes_shannon_norm")

    return layer
