"""SIMBOLOGIA GRADUADA"""
""" S'ELIMINA AQUEST I S'AGAFA EL 3 COM A MÈTODE QGIS I EL 2 COM A MANUAL AMB INTERPOLACIÓ O ELECCIO MANUAL DE COLORS"""

# Desactivar la visibilitat de totes les capes importades
for layer in project.mapLayers().values():
    root.findLayer(layer).setItemVisibilityChecked(False)


# Creació d'una funció per a aplicar simbologia graduada a elements de tipus poligon
# No es defineixen els rangs, sinó que s'utilitza un mètode de classificació propi de QGIS
# S'utilitzen, també, les rampes de colors pròpies de QGIS
def simbologia_graduada_QGIS(layer, atribut, num_classes, color_ramp, mode):
    """
    Aplica simbologia graduada a una capa poligonal existent
    Utilitza un mètode de classificació i una rampa de colors propis de QGIS
    No es modifica la simbologia dels polígons

    La funció:
        Clona la capa d'entrada
        Assigna un nom nou a la capa clonada
        Crea un grup de simbologia graduada 
        Genera simbologia especificant el mètode de classificació i la rampa de colors
    
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
    layer_clone.setName(f"{layer_clone.name()}_simbGradQGIS")
    
    # Addició de la capa al projecte
    project.addMapLayer(layer_clone, False)
    
    # Creació d'un grup de capes de simbologia única, si no existeix
    group = root.findGroup("Simbologia_graduada_QGIS")
    if not group:
        group = root.addGroup("Simbologia_graduada_QGIS")
    # Addició de la capa al grup
    group.addLayer(layer_clone)

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


# Aplicació de la simbologia graduada a les capes
## La variable graduada serà l'àrea de l'element
params_limAdm_grad = {
    'Barris': {"atribut": 'AREA', "num_classes": 5, "color_ramp": "Viridis", "mode": "Jenks"},
    'Districtes': {"atribut": 'AREA', "num_classes": 5, "color_ramp": "Blues", "mode": "EqualInterval"},
}

for layer in dict_layers["Limits_administratius"].values():
    # Comprovació que la capa existeix en el diccionari de paràmetres
    if layer.name() in params_limAdm_grad:
        # Assingació del conjunt de paràmetres de la capa a una nova variable més manejable
        p_layer = params_limAdm_grad[layer.name()]
        
        # Crida de la funció amb la nova variable de paràmetres
        simbologia_graduada_QGIS(layer, p_layer["atribut"], p_layer["num_classes"], p_layer["color_ramp"], p_layer["mode"])
    else:
        print(f"El diccionari de paràmetres no recull la capa {layer.name()}!")
    

