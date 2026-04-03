"""SIMBOLITZACIÓ"""

# SIMBOLOGIA GRADUADA

## LÍMITS ADMINISTRATIUS
# Creació d'una funció per a aplicar simbologia graduada
# No es defineixen els rangs, sinó que s'utilitza un mètode de classificació propi de QGIS
def simbologia_graduada_1(layer, atribut, num_classes, color_ramp, mode):
    """
    Aplica simbologia graduada a una capa poligonal existent
    Utilitza un mètode de classificació i una rampa de colors propis de QGIS
    
    Paràmetres de la funció:
        layer : capa de tipus poligonal sobre la que aplicar la simbologia
        atribut : camp a representar
        num_classes : número de classes amb què es divideix el valor de l'atribut
        color_ramp : rampa de color d'estil QGIS
        mode : mètode de classificació de QGIS
    """
    # Clonació de la capa d'entrada
    layer_clone = layer.clone()
    # Assignació d'un nou nom
    layer_clone.setName(f"{layer.name()}_simbGrad")
    # Addició de la capa al projecte
    project.addMapLayer(layer_clone, False)
    # Creació d'un grup de capes de simbologia categòrica, si no existeix
    group = root.findGroup("Simbologia_graduada")
    if not group:
        group = root.addGroup("Simbologia_graduada")
    # Addició de la capa al grup
    group.addLayer(layer_clone)
    # Activar la visibilitat del grup i de les capes
    root.setItemVisibilityChecked(True)
    group.setItemVisibilityChecked(True)
    node = root.findLayer(layer_clone.id())
    if node:
        node.setItemVisibilityChecked(True)

    # Mètodes de classificació possibles
    mode_map = {
        "EqualInterval": QgsGraduatedSymbolRenderer.EqualInterval,
        "Quantile": QgsGraduatedSymbolRenderer.Quantile,
        "Jenks": QgsGraduatedSymbolRenderer.Jenks,
        "StdDev": QgsGraduatedSymbolRenderer.StdDev,
        "Pretty": QgsGraduatedSymbolRenderer.Pretty
    }

    # Creació del renderer graduat, amb els paràmetres entrats en la crida de la funció
    renderer = QgsGraduatedSymbolRenderer.createRenderer(
        layer,
        atribut,
        num_classes,
        mode_map[mode],
        QgsFillSymbol(),
        QgsStyle().defaultStyle().colorRamp(color_ramp)
    )
    # Aplicació del renderer a la capa
    layer.setRenderer(renderer)
    
    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())
