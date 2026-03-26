"""Funcions de PyQGIS sobre Barcelona"""


"""INICIALITZACIÓ DEL PROJECTE"""

# Generar instància del projecte
project = QgsProject.instance()
# Generar instància del panell de capes
root = project.layerTreeRoot()



"""IMPORTACIÓ DE CAPES"""

# Capes al projecte
capes_lim_adm = {
    "Barris": "C:/PyQGIS_practic/Limits_administratius_BCN/0301040100_Barris_UNITATS_ADM.shp",
    "Districtes": "C:/PyQGIS_practic/Limits_administratius_BCN/0301040100_Districtes_UNITATS_ADM.shp",
    "TermeMunicipal": "C:/PyQGIS_practic/Limits_administratius_BCN/0301040100_TermeMunicipal_UNITATS_ADM.shp"
}
capes_graf_viari = {
    "Graf_trams": "C:/PyQGIS_practic/Graf_viari/BCN_GrafVial_Trams_ETRS89_SHP.shp",
    #"Graf_nodes": "C:/PyQGIS_practic/Graf_viari/BCN_GrafVial_Nodes_ETRS89_SHP.shp"
}
layers = {
    "Limits_administratius": {},
    "Graf": {}
}
indexs = {}

# Importació de les capes
# Generació dels índex espacials sobre les geometries de cada capa
## Límits administratius
for i, (nom, path) in enumerate(capes_lim_adm.items()):
    # Creació de la capa vectorial
    layer = QgsVectorLayer(path, nom, "ogr")
    # Comprovació que la capa és vàlida
    if not layer.isValid():
        print(f"Error al carregar la capa de {nom}!")
    else:
        # Addició de la capa al projecte
        project.addMapLayer(layer, False)
        # Inserció de la capa al panell de capes a la posició definida
        root.insertLayer(i, layer)
        # Addició de la capa al diccionari de capes
        # El key és el nom de la capa, i el value és la capa vectorial pròpiament (QgsVectorLayer)
        layers["Limits_administratius"][nom] = layer
        # Generació de l'índex i addició al diccionari d'índexs
        indexs[nom] = QgsSpatialIndex(layer.getFeatures())
## Graf viari
for i, (nom, path) in enumerate(capes_graf_viari.items()):
    # Creació de la capa vectorial
    layer = QgsVectorLayer(path, nom, "ogr")
    # Comprovació que la capa és vàlida
    if not layer.isValid():
        print(f"Error al carregar la capa de {nom}!")
    else:
        # Addició de la capa al projecte
        project.addMapLayer(layer, False)
        # Inserció de la capa al panell de capes a la posició definida
        root.insertLayer(i, layer)
        # Addició de la capa al diccionari de capes
        # El key és el nom de la capa, i el value és la capa vectorial pròpiament (QgsVectorLayer)
        layers["Graf"][nom] = layer
        # Generació de l'índex i addició al diccionari d'índexs
        indexs[nom] = QgsSpatialIndex(layer.getFeatures())



"""SISTEMES DE REFERÈNCIA"""

# Comprovació dels sistema de referència de coordenades del projecte i de les capes
print("SRC del projecte:", project.crs().authid())
for group in layers.values():
    for layer in group.values():
        print(f"SRC de la capa {layer.name()} és {layer.crs().authid()}")
        if layer.crs().authid() == project.crs().authid():
            print(f"La capa {layer.name()} i el projecte estan en el mateix SRC")
        else:
            print(f"La capa {layer.name()} està en el SRC {layer.crs().authid()} i necessita ser reprojectada!")



"""NETEJA DE CAPES"""

# LÍMITS ADMINISTRATIUS
# Les capes contenen molts camps (fins a 46!) que resulten innecessaris
layers["Limits_administratius"]['Barris'].fields().count()
# Totes tres capes contenen els mateixos 46 camps
layers["Limits_administratius"]['Barris'].fields().names()

# Camps a mantenir
camps_mantenir_limAdm = ['CONJ_DESCR', 'DISTRICTE', 'BARRI', 'PERIMETRE', 'AREA', 'TIPUS_UA', 'NOM']
# Camps a eliminar
for layer in layers["Limits_administratius"].values():
    # Llista buida que contindrà els índex dels camps a eliminar
    index_eliminar = []
    
    # Per cada capa, es busca els camps no coincidents amb la llista de camps a mantenir
    for i, field in enumerate(layer.fields()):
        # Si el nom del camp no es troba a la llista de camps a mantenir, afegeix el seu índex a la llista buida
        if field.name() not in camps_mantenir_limAdm:
            index_eliminar.append(i)
        else:
            print(f"Camp {field.name()} conservat")
    
    with edit(layer):
        layer.deleteAttributes(index_eliminar)

