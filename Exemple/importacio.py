"""IMPORTACIÓ DE CAPES"""

### RUTA I LAYERS AL MAIN - O A ARXIU DE CONFIGURACIÓ
# Rutes
path_dades = "C:/projectes_git/Dades/PyQGIS_Repo"

# Diccionari de capes per temàtica 
# Nom de la capa: ruta absoluta
layers = {
"Limits_administratius": {
    "Barris": f"{path_dades}/Limits_administratius_BCN/0301040100_Barris_UNITATS_ADM.shp",
    "Districtes": f"{path_dades}/Limits_administratius_BCN/0301040100_Districtes_UNITATS_ADM.shp",
    "TermeMunicipal": f"{path_dades}/Limits_administratius_BCN/0301040100_TermeMunicipal_UNITATS_ADM.shp"
},
"Cadastre": {
    "Edificis": f"{path_dades}/Cadastre/08900/A.ES.SDGC.BU.08900.building.gml",
    "Edificis_part": f"{path_dades}/Cadastre/08900/A.ES.SDGC.BU.08900.buildingpart.gml",
    "Parcelles": f"{path_dades}/Cadastre/08900/A.ES.SDGC.CP.08900.cadastralparcel.gml",
    "Illes": f"{path_dades}/Cadastre/08900/A.ES.SDGC.CP.08900.cadastralzoning.gml"
},
"Graf": {
    "Graf_trams": f"{path_dades}/Graf_viari/BCN_GrafVial_Trams_ETRS89_SHP.shp",
    #"Graf_nodes": f"{path_dades}/Graf_viari/BCN_GrafVial_Nodes_ETRS89_SHP.shp"
}}


from qgis.core import QgsProject, QgsVectorLayer, QgsSpatialIndex

def carregar_capes(layers):
    """
    Funció que, a partir d'un diccionari de capes - nom:ruta - retorna un diccionari de diccionaris de capes per temàtica
    La funció també retorna un diccionari equivalent d'índexs espacials

    Comprovació del SRC de cada capa importada
    """

    # Diccionari buit de diccionaris de capes per temàtica
    dict_layers = {}

    # Diccionari buit dels índex de les capes
    dict_indexs = {}

    for grup, capes in layers.items():
        for nom, path in capes.items():
            # Creació de la capa vectorial amb la ruta i el nom especificats
            layer = QgsVectorLayer(path, nom, "ogr")
            
            # Comprovació de la validesa de la capa creada
            if not layer.isValid():
                print(f"Error al carregar la capa {nom}")
            
            else:
                # Addició de la capa al projecte - no al canvas
                QgsProject.instance().addMapLayer(layer, False)

                # Addició de la capa al diccionari de diccionaris de capes
                # Es crea un grup de capes amb el nom del grup
                # Per cada grup, el key és el nom de la capa, i el value és la capa vectorial pròpiament (QgsVectorLayer)
                dict_layers[grup][nom] = layer

                # Generació de l'índex de cada capa i addició al diccionari d'índexs de manera anàloga a les capes
                dict_indexs[grup][nom] = QgsSpatialIndex(layer.getFeatures())

                # Impresió per pantalla del SRC de cada capa, en codi EPSG
                print(f"El SRC de la capa {layer.name()} és {layer.crs().authid()}")
        
                # Comparació amb el SRC del projecte
                if layer.crs().authid() == "EPSG:25831":
                    print(f"La capa {layer.name()} està en el SRC correcte")
                else:
                    print(f"La capa {layer.name()} està en el SRC {layer.crs().authid()} i necessita ser reprojectada a EPSG:25831!")


    return dict_layers, dict_indexs
