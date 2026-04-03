"""SIMBOLITZACIÓ"""

# SIMBOLOGIA GRADUADA

## LÍMITS ADMINISTRATIUS
# Creació d'una funció per a aplicar simbologia graduada
# No es defineixen els rangs, sinó que s'utilitza un mètode de classificació propi de QGIS
def simbologia_graduada_1(layer, atribut, num_classes, color_ramp, mode):
    """
    Aplica simbologia graduada amb estètica per defecte a una capa poligonal existent
    
    Paràmetres de la funció:
        atribut : camp a representar
        num_classes : número de classes de l'atribut
        color_ramp : rampa de color d'estil QGIS
        mode : mètode de classificació
    """
    
    mode_map = {
        "EqualInterval": QgsGraduatedSymbolRenderer.EqualInterval,
        "Quantile": QgsGraduatedSymbolRenderer.Quantile,
        "Jenks": QgsGraduatedSymbolRenderer.Jenks,
        "StdDev": QgsGraduatedSymbolRenderer.StdDev,
        "Pretty": QgsGraduatedSymbolRenderer.Pretty
    }
    
    renderer = QgsGraduatedSymbolRenderer.createRenderer(
        layer,
        atribut,
        num_classes,
        mode_map[mode],
        QgsFillSymbol(),
        QgsStyle().defaultStyle().colorRamp(color_ramp)
    )
    
    layer.setRenderer(renderer)
    
    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())
