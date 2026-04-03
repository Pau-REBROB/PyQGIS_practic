"""SIMBOLITZACIÓ"""

# SIMBOLOGIA CATEGÒRICA

## LÍMITS ADMINISTRATIUS
# Creació d'una funció per a aplicar simbologia categòrica 
def aplicar_simb_categ(layer, atribut, colors, outline_width, stroke_color):
    """
    Aplica simbologia categòrica a una capa poligonal existent
    
    Paràmetres de la funció:
        atribut : camp a representar
        colors : llista de colors - passats com a string - que tindran les categories ## Es podria establir com a aleatori
        outline_width : gruix de la línia (0.26 per defecte)
        stroke_color : color de la línia de contorn passat com a string
    """
    
    valors_atribut = sorted(set([feat[atribut] for feat in layer.getFeatures()]))
    
    categories = []
    
    for valor, color in zip(valors_atribut, colors):
        col = QColor(color)
        symbol = QgsFillSymbol()
        symbol.setColor(QColor(col))
        symbol_layer_0 = symbol.symbolLayer(0)
        symbol_layer_0.setStrokeWidth(outline_width)
        symbol_layer_0.setStrokeColor(QColor(stroke_color))
          
        cat = QgsRendererCategory(valor, symbol, str(valor))
        categories.append(cat)
    
    renderer = QgsCategorizedSymbolRenderer(atribut, categories)
    layer.setRenderer(renderer)
    
    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())

# Aplicar la simbologia categòrica a les capes
## Definició dels paràmetres de cada capa
params_limAdm_cat = {
    'Barris': {"atribut": 'DISTRICTE', 
               "colors": ["lightsalmon", "lightpink", "lightcoral", "lightblue", "lightsteelblue", "limegreen", "lightyellow", "lightgoldenrodyellow", "lightgrey", "whitesmoke"],
               "outline_width": 0.2, "stroke_color": "black"},
    'Districtes': {"atribut": 'DISTRICTE', 
                   "colors": ['mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue'],
                   "outline_width": 0.4, "stroke_color": "black"},
}
## Aplicar la funció
for layer in layers["Limits_administratius"].values():
    # Comprovació que la capa existeix en el diccionari de paràmetres
    if layer.name() in params_limAdm_cat:
        p_layer = params_limAdm_cat[layer.name()]
        aplicar_simb_categ(layer, p_layer["atribut"], p_layer["colors"], p_layer["outline_width"], p_layer["stroke_color"])
    else:
        print(f"El diccionari de paràmetres no recull la capa {layer.name()}! Cal revisar-lo")
