"""SIMBOLITZACIÓ"""

# SIMBOLOGIA GRADUADA

## LÍMITS ADMINISTRATIUS
# Creació d'una funció per a aplicar simbologia graduada
# No es defineixen els rangs, sinó que s'utilitza un mètode de classificació propi de QGIS
def simbologia_graduada_QGIS(layer, atribut, num_classes, color_ramp, mode):
    """
    Aplica simbologia graduada a una capa poligonal existent
    Utilitza un mètode de classificació i una rampa de colors propis de QGIS
    No es modifica la simbologia dels polígons
    
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

    # S'estableix el renderer graduat de la capa, amb els paràmetres entrats en la crida de la funció
    renderer = QgsGraduatedSymbolRenderer.createRenderer(
        layer_clone,
        atribut,
        num_classes,
        mode_map[mode],
        QgsFillSymbol(),
        QgsStyle().defaultStyle().colorRamp(color_ramp)
    )
    # S'aplica a la capa el renderer creat
    layer_clone.setRenderer(renderer)
    # Actualització del llenç
    layer_clone.triggerRepaint()
    iface.mapCanvas().refresh()
    # Actualització del panell de capes
    iface.layerTreeView().refreshLayerSymbology(layer_clone.id())


# Aplicar la simbologia graduada a les capes
## Definició dels paràmetres de cada capa
params_limAdm_grad = {
    'Barris': {"atribut": 'AREA', "num_classes": 5, "color_ramp": "Viridis", "mode": "Jenks"},
    'Districtes': {"atribut": 'AREA', "num_classes": 5, "color_ramp": "Blues", "mode": "EqualInterval"},
}

## Aplicar la funció
for layer in layers["Limits_administratius"].values():
    # Comprovació que la capa existeix en el diccionari de paràmetres
    if layer.name() in params_limAdm_grad:
        p_layer = params_limAdm_grad[layer.name()]
        simbologia_graduada_QGIS(layer, p_layer["atribut"], p_layer["num_classes"], p_layer["color_ramp"], p_layer["mode"])
    else:
        print(f"El diccionari de paràmetres no recull la capa {layer.name()}!")
    

