"""INICIALITZACIÓ DEL PROJECTE"""

# Generar instància del projecte
project = QgsProject.instance()

# Generar instància del panell de capes
root = project.layerTreeRoot()



"""IMPORTACIÓ DE CAPES"""

# Diccionari de capes per temàtica amb el nom i la ruta
capes_lim_adm = {
    "Barris": "C:/PyQGIS_practic/Limits_administratius_BCN/0301040100_Barris_UNITATS_ADM.shp",
    "Districtes": "C:/PyQGIS_practic/Limits_administratius_BCN/0301040100_Districtes_UNITATS_ADM.shp",
    "TermeMunicipal": "C:/PyQGIS_practic/Limits_administratius_BCN/0301040100_TermeMunicipal_UNITATS_ADM.shp"
}

capes_graf_viari = {
    "Graf_trams": "C:/PyQGIS_practic/Graf_viari/BCN_GrafVial_Trams_ETRS89_SHP.shp",
    #"Graf_nodes": "C:/PyQGIS_practic/Graf_viari/BCN_GrafVial_Nodes_ETRS89_SHP.shp"
}

# Diccionari buit dels diccionaris de capes per temàtica
layers = {
    "Limits_administratius": {},
    "Graf": {}
}

# Diccionari buit dels índex de les capes
indexs = {}

# Importació de les capes al projecte i generació dels índex espacials sobre les geometries de cada capa
## Límits administratius
for i, (nom, path) in enumerate(capes_lim_adm.items()):
    # Per a cada nom i ruta del diccionari de capes de límits administratius:
    # Creació de la capa vectorial amb la ruta i utilitzant el nom
    layer = QgsVectorLayer(path, nom, "ogr")
    # Comprovació que la capa és vàlida
    if not layer.isValid():
        print(f"Error al carregar la capa de {nom}!")
    else:
        # Si la capa és vàlida:
        # Addició de la capa al projecte, sense afegir-la al llenç
        project.addMapLayer(layer, False)
        # Inserció de la capa al panell de capes a la posició definida
        root.insertLayer(i, layer)
        # Addició de la capa al diccionari de diccionaris de capes, al grup de Límits administratius
        # El key és el nom de la capa, i el value és la capa vectorial pròpiament (QgsVectorLayer)
        layers["Limits_administratius"][nom] = layer
        # Generació de l'índex i addició al diccionari d'índexs
        indexs[nom] = QgsSpatialIndex(layer.getFeatures())
## Graf viari
for i, (nom, path) in enumerate(capes_graf_viari.items()):
    # Per a cada nom i ruta del diccionari de capes del graf viari:
    # Creació de la capa vectorial amb la ruta i utilitzant el nom
    layer = QgsVectorLayer(path, nom, "ogr")
    # Comprovació que la capa és vàlida
    if not layer.isValid():
        print(f"Error al carregar la capa de {nom}!")
    else:
        # Si la capa és vàlida:
        # Addició de la capa al projecte, sense afegir-la al llenç
        project.addMapLayer(layer, False)
        # Inserció de la capa al panell de capes a la posició definida
        root.insertLayer(i, layer)
        # Addició de la capa al diccionari de diccionaris de capes, al grup de Graf viari
        # El key és el nom de la capa, i el value és la capa vectorial pròpiament (QgsVectorLayer)
        layers["Graf"][nom] = layer
        # Generació de l'índex i addició al diccionari d'índexs
        indexs[nom] = QgsSpatialIndex(layer.getFeatures())
