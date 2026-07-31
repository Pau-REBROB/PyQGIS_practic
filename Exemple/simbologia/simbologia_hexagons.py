import config
import simbologia.simbologies as simbologies

def simbologia_us_predominant(hexagons):
    """
    Aplica una simbologia categòrica als hexàgons
    segons el seu ús predominant.
    """

    layer = simbologies.simbologia_categorica(
        layer=hexagons,
        **config.SIMBOLOGIA["Hexagons_us_predominant"]
    )

    renderer = layer.renderer()

    for i, categoria in enumerate(renderer.categories()):
        valor = categoria.value()
        etiqueta = config.ETIQUETES_USOS.get(valor, valor)

        renderer.updateCategoryLabel(i, etiqueta)

    layer.triggerRepaint()
    
    layer.setName("Hexagons_us_predominant")

    return layer


def simbologia_dominancia(hexagons):
    """
    Aplica una simbologia graduada als hexàgons
    segons el grau de dominància funcional.
    """

    layer = simbologies.simbologia_graduada(
        layer=hexagons,
        **config.SIMBOLOGIA["Hexagons_dominancia"]
    )

    renderer = layer.renderer()

    for i, rang in enumerate(renderer.ranges()):
        lower = round(rang.lowerValue(), 1)
        upper = round(rang.upperValue(), 1)

        renderer.updateRangeLabel(i, f"{lower:.1f} - {upper:.1f}%")

    layer.triggerRepaint()

    layer.setName("Hexagons_dominancia")

    return layer


def simbologia_shannon(hexagons):
    """
    Aplica una simbologia graduada als hexàgons
    segons l'índex de diversitat de Shannon.
    """

    layer = simbologies.simbologia_graduada(
        layer=hexagons,
        **config.SIMBOLOGIA["Districtes_shannon"]
    )

    renderer = layer.renderer()

    for i, rang in enumerate(renderer.ranges()):
        lower = round(rang.lowerValue(), 2)
        upper = round(rang.upperValue(), 2)

        renderer.updateRangeLabel(i, f"{lower:.2f} - {upper:.2f}")

    layer.triggerRepaint()

    layer.setName("Hexagons_shannon_norm")

    return layer