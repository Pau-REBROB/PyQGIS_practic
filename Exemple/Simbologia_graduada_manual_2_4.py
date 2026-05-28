"""SIMBOLITZACIÓ"""

"""SIMBOLOGIA GRADUADA"""

def simbologia_graduada_manual(layer, atribut, breaks, color_ramp):
    """
    Aplica simbologia graduada a una capa poligonal existent
    Es creen manualment els rangs de dades i s'interpola el color des d'una rampa de colors propis de QGIS
    No es modifica la simbologia dels polígons

    La funció:
        Clona la capa d'entrada
        Assigna un nom nou a la capa clonada
        Crea un grup de simbologia graduada 
        Genera simbologia especificant manualment el rang de valors i interpolant el color
    
    Paràmetres de la funció:
        layer : capa de tipus poligonal sobre la que aplicar la simbologia
        atribut : camp a representar
        breaks : llista de valors amb què es divideix el valor de l'atribut
        color_ramp : rampa de color d'estil QGIS
    """
    # Clonació de la capa d'entrada
    layer_clone = layer.clone()
    
    # Assignació d'un nou nom
    layer_clone.setName(f"{layer_clone.name()}_simbGradManual")
    
    # Addició de la capa al projecte
    project.addMapLayer(layer_clone, False)
    
    # Creació d'un grup de capes de simbologia única, si no existeix
    group = root.findGroup("Simbologia_graduada_manual")
    if not group:
        group = root.addGroup("Simbologia_graduada_manual")
    # Addició de la capa al grup
    group.addLayer(layer_clone)

    # S'estableix una variable de la rampa de colors passada com a argument
    rampa = QgsStyle().defaultStyle().colorRamp(color_ramp)

    # S'estableixen el nombre de salts de les dades, com al nombre d'intervals-1
    intervals = len(breaks)-1

    # Es defineix una llista buida que contindrà tots els rangs
    rangs = []

    # Iteració sobre la llista d'intervals per a crear cada rang
    for i in range(intervals):
        # Es defineix el constructor del símbol
        symbol = QgsFillSymbol()
        
        # S'estableix un color com el valor interpolat de la rampa de colors en funció del nombre d'intervals
        color = rampa.color(float(i)/(intervals-1) if intervals > 1 else 0)
        
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

    # Retorn de la capa amb la simbologia
    return layer_clone



if __name__ == '__main__':
    # Codi a executar quan es cridi des d'aquest mateix script

    # Desactivar la visibilitat de totes les capes importades
    for layer in project.mapLayers().values():
        node = root.findLayer(layer)
        if node:
            node.setItemVisibilityChecked(False)

    # Aplicació de la simbologia graduada a les capes
    ## La variable graduada serà el número de plantes per sobre el terra de l'element
    params_cadastre_grad_man = {
        'Edificis_part': {"atribut": 'numberOfFloorsAboveGround', "breaks": [0, 1, 3, 5, 10, 20, 100], "color_ramp": "Spectral"}
    }

    for layer in dict_layers["Cadastre"].values():
        # Comprovació que la capa existeix en el diccionari de paràmetres
        if layer.name() in params_cadastre_grad_man:
            # Assingació del conjunt de paràmetres de la capa a una nova variable més manejable
            p_layer = params_cadastre_grad_man[layer.name()]

            # Crida de la funció amb la nova variable de paràmetres
            simbologia_graduada_manual(layer, p_layer["atribut"], p_layer["breaks"], p_layer["color_ramp"])
        else:
            print(f"El diccionari de paràmetres no recull la capa {layer.name()}!")
      