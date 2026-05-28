"""NETEJA DE CAPES"""

# LÍMITS ADMINISTRATIUS
# Les capes contenen molts camps (fins a 46!) que resulten innecessaris
# Les tres capes del grup de Límits administratius contenen els mateixos 46 camps
# Número de camps
dict_layers["Limits_administratius"]['Barris'].fields().count()
# Nom dels camps
dict_layers["Limits_administratius"]['Barris'].fields().names()

# Camps a mantenir
camps_mantenir_limAdm = ['DISTRICTE', 'BARRI', 'PERIMETRE', 'AREA', 'TIPUS_UA', 'NOM']
  # 'DISTRICTE' codi del districte
  # 'BARRI' codi del barri
  # 'PERIMETRE' perímetre de la geometria
  # 'AREA' superfície de la geometria
  # 'TIPUS_UA' tipus d'unitat administrativa - indica si es tracta d'un barri, un districte o un terme municipal
  # 'NOM' nom de la unitat administrativa

# Camps a eliminar
for name, layer in dict_layers["Limits_administratius"].items():
    # Clonació de la capa per no modificar l'original
    layer_clone = layer.clone()

    # Llista buida que contindrà els índex dels camps a eliminar
    index_eliminar = []
    
    # Per cada capa del grup de Límits administratius, es busquen els seus camps i el seu índex
    for i, field in enumerate(layer_clone.fields()):
        # Si el nom del camp no es troba a la llista de camps a mantenir:
        # Afegir el seu índex a la llista buida a eliminar
        if field.name() not in camps_mantenir_limAdm:
            index_eliminar.append(i)
        else:
            print(f"Camp {field.name()} conservat")

    # Edició de la capa i eliminació del camp i els seus atributs
    with edit(layer_clone):
        layer_clone.deleteAttributes(index_eliminar)
    
    # Desat de la nova capa
    transform_context = project.transformContext()
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.driverName = "GPKG"
    QgsVectorFileWriter.writeAsVectorFormatV3(layer_clone, 
                                              f"C:/projectes_git/Dades/PyQGIS_Repo/Limits_administratius_BCN/{name}_clone.gpkg", 
                                              transform_context, 
                                              save_options) 
    
    # Eliminació de la capa original del projecte
    project.removeMapLayer(layer.id())
    
    # Actualització del diccionari amb la capa neta
    layer_clean = QgsVectorLayer(f"C:/projectes_git/Dades/PyQGIS_Repo/Limits_administratius_BCN/{name}_clone.gpkg", name, "ogr")
    dict_layers["Limits_administratius"][name] = layer_clean

# Comprovació de l'eliminació
for name, layer in dict_layers["Limits_administratius"].items():
    print(f"Número de camps presents a la capa {name} després de la neteja: {layer.fields().count()}")
    print(f"Camps presents: {layer.fields().names()}")


# CADASTRE
# Diferència entre Adreces i Parcel·les i Edificis
# Camps a mantenir
camps_mantenir_cadastre = {
    'Edificis': ['gml_id', 'localId', 'numberOfFloorsAboveGround', 'numberOfFloorsBelowGround'],
    # 'gml_id' codi de l'arxiu de cadastre
    # 'localId' codi local
    # 'numberOfFloorsAboveGround' número de pisos per sobre nivell de terra
    # 'numberOfFloorsBelowGround' número de pisos per sota terra
    'Parcelles': ['gml_id', 'areaValue', 'localId', 'nationalCadastralReference', 'pos'],
    # 'gml_id' codi de l'arxiu de cadastre
    # 'areaValue' valor del metre quadrat
    # 'localId' codi local
    # 'nationalCadastralReference' número de referència cadastral
    # 'pos' coordenades UTM
    'Illes': ['gml_id', 'areaValue', 'localId', 'nationalCadastralReference', 'pos']
}

