"""INICIALITZACIÓ DEL PROJECTE"""

# Generar instància del projecte
project = QgsProject.instance()

# Generar instància del panell de capes
root = project.layerTreeRoot()


"""IMPORTACIÓ DE CAPES"""

# Diccionari de capes per temàtica 
# Nom de la capa: ruta absoluta
capes_lim_adm = {
    "Barris": "C:/projectes_git/Dades/PyQGIS_Repo/Limits_administratius_BCN/0301040100_Barris_UNITATS_ADM.shp",
    "Districtes": "C:/projectes_git/Dades/PyQGIS_Repo/Limits_administratius_BCN/0301040100_Districtes_UNITATS_ADM.shp",
    "TermeMunicipal": "C:/projectes_git/Dades/PyQGIS_Repo/Limits_administratius_BCN/0301040100_TermeMunicipal_UNITATS_ADM.shp"
}

capes_urb = {
    "Adreces": "C:/projectes_git/Dades/PyQGIS_Repo/Urbanisme/0501040100_Adreces_TXT.shp",
    "Parcelles": "C:/projectes_git/Dades/PyQGIS_Repo/Urbanisme/0601040100_Parcel·lari_POL_v.shp",
    "Illes": "C:/projectes_git/Dades/PyQGIS_Repo/Urbanisme/0601040100_Illes_POL_v.shp"
}

capes_graf_viari = {
    "Graf_trams": "C:/projectes_git/Dades/PyQGIS_Repo/Graf_viari/BCN_GrafVial_Trams_ETRS89_SHP.shp",
    #"Graf_nodes": "C:/projectes_git/Dades/PyQGIS_Repo/Graf_viari/BCN_GrafVial_Nodes_ETRS89_SHP.shp"
}

# Diccionari buit de diccionaris de capes per temàtica
# Temàtica: diccionari de capes
dict_layers = {
    "Limits_administratius": {},
    "Urbanisme": {},
    "Graf": {}
}

# Diccionari buit dels índex de les capes
dict_indexs = {}


# Importació de les capes al projecte i generació dels índex espacials sobre les geometries de cada capa
## Límits administratius
for i, (nom, path) in enumerate(capes_lim_adm.items()):
    
    # Creació de la capa vectorial amb la ruta i utilitzant el nom
    layer = QgsVectorLayer(path, nom, "ogr")
    
    # Comprovació que la capa és vàlida
    if not layer.isValid():
        print(f"Error al carregar la capa de {nom}!")
    else:
        # Addició de la capa al projecte, sense afegir-la al llenç
        project.addMapLayer(layer, False)
        
        # Inserció de la capa al panell de capes a la posició definida
        root.insertLayer(i, layer)
        
        # Addició de la capa al diccionari de diccionaris de capes, al grup de Límits administratius
        # El key és el nom de la capa, i el value és la capa vectorial pròpiament (QgsVectorLayer)
        dict_layers["Limits_administratius"][nom] = layer
        
        # Generació de l'índex i addició al diccionari d'índexs
        dict_indexs[nom] = QgsSpatialIndex(layer.getFeatures())

## Urbanisme
for i, (nom, path) in enumerate(capes_urb.items()):

    # Creació de la capa vectorial amb la ruta i utilitzant el nom
    layer = QgsVectorLayer(path, nom, "ogr")
    
    # Comprovació que la capa és vàlida
    if not layer.isValid():
        print(f"Error al carregar la capa de {nom}!")
    else:
        # Addició de la capa al projecte, sense afegir-la al llenç
        project.addMapLayer(layer, False)
       
        # Inserció de la capa al panell de capes a la posició definida
        root.insertLayer(i, layer)
       
        # Addició de la capa al diccionari de diccionaris de capes, al grup d'Urbanisme
        # El key és el nom de la capa, i el value és la capa vectorial pròpiament (QgsVectorLayer)
        dict_layers["Urbanisme"][nom] = layer
        
        # Generació de l'índex i addició al diccionari d'índexs
        dict_indexs[nom] = QgsSpatialIndex(layer.getFeatures())

## Graf viari
for i, (nom, path) in enumerate(capes_graf_viari.items()):

    # Creació de la capa vectorial amb la ruta i utilitzant el nom
    layer = QgsVectorLayer(path, nom, "ogr")
    
    # Comprovació que la capa és vàlida
    if not layer.isValid():
        print(f"Error al carregar la capa de {nom}!")
    else:
        # Addició de la capa al projecte, sense afegir-la al llenç
        project.addMapLayer(layer, False)
       
        # Inserció de la capa al panell de capes a la posició definida
        root.insertLayer(i, layer)
       
        # Addició de la capa al diccionari de diccionaris de capes, al grup de Graf viari
        # El key és el nom de la capa, i el value és la capa vectorial pròpiament (QgsVectorLayer)
        dict_layers["Graf"][nom] = layer
        
        # Generació de l'índex i addició al diccionari d'índexs
        dict_indexs[nom] = QgsSpatialIndex(layer.getFeatures())


"""SISTEMES DE REFERÈNCIA"""

# Comprovació dels sistema de referència de coordenades del projecte
print("SRC del projecte:", project.crs().authid())

# Comprovació dels sistema de referència de coordenades de les capes
for group in dict_layers.values():
    for layer in group.values():
        # Impresió per pantalla del SRC de cada capa, en codi EPSG
        print(f"El SRC de la capa {layer.name()} és {layer.crs().authid()}")
        
        # Comparació amb el SRC del projecte
        if layer.crs().authid() == project.crs().authid():
            print(f"La capa {layer.name()} i el projecte estan en el mateix SRC")
        else:
            print(f"La capa {layer.name()} està en el SRC {layer.crs().authid()} i necessita ser reprojectada a EPSG:25831!")

