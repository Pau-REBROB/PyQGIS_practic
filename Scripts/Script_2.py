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