# Comprovació de l'eliminació
for layer in layers["Limits_administratius"].values():
    print(f"Número de camps presents a la capa {layer.name()}: {layer.fields().count()}")
    print(f"Camps presents: {layer.fields().names()}")

# GRAF VIARI
# Número de camps
layers["Graf"]['Graf_trams'].fields().count()
# Nom dels camps
layers["Graf"]['Graf_trams'].fields().names()

# Camps a mantenir
camps_mantenir_grafViari = ['COORD_X', 'COORD_Y', 'LONGITUD', 'ANGLE', 'C_Tram', 'Distric_D', 'NDistric_D', 'TVia_D', 'NVia_D', 'Distric_E', 'NDistric_E', 'TVia_E', 'NVia_E']
# Camps a eliminar
for layer in layers["Graf"].values():
    # Llista buida que contindrà els índex dels camps a eliminar
    index_eliminar = []
    
    # Per cada capa, es busca els camps no coincidents amb la llista de camps a mantenir
    for i, field in enumerate(layer.fields()):
        # Si el nom del camp no es troba a la llista de camps a mantenir, afegeix el seu índex a la llista buida
        if field.name() not in camps_mantenir_grafViari:
            index_eliminar.append(i)
        else:
            print(f"Camp {field.name()} conservat")
    
    with edit(layer):
        layer.deleteAttributes(index_eliminar)

# Comprovació de l'eliminació
for layer in layers["Graf"].values():
    print(f"Número de camps presents a la capa {layer.name()}: {layer.fields().count()}")
    print(f"Camps presents: {layer.fields().names()}")




"""SIMBOLITZACIÓ"""

# SÍMBOL ÚNIC
# Creació d'una funció per a aplicar simbologia única
def aplicar_simb_unica(layer, fill_color, outline_width, stroke_color):
    """
    Aplica una simbologia única a una capa poligonal existent
    
    Paràmetres de la funció:
        fill_color : color del farcit passat com a (R,G,B,Alpha)
        outline_width : gruix de la línia (0.26 per defecte)
        stroke_color : color de la línia de contorn passat com a string
    """
    #layer_clone = layer.clone()
    symbol = QgsFillSymbol()
    symbol.setColor(QColor(*fill_color))
    symbol_layer_0 = symbol.symbolLayer(0)
    symbol_layer_0.setStrokeWidth(outline_width)
    symbol_layer_0.setStrokeColor(QColor(stroke_color))
    
    layer.renderer().setSymbol(symbol)
    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())

# Aplicar la simbologia única a les capes
## Definició dels paràmetres de cada capa
params_limAdm = {
    'Barris': {"fill_color": (0,0,0,0), "outline_width": 0.2, "stroke_color": "black"},
    'Districtes': {"fill_color": (0,0,0,0), "outline_width": 0.4, "stroke_color": "black"},
    'TermeMunicipal': {"fill_color": (227,241,249,150), "outline_width": 0.6, "stroke_color": "black"}
}
## Aplicar la funció
for layer in layers["Limits_administratius"].values():
    # Comprovació que la capa existeix en el diccionari de paràmetres
    if layer.name() in params_limAdm:
        p_layer = params_limAdm[layer.name()]
        aplicar_simb_unica(layer, p_layer["fill_color"], p_layer["outline_width"], p_layer["stroke_color"])
    else:
        print(f"El diccionari de paràmetres no recull la capa {layer.name()}! Cal revisar-lo")

## GRAF VIARI
# Creació d'una funció per a aplicar simbologia única
def aplicar_simb_unica_linia(layer, fill_color, width, outline_color, outline_width):
    """
    Aplica una simbologia única a una capa linial existent
    
    Paràmetres de la funció:
        fill_color : color del farcit passat com a (R,G,B,Alpha)
        width : gruix de la línia base (0.26 per defecte)
        outline_color : color del contorn de la línia passat com a (R,G,B,Alpha)
        outline_width : gruix de la línia (0.26 per defecte)
    """
    #layer_clone = layer.clone()
    symbol = QgsLineSymbol()
    
    # Línia base
    linia_base = QgsSimpleLineSymbolLayer()
    linia_base.setColor(QColor(*fill_color))
    linia_base.setWidth(width)
    
    # Línia exterior
    linia_ext = QgsSimpleLineSymbolLayer()
    linia_ext.setColor(QColor(*outline_color))
    linia_ext.setWidth(outline_width)
    
    symbol.changeSymbolLayer(0, linia_ext)
    symbol.appendSymbolLayer(linia_base)
    
    layer.renderer().setSymbol(symbol)
    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())

# Aplicar la simbologia única a la capa
aplicar_simb_unica_linia(
    layers["Graf"]["Graf_trams"],
    (0,0,255,255),
    0.10,
    (200,200,200,255),
    0.3
)







