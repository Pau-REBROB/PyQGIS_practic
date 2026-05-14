"""SIMBOLITZACIÓ"""

# SIMBOLOGIA GRADUADA

# Desactivar la visibilitat de totes les capes importades
root.setItemVisibilityCheckedRecursive(False)

## LÍMITS ADMINISTRATIUS
# Creació d'una funció per a aplicar simbologia graduada
# No s'utilitza un mètode de classificació propi de QGIS, sinó que es creen els rangs manualment
# S'utilitzen les rampes de colors pròpies de QGIS fent una interpolació per a determinar el color corresponent
def simbologia_graduada_manual(layer, atribut, breaks, color_ramp):
    """
    Aplica simbologia graduada a una capa poligonal existent
    Es creen manualment els rangs de dades i s'interpola el color des d'una rampa de colors propis de QGIS
    No es modifica la simbologia dels polígons
    
    Paràmetres de la funció:
        layer : capa de tipus poligonal sobre la que aplicar la simbologia
        atribut : camp a representar
        breaks : llista de valors amb què es divideix el valor de l'atribut
        color_ramp : rampa de color d'estil QGIS
    """
    # Clonació de la capa d'entrada
    layer_clone = layer.clone()
    # Assignació d'un nou nom
    layer_clone.setName(f"{layer.name()}_simbGradManual")
    # Addició de la capa al projecte
    project.addMapLayer(layer_clone, False)
    # Creació d'un grup de capes de simbologia categòrica, si no existeix
    group = root.findGroup("Simbologia_graduada_manual")
    if not group:
        group = root.addGroup("Simbologia_graduada_manual")
    # Addició de la capa al grup
    group.addLayer(layer_clone)
    # Activar la visibilitat del grup i de les capes
    root.setItemVisibilityChecked(True)
    group.setItemVisibilityChecked(True)
    node = root.findLayer(layer_clone.id())
    if node:
        node.setItemVisibilityChecked(True)

    # S'estableix una variable de la rampa de colors passada com a argument
    rampa = QgsStyle().defaultStyle().colorRamp(color_ramp)

    # S'estableixen el nombre de salts de les dades, com al nombre d'intervals-1
    intervals = len(breaks)-1

    # Es defineix una llista buida que contindrà tots els rangs
    rangs = []

    # Iteració sobre la llista d'intervals per a crear cada rang
    for i in range(intervals):
        # Es defineix l'objecte del símbol
        symbol = QgsFillSymbol()
        # S'estableix un color com el valor interpolat de la rampa de colors en funció del nombre d'intervals
        color = rampa.color(float(i)/(intervals-1))
        # Es defineix el color del símbol
        symbol.setColor(color)
        # Es crea el rang per l'interval de dades iterat
        range_i = QgsRendererRange(breaks[i], breaks[i+1], symbol, f"{breaks[i]}-{breaks[i+1]}")
        # S'afegeix el rang a la llista de rangs
        rangs.append(range_i)

    # Es crea el renderer graduat amb l'atribut i el llistat de rangs
    renderer = QgsGraduatedSymbolRenderer(atribut, rangs)
    # S'aplica a la capa el renderer creat
    layer_clone.setRenderer(renderer)
    # Actualització del llenç
    layer_clone.triggerRepaint()
    iface.mapCanvas().refresh()
    # Actualització del panell de capes
    iface.layerTreeView().refreshLayerSymbology(layer_clone.id())


# Aplicar la simbologia graduada a les capes
## Definició dels paràmetres de cada capa
params_limAdm_grad2 = {
    'Barris': {"atribut": 'AREA', "breaks": [100000, 500000, 1000000, 2000000, 5000000, 15000000], "color_ramp": "Spectral"},
    'Districtes': {"atribut": 'AREA', "breaks": [4000000, 8000000, 12000000, 15000000, 20000000, 25000000], "color_ramp": "YlGnBu"},
}

## Aplicar la funció
for layer in layers["Limits_administratius"].values():
    # Comprovació que la capa existeix en el diccionari de paràmetres
    if layer.name() in params_limAdm_grad2:
        p_layer = params_limAdm_grad2[layer.name()]
        simbologia_graduada_manual(layer, p_layer["atribut"], p_layer["breaks"], p_layer["color_ramp"])
    else:
      print(f"El diccionari de paràmetres no recull la capa {layer.name()}!")
      