# Camps a eliminar
for name, layer in dict_layers["Cadastre"].items():
    # Clonació de la capa per no modificar l'original
    layer_clone = layer.materialize(QgsFeatureRequest())

    # Llista buida que contindrà els índex dels camps a eliminar
    index_eliminar = []
    
    # Per cada capa del grup de Límits administratius, es busquen els seus camps i el seu índex
    for i, field in enumerate(layer_clone.fields()):
        # Si el nom del camp no es troba a la llista de camps a mantenir:
        # Afegir el seu índex a la llista buida a eliminar
        if field.name() not in camps_mantenir_cadastre[name]:
            index_eliminar.append(i)
        else:
            print(f"Camp {field.name()} conservat")

    # Edició de la capa i eliminació del camp i els seus atributs
    with edit(layer_clone):
        layer_clone.deleteAttributes(index_eliminar)
    
    # Desat de la nova capa
    transform_context = project.transformContext()
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.driverName = "GPKG"
    QgsVectorFileWriter.writeAsVectorFormatV3(layer_clone, 
                                              f"C:/projectes_git/Dades/PyQGIS_Repo/Cadastre/{name}_clone.gpkg", 
                                              transform_context, 
                                              save_options) 
    
    # Eliminació de la capa original del projecte
    project.removeMapLayer(layer.id())

    # Actualització del diccionari amb la capa neta
    layer_clean = QgsVectorLayer(f"C:/projectes_git/Dades/PyQGIS_Repo/Cadastre/{name}_clone.gpkg", name, "ogr")
    dict_layers["Cadastre"][name] = layer_clean


# Comprovació de l'eliminació
for name, layer in dict_layers["Cadastre"].items():
    print(f"Número de camps presents a la capa {name} després de la neteja: {layer.fields().count()}")
    print(f"Camps presents: {layer.fields().names()}")


# GRAF VIARI
# Número de camps
dict_layers["Graf"]['Graf_trams'].fields().count()
# Nom dels camps
dict_layers["Graf"]['Graf_trams'].fields().names()

# Camps a mantenir
camps_mantenir_grafViari = ['COORD_X', 'COORD_Y', 'LONGITUD', 'ANGLE', 'C_Tram', 'Distric_D', 'NDistric_D', 'TVia_D', 'NVia_D', 'Distric_E', 'NDistric_E', 'TVia_E', 'NVia_E']
    # 'COORD_X' coordenada UTM X
    # 'COORD_Y' coordenada UTM Y
    # 'LONGITUD' longitud de la via
    # 'ANGLE' angle de la via
    # 'C_Tram' codi del tram de via
    # 'Distric_D' codi districte de la part dreta
    # 'NDistric_D' nom districte de la part dreta
    # 'TVia_D' tipus de via de la part dreta
    # 'NVia_D' nom de la via de la part dreta
    # 'Distric_E' codi districte de la part esquerra
    # 'NDistric_E' nom districte de la part esquerra
    # 'TVia_E' tipus de via de la part esquerra
    # 'NVia_E'  nom de la via de la part esquerra

# Camps a eliminar
for name, layer in dict_layers["Graf"].items():
    layer_clone = layer.clone()

    index_eliminar = []
    
    for i, field in enumerate(layer_clone.fields()):
        if field.name() not in camps_mantenir_grafViari:
            index_eliminar.append(i)
        else:
            print(f"Camp {field.name()} conservat")
    
    with edit(layer_clone):
        layer_clone.deleteAttributes(index_eliminar)

    # Desat de la nova capa
    transform_context = project.transformContext()
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.driverName = "GPKG"
    QgsVectorFileWriter.writeAsVectorFormatV3(layer_clone, 
                                              f"C:/projectes_git/Dades/PyQGIS_Repo/Graf_viari/{name}_clone.gpkg", 
                                              transform_context, 
                                              save_options) 
    
    # Eliminació de la capa original del projecte
    project.removeMapLayer(layer.id())
    
    # Actualització del diccionari amb la capa neta
    layer_clean = QgsVectorLayer(f"C:/projectes_git/Dades/PyQGIS_Repo/Graf_viari/{name}_clone.gpkg", name, "ogr")
    dict_layers["Graf"][name] = layer_clean

# Comprovació de l'eliminació
for name, layer in dict_layers["Graf"].items():
    print(f"Número de camps presents a la capa {name} després de la neteja: {layer.fields().count()}")
    print(f"Camps presents: {layer.fields().names()}")


"""ADDICIÓ DE CAPES AL PROJECTE"""

# Addició de les capes al projecte en grups de capes
# Les capes han estat creades en ordre
for theme, group in reversed(dict_layers.items()):
    # Creació d'un grup de capes per cada temàtica, si no existeix
    group_theme = root.findGroup(theme)
    if not group_theme:
        group_theme = root.addGroup(theme)
    
    # Addició de les capes als grups
    for layer in group.values():
        # Addició de la capa al projecte, també
        project.addMapLayer(layer, False)
        group_theme.addLayer(layer)
 