# # Creació de grups per cada tipus de simbolització
# grup_original = root.addGroup("Capes originals")
# grup_original.addLayer(BcnBarris)
# grup_original.addLayer(BcnDistrictes)
# grup_original.addLayer(BcnTerme)

# grup_simb_unica = root.addGroup("Simbologia única")

# grup_simb_categorica = root.addGroup("Simbologia categòrica")

# grup_simb_graduada = root.addGroup("Simbologia graduada")

# grup_simb_regles = root.addGroup("Simbologia regles")





# # Modificació de la simbologia CATEGÒRICA de les capes
# ## Capa de barris
# BcnBarris_cat = BcnBarris.clone()
# print(BcnBarris_cat.fields().names())
# # Atribut categòric
# atribut = 'DISTRICTE'
# valors_atribut = sorted(set([feat[atribut] for feat in BcnBarris_cat.getFeatures()]))
# # Llista que contindrà les categories
# categories = []
# # Llista que conté els colors de cada categoria
# colors = ["red", "pink", "purple", "blue", "cian", "green", "yellow", "orange", "grey", "white"]
# # Iteració per cada atribut i cada color
# for valor, color in zip(valors_atribut, colors):
#     col = QColor(color)
#     symbol = QgsFillSymbol.createSimple({"color":col, "outline_color":QColor("grey"), "outline_width":0.3})
#     cat = QgsRendererCategory(valor, symbol, str(valor))
#     categories.append(cat)
# # Renderitzat
# renderer = QgsCategorizedSymbolRenderer(atribut, categories)
# BcnBarris_cat.setRenderer(renderer)
# BcnBarris_cat.triggerRepaint()
# # Afegir la capa al grup
# grup_simb_categorica.addLayer(BcnBarris_cat)
# # Actualitzar el panell de capes
# iface.layerTreeView().refreshLayerSymbology(BcnBarris_cat.id())

# ## Capa de districtes
# BcnDistrictes_cat = BcnDistrictes.clone()
# # Atribut categòric
# atribut = 'DISTRICTE'
# valors_atribut = sorted(set([feat[atribut] for feat in BcnDistrictes_cat.getFeatures()]))
# # Llista que contindrà les categories
# categories = []
# # Llista que conté els colors de cada categoria
# colors = ["red", "pink", "purple", "blue", "cian", "green", "yellow", "orange", "grey", "white"]
# # Iteració per cada atribut i cada color
# for valor, color in zip(valors_atribut, colors):
#     col = QColor(color)
#     symbol = QgsFillSymbol.createSimple({"color":col, "outline_color":QColor("grey"), "outline_width":0.5})
#     cat = QgsRendererCategory(valor, symbol, str(valor))
#     categories.append(cat)
# # Renderitzat
# renderer = QgsCategorizedSymbolRenderer(atribut, categories)
# BcnDistrictes_cat.setRenderer(renderer)
# BcnDistrictes_cat.triggerRepaint()
# # Afegir la capa al grup
# grup_simb_categorica.addLayer(BcnDistrictes_cat)
# # Actualitzar el panell de capes
# iface.layerTreeView().refreshLayerSymbology(BcnDistrictes_cat.id())


# # Modificació de la simbologia GRADUADA de les capes
# ## Capa de districtes
# BcnDistrictes_grad = BcnDistrictes.clone()
# # Atribut numèric graduat
# atribut = 'AREA'
# # Número de classes
# num_class = 5
# # Rampa de color
# color_ramp = QgsStyle().defaultStyle().colorRamp("Viridis")
# # Creació del renderitzat
# renderer = QgsGraduatedSymbolRenderer.createRenderer(
#     BcnDistrictes_grad,
#     atribut,
#     num_class,
#     QgsGraduatedSymbolRenderer.Jenks,
#     QgsSymbol.defaultSymbol(BcnDistrictes.geometryType()),
#     color_ramp
# )
# # Aplicar el renderitzat
# BcnDistrictes_grad.setRenderer(renderer)
# BcnDistrictes_grad.triggerRepaint()
# # Afegir la capa al grup
# grup_simb_graduada.addLayer(BcnDistrictes_grad)
# # Actualitzar el panell de capes
# iface.layerTreeView().refreshLayerSymbology(BcnDistrictes_grad.id())

