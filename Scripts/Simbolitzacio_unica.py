"""SIMBOLITZACIÓ"""

# Colors disponibles a QGIS:
print(QColor.colorNames())

#['aliceblue', 'antiquewhite', 'aqua', 'aquamarine', 'azure', 
# 'beige', 'bisque', 'black', 'blanchedalmond', 'blue', 'blueviolet', 'brown', 'burlywood', 
# 'cadetblue', 'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan',
# 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkgrey', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray', 'darkslategrey', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue', 'dimgray', 'dimgrey', 'dodgerblue',
# 'firebrick', 'floralwhite', 'forestgreen', 'fuchsia',
# 'gainsboro', 'ghostwhite', 'gold', 'goldenrod', 'gray', 'green', 'greenyellow', 'grey',
# 'honeydew', 'hotpink', 
# 'indianred', 'indigo', 'ivory',
# 'khaki',
# 'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan', 'lightgoldenrodyellow', 'lightgray', 'lightgreen', 'lightgrey', 'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightslategrey', 'lightsteelblue', 'lightyellow', 'lime', 'limegreen', 'linen',
# 'magenta', 'maroon', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mintcream', 'mistyrose', 'moccasin',
# 'navajowhite', 'navy',
# 'oldlace', 'olive', 'olivedrab', 'orange', 'orangered', 'orchid',
# 'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'purple', 
# 'red', 'rosybrown', 'royalblue',
# 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'silver', 'skyblue', 'slateblue', 'slategray', 'slategrey', 'snow', 'springgreen', 'steelblue', 
# 'tan', 'teal', 'thistle', 'tomato', 'transparent', 'turquoise',
# 'violet', 
# 'wheat', 'white', 'whitesmoke', 
# 'yellow', 'yellowgreen']



# SÍMBOL ÚNIC
## LÍMITS ADMINISTRATIUS
# Creació d'una funció per a aplicar simbologia única
def simbologia_unica(layer, fill_color, outline_width, stroke_color):
    """
    Aplica una simbologia de símbol únic a una capa poligonal existent
    
    Paràmetres de la funció:
        layer : capa vectorial de tipus poligonal sobre la que aplicar la simbologia
        fill_color : color del farcit, passat com a (R,G,B,Alpha)
        outline_width : gruix de la línia de contorn (0.26 per defecte)
        stroke_color : color de la línia de contorn, passat com a (R,G,B,Alpha)
    """
    # Clonació de la capa d'entrada
    layer_clone = layer.clone()
    # Assignació d'un nou nom
    layer_clone.setName(f"{layer.name()}_simbUnica")
    # Addició de la capa al projecte
    project.addMapLayer(layer_clone, False)
    # Creació d'un grup de capes de simbologia única, si no existeix
    group = root.findGroup("Simbologia_única")
    if not group:
        group = root.addGroup("Simbologia_única")
    # Addició de la capa al grup
    group.addLayer(layer_clone)

    # Creació de l'objecte símbol
    symbol = QgsFillSymbol()
    # S'estableix el color de farcit
    symbol.setColor(QColor(*fill_color))
    # Accés a la capa més interna del símbol
    symbol_layer_0 = symbol.symbolLayer(0)
    # S'estableix el gruix i el color de la línia de contorn
    symbol_layer_0.setStrokeWidth(outline_width)
    symbol_layer_0.setStrokeColor(QColor(*stroke_color))

    # S'estableix el renderer de la capa i se li assigna el símbol creat
    layer_clone.renderer().setSymbol(symbol)
    # Actualització del llenç
    layer_clone.triggerRepaint()
    # Actualització del panell de capes
    iface.layerTreeView().refreshLayerSymbology(layer_clone.id())

# Aplicar la simbologia única a les capes
## Definició dels paràmetres de cada capa
params_limAdm = {
    'Barris': {"fill_color": (0,0,0,0), "outline_width": 0.2, "stroke_color": (0,0,0,255)},
    'Districtes': {"fill_color": (0,0,0,0), "outline_width": 0.4, "stroke_color": (0,0,0,255)},
    'TermeMunicipal': {"fill_color": (227,241,249,150), "outline_width": 0.6, "stroke_color": (0,0,0,255)}
}
## Aplicar la funció
for layer in layers["Limits_administratius"].values():
    # Comprovació que la capa del diccionari de capes existeix en el diccionari de paràmetres
    if layer.name() in params_limAdm:
        # Assingació del conjunt de paràmetres de la capa a una nova variable més manejable
        p_layer = params_limAdm[layer.name()]
        # Crida de la funció
        simbologia_unica(layer, p_layer["fill_color"], p_layer["outline_width"], p_layer["stroke_color"])
    else:
        print(f"El diccionari de paràmetres no recull la capa cridada {layer.name()}!")


## GRAF VIARI
# Creació d'una funció per a aplicar simbologia única
def simbologia_unica_linia(layer, fill_color, width, outline_color, outline_width):
    """
    Aplica una simbologia de símbol únic a una capa linial existent
    
    Paràmetres de la funció:
        layer : capa vectorial de tipus lineal sobre la que aplicar la simbologia
        fill_color : color del farcit, passat com a (R,G,B,Alpha)
        width : gruix de la línia base (0.26 per defecte)
        outline_color : color del contorn de la línia, passat com a (R,G,B,Alpha)
        outline_width : gruix de la línia externa (0.26 per defecte)
    """
    # Clonació de la capa d'entrada
    layer_clone = layer.clone()
    # Assignació d'un nou nom
    layer_clone.setName(f"{layer.name()}_simbUnica")
    # Addició de la capa al projecte
    project.addMapLayer(layer_clone, False)
    # Creació d'un grup de capes de simbologia única, si no existeix
    group = root.findGroup("Simbologia_única")
    if not group:
        group = root.addGroup("Simbologia_única")
    # Addició de la capa al grup, a la primera posició
    group.insertLayer(0, layer_clone)

    # Creació de l'objecte símbol
    symbol = QgsLineSymbol()
    
    # Creació de la línia base
    linia_base = QgsSimpleLineSymbolLayer()
    # S'estableix el seu color i gruix
    linia_base.setColor(QColor(*fill_color))
    linia_base.setWidth(width)
    
    # Creació de la línia exterior
    linia_ext = QgsSimpleLineSymbolLayer()
    # S'estableix el seu color i gruix
    linia_ext.setColor(QColor(*outline_color))
    linia_ext.setWidth(outline_width)

    # S'estableix la línia exterior com a símbol
    symbol.changeSymbolLayer(0, linia_ext)
    # S'afegeix al símbol la línia base per sobre
    symbol.appendSymbolLayer(linia_base)

    # S'estableix el renderer de la capa i se li assigna el símbol creat
    layer.renderer().setSymbol(symbol)
    # Actualització del llenç
    layer.triggerRepaint()
    # Actualització del panell de capes
    iface.layerTreeView().refreshLayerSymbology(layer.id())

# Aplicar la simbologia única a la capa
simbologia_unica_linia(
    layers["Graf"]["Graf_trams"],
    (0,0,255,180),
    0.10,
    (200,200,200,180),
    0.3
)
