"""INICIALITZACIÓ DEL PROJECTE"""

# Generar instància del projecte
project = QgsProject.instance()

# Generar instància del panell de capes
root = project.layerTreeRoot()



"""IMPORTACIÓ DE CAPES"""

# Diccionari de capes per temàtica amb el nom i la ruta
capes_lim_adm = {
    "Barris": "d:/47994558K/OneDrive - Generalitat de Catalunya/QGIS_TESTS/BARCELONA/Limits_Administratius/BCN_UNITATS_ADM_SHP/0301040100_Barris_UNITATS_ADM.shp",
    "Districtes": "d:/47994558K/OneDrive - Generalitat de Catalunya/QGIS_TESTS/BARCELONA/Limits_Administratius/BCN_UNITATS_ADM_SHP/0301040100_Districtes_UNITATS_ADM.shp",
    "TermeMunicipal": "d:/47994558K/OneDrive - Generalitat de Catalunya/QGIS_TESTS/BARCELONA/Limits_Administratius/BCN_UNITATS_ADM_SHP/0301040100_TermeMunicipal_UNITATS_ADM.shp"
}

capes_graf_viari = {
    "Graf_trams": "d:/47994558K/OneDrive - Generalitat de Catalunya/QGIS_TESTS/BARCELONA/Graf_viari/BCN_GrafVial_Trams_ETRS89_SHP.shp",
    #"Graf_nodes": "d:/47994558K/OneDrive - Generalitat de Catalunya/QGIS_TESTS/BARCELONA/Graf_viari/BCN_GrafVial_Nodes_ETRS89_SHP.shp"
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