# # Representació amb rangs definits, no per defecte
# ## Capa de districtes
# BcnDistrictes_grad2 = BcnDistrictes.clone()
# # Crear els colors
# colors = ["red", "purple", "blue", "green"]
# # Crear els itervals
# breaks = [1000000, 5000000, 10000000, 15000000, 25000000]
# # Crear els rangs
# rangs = []
# # Iterar sobre els colors
# for i in range(len(colors)):
#     symbol = QgsSymbol.defaultSymbol(BcnDistrictes_grad2.geometryType())
#     symbol.setColor(QColor(colors[i]))
#     #symbol = QgsFillSymbol.createSimple({"color":QColor(colors[i]), "outline_color":QColor("grey"), "outline_width":0.3})
#     range_ = QgsRendererRange(breaks[i], breaks[i+1], symbol, f"{breaks[i]}-{breaks[i+1]}")
#     rangs.append(range_)
# # Renderitzat
# renderer = QgsGraduatedSymbolRenderer(atribut, rangs)
# BcnDistrictes_grad2.setRenderer(renderer)
# BcnDistrictes_grad2.triggerRepaint()
# # Afegir la capa al grup
# grup_simb_graduada.addLayer(BcnDistrictes_grad2)
# # Actualitzar el panell de capes
# iface.layerTreeView().refreshLayerSymbology(BcnDistrictes_grad2.id())

# # Representació amb rangs definits i rampes de QGIS
# ## Capa de districtes
# BcnDistrictes_grad3 = BcnDistrictes.clone()
# # Crear la rampa de colors
# color_ramp = QgsStyle().defaultStyle().colorRamp("YlOrBr")
# # Crear els itervals
# breaks = [1000000, 5000000, 10000000, 15000000, 25000000]
# intervals = len(breaks)-1
# # Crear els rangs
# rangs = []
# # Iterar sobre els intervals
# for i in range(intervals):
#     symbol = QgsSymbol.defaultSymbol(BcnDistrictes_grad3.geometryType())
#     color = color_ramp.color(float(i)/(intervals-1))
#     symbol.setColor(color)
#     #symbol = QgsFillSymbol.createSimple({"color":QColor(colors[i]), "outline_color":QColor("grey"), "outline_width":0.3})
#     range_ = QgsRendererRange(breaks[i], breaks[i+1], symbol, f"{breaks[i]}-{breaks[i+1]}")
#     rangs.append(range_)
# # Renderitzat
# renderer = QgsGraduatedSymbolRenderer(atribut, rangs)
# BcnDistrictes_grad3.setRenderer(renderer)
# BcnDistrictes_grad3.triggerRepaint()
# # Afegir la capa al grup
# grup_simb_graduada.addLayer(BcnDistrictes_grad3)
# # Actualitzar el panell de capes
# iface.layerTreeView().refreshLayerSymbology(BcnDistrictes_grad3.id())


# # Modificació de la simbologia BASADA EN REGLES de les capes
# ## Capa de barris
# BcnBarris_rule = BcnBarris.clone()
# # Creació del símbol
# symbol_rule = QgsSymbol.defaultSymbol(BcnBarris_rule.geometryType())
# # Definició de les regles
# rule_1 = QgsRuleBasedRenderer.Rule(
#     symbol_rule.clone(),
#     filterExp = '("AREA"<500000) AND ("PERIMETRE"<30000)',
#     label = "Regla 1"
# )
# rule_2 = QgsRuleBasedRenderer.Rule(
#     symbol_rule.clone(),
#     filterExp = '("AREA">500000) AND ("PERIMETRE">30000)',
#     label = "Regla 2"
# )
# # rule_1 = QgsRuleBasedRenderer.Rule(symbol_rule.clone())
# # rule_1.setFilterExpression('("AREA"<500000) AND ("PERIMETRE"<30000)')
# # rule_1.setLabel("Rule 1")
# rule_1.symbol().setColor(QColor("lightgreen"))
# layer0_1 = rule_1.symbol().symbolLayer(0)
# layer0_1.setStrokeColor(QColor("green"))
# layer0_1.setStrokeWidth(0.4)
# #rule_1.symbol().set(QColor("green"))
# # rule_2 = QgsRuleBasedRenderer.Rule(symbol_rule.clone())
# # rule_2.setFilterExpression('("AREA">500000) AND ("PERIMETRE">30000)')
# # rule_2.setLabel("Regla 2")
# rule_2.symbol().setColor(QColor("lightblue"))
# layer0_2 = rule_2.symbol().symbolLayer(0)
# layer0_2.setStrokeColor(QColor("blue"))
# layer0_2.setStrokeWidth(0.4)
# #rule_2.symbol().setOutlineColor(QColor("blue"))
# # Definir el renderer i el root
# renderer = QgsRuleBasedRenderer(symbol_rule)
# root_rule = renderer.rootRule()
# # Eliminació de regles anteriors
# root_rule.removeChildAt(0)
# # Addició de les regles a l'arbre
# root_rule.appendChild(rule_1)
# root_rule.appendChild(rule_2)
# # Renderització
# BcnBarris_rule.setRenderer(renderer)
# BcnBarris_rule.triggerRepaint()
# # Afegir la capa al grup
# grup_simb_regles.addLayer(BcnBarris_rule)
# # Actualitzar el panell de capes
# iface.layerTreeView().refreshLayerSymbology(BcnBarris_rule.id())
