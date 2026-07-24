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

    renderer = layer.renderer()

    rangs = renderer.ranges()

    for rang in rangs:
        lower = round(rang.lowerValue(), 1)
        upper = round(rang.upperValue(), 1)

        rang.setLabel(f"{lower:.1f} - {upper:.1f}%")

    renderer.updateRanges(rangs)

    layer.triggerRepaint()

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

    renderer = layer.renderer()

    rangs = renderer.ranges()

    for rang in rangs:
        lower = round(rang.lowerValue(), 2)
        upper = round(rang.upperValue(), 2)

        rang.setLabel(f"{lower:.2f} - {upper:.2f}")

    renderer.updateRanges(rangs)

    layer.triggerRepaint()

    layer.setName("Districtes_shannon_norm")

    return layer
