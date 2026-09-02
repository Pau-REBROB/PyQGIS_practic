import config
import simbologia.simbologies as simbologies

def simbologia_edificis_industrials(edificis):
    """
    Aplica una simbologia categòrica als edificis
    segons el seu ús industrial o no.
    """

    layer = simbologies.simbologia_categorica(
        layer=edificis,
        **config.SIMBOLOGIA["Atles"]["Edificis"]
    )

    renderer = layer.renderer()

    for i, categoria in enumerate(renderer.categories()):
        valor = categoria.value()
        etiqueta = config.ETIQUETES_USOS.get(valor, valor)

        renderer.updateCategoryLabel(i, etiqueta)

    layer.triggerRepaint()
    
    layer.setName("Ús actual")
    
    return layer


def simbologia_districtes_atles(districtes):
    """
    Aplica una simbologia única als districtes.
    """

    layer = simbologies.simbologia_unica(
        layer=districtes,
        **config.SIMBOLOGIA["Atles"]["Districtes"]
    )

    return layer


def simbologia_us_predominant(zones, ua):
    """
    Aplica una simbologia categòrica a les unitats
    administratives segons el seu ús predominant.
    """

    layer = simbologies.simbologia_categorica(
        layer=zones,
        **config.SIMBOLOGIA["Us_predominant"][f"{ua}"]
    )

    renderer = layer.renderer()

    for i, categoria in enumerate(renderer.categories()):
        valor = categoria.value()
        etiqueta = config.ETIQUETES_USOS.get(valor, valor)

        renderer.updateCategoryLabel(i, etiqueta)

    layer.triggerRepaint()
    
    layer.setName("Ús_predominant")

    return layer


def simbologia_dominancia(zones, ua):
    """
    Aplica una simbologia graduada a les unitats
    administratives segons el grau de dominància funcional.
    """

    layer = simbologies.simbologia_graduada(
        layer=zones,
        **config.SIMBOLOGIA["Dominancia"][f"{ua}"]
    )

    renderer = layer.renderer()

    for i, rang in enumerate(renderer.ranges()):
        lower = round(rang.lowerValue(), 1)
        upper = round(rang.upperValue(), 1)

        renderer.updateRangeLabel(i, f"{lower:.1f} - {upper:.1f}%")

    layer.triggerRepaint()

    layer.setName("Dominancia")

    return layer


def simbologia_shannon(zones, ua):
    """
    Aplica una simbologia graduada a les unitats
    administratives segons l'índex de diversitat de Shannon.
    """

    layer = simbologies.simbologia_graduada(
        layer=zones,
        **config.SIMBOLOGIA["Shannon"][f"{ua}"]
    )

    renderer = layer.renderer()

    for i, rang in enumerate(renderer.ranges()):
        lower = round(rang.lowerValue(), 2)
        upper = round(rang.upperValue(), 2)

        renderer.updateRangeLabel(i, f"{lower:.2f} - {upper:.2f}")

    layer.triggerRepaint()

    layer.setName("Índex_shannon_norm")

    return layer


def simbologia_bivariant(zones, ua):
    """
    Aplica una simbologia categòrica a les unitats
    administratives segons una variable bivariant. 
    """

    layer = simbologies.simbologia_categorica(
            layer=zones,
            **config.SIMBOLOGIA["Bivariant"][f"{ua}"]
    )
        
    layer.setName("Classificació_bivariant")
    
    return layer
