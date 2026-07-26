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

    renderer = layer.renderer()

    for i, categoria in enumerate(renderer.categories()):
        valor = categoria.value()
        etiqueta = config.ETIQUETES_USOS.get(valor, valor)

        renderer.updateCategoryLabel(i, etiqueta)

    layer.triggerRepaint()
    
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

    for i, rang in enumerate(renderer.ranges()):
        lower = round(rang.lowerValue(), 1)
        upper = round(rang.upperValue(), 1)

        renderer.updateRangeLabel(i, f"{lower:.1f} - {upper:.1f}%")

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

    for i, rang in enumerate(renderer.ranges()):
        lower = round(rang.lowerValue(), 2)
        upper = round(rang.upperValue(), 2)

        renderer.updateRangeLabel(i, f"{lower:.2f} - {upper:.2f}")

    layer.triggerRepaint()

    layer.setName("Districtes_shannon_norm")

    return layer


def simbologia_bivariant(districtes):
    """
    Aplica una simbologia categòrica als districtes
    segons una variable bivariant. 
    """

    layer = simbologies.simbologia_categorica(
            layer=districtes,
            **config.SIMBOLOGIA["Barris_bivariant"]
    )
    
    # renderer = layer.renderer()
    
    # for i, categoria in enumerate(renderer.categories()):
    #     valor = categoria.value()
    #     etiqueta = config.ETIQUETES_USOS.get(valor, valor)

    #     renderer.updateCategoryLabel(i, etiqueta)
    
    # layer.triggerRepaint()
        
    layer.setName("Districtes_bivariància")
    
    return layer
