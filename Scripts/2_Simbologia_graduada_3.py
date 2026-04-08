"""SIMBOLITZACIÓ"""

# SIMBOLOGIA GRADUADA

# Desactivar la visibilitat de totes les capes importades
root.setItemVisibilityCheckedRecursive(False)

## LÍMITS ADMINISTRATIUS
# Creació d'una funció per a aplicar simbologia graduada
# No es defineixen els rangs, sinó que s'utilitza un mètode de classificació propi de QGIS
# S'utilitzen les rampes de colors pròpies de QGIS
def simbologia_graduada_QGIS_2(layer, atribut, num_classes, color_ramp, mode, stroke_color, stroke_width):
    """
    Aplica simbologia graduada a una capa poligonal existent
    Utilitza un mètode de classificació i una rampa de colors propis de QGIS
    Es modifica la simbologia dels polígons
    
    Paràmetres de la funció:
        layer : capa de tipus poligonal sobre la que aplicar la simbologia
        atribut : camp a representar
        num_classes : número de classes amb què es divideix el valor de l'atribut
        color_ramp : rampa de color d'estil QGIS
        mode : mètode de classificació de QGIS
        stroke_color : color de la línia de contorn, passat com a string
        stroke_width : gruix de la línia de contorn (0.26 per defecte)
    """
    # Clonació de la capa d'entrada
    layer_clone = layer.clone()
    # Assignació d'un nou nom
    layer_clone.setName(f"{layer.name()}_simbGrad2")
    # Addició de la capa al projecte
    project.addMapLayer(layer_clone, False)
    # Creació d'un grup de capes de simbologia categòrica, si no existeix
    group = root.findGroup("Simbologia_graduada_2")
    if not group:
        group = root.addGroup("Simbologia_graduada_2")
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

    # Es defineix la simbologia, amb el color i el gruix del contorn
    symbol = QgsFillSymbol()
    symbol.symbolLayer(0).setStrokeColor(QColor(stroke_color))
    symbol.symbolLayer(0).setStrokeWidth(stroke_width)

    # S'estableix el renderer graduat de la capa, amb els paràmetres entrats en la crida de la funció
    renderer = QgsGraduatedSymbolRenderer.createRenderer(
        layer_clone,
        atribut,
        num_classes,
        mode_map[mode],
        symbol,
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
    'Barris': {"atribut": 'AREA', "num_classes": 6, "color_ramp": "Mako", "mode": "Pretty", "stroke_color": "white", "stroke_width": 0.25},
    'Districtes': {"atribut": 'AREA', "num_classes": 6, "color_ramp": "Cividis", "mode": "Pretty", "stroke_color": "white", "stroke_width": 0.45},
}

## Aplicar la funció
for layer in layers["Limits_administratius"].values():
    # Comprovació que la capa existeix en el diccionari de paràmetres
    if layer.name() in params_limAdm_grad:
        p_layer = params_limAdm_grad[layer.name()]
        simbologia_graduada_QGIS_2(layer, p_layer["atribut"], p_layer["num_classes"], p_layer["color_ramp"], p_layer["mode"], p_layer["stroke_color"], p_layer["stroke_width"])
    else:
        print(f"El diccionari de paràmetres no recull la capa {layer.name()}!")
