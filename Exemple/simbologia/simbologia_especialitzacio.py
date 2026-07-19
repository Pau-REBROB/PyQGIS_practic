import config
import simbologia.simbologies as simbologies

def simbologia_us_predominant(districtes):
    """
    Aplica una simbologia categòrica als districtes
    segons el seu ús predominant.
    """

    districtes_clone = districtes.clone()

    simbologies.simbologia_categorica(
        layer=districtes_clone,
        **config.SIMBOLOGIA["Districtes_us_predominant"]
    )

    return districtes_clone


def simbologia_dominancia(districtes):
    """
    Aplica una simbologia graduada als districtes
    segons el grau de dominància funcional.
    """

    districtes_clone = districtes.clone()

    simbologies.simbologia_graduada(
        layer=districtes_clone,
        **config.SIMBOLOGIA["Districtes_dominancia"]
    )

    return districtes_clone


def simbologia_shannon(districtes):
    """
    Aplica una simbologia graduada als districtes
    segons l'índex de diversitat de Shannon.
    """

    districtes_clone = districtes.clone()

    simbologies.simbologia_graduada(
        layer=districtes_clone,
        **config.SIMBOLOGIA["Districtes_shannon"]
    )

    return districtes_clone
