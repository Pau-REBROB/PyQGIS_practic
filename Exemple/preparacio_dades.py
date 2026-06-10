"""NETEJA DE CAPES"""

# ELS CAMPS A MANTENIR ESTARIEN AL MAIN O CONFIGURACIÓ COM A DICCIONARI

# LA INSPECCIÓ ES FARIA EN EL MAIN??


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

# CADASTRE
# Diferència entre Adreces i Parcel·les i Edificis
# Camps a mantenir
camps_mantenir_cadastre = {
    'Edificis': ['gml_id', 'end', 'reference', 'localId', 'currentUse', 'numberOfDwellings', 'value'],
    # 'gml_id' codi de l'arxiu de cadastre
    # 'end' any de finalització de construcció
    # 'reference' referència del codi gml_id
    # 'localId' codi local
    # 'currentUse' ús actual
    # 'numberOfDwellings' número d'habitacions
    # 'value' valor del metre quadrat
    'Edificis_part': ['gml_id', 'localId', 'numberOfFloorsAboveGround', 'numberOfFloorsBelowGround'],
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



from qgis.core import QgsFeatureRequest, QgsProject, QgsVectorFileWriter, QgsVectorLayer

def netejar_capa(layer, camps):
    """
    Funció que elimina els camps especificats de la capa
    """

    # Clonació de la capa original per no modificar-la
    layer_clone = layer.materialize(QgsFeatureRequest())

    # Llista buida que contindrà els índex dels camps a eliminar
    index_eliminar = []

    # Cerca dels índexs dels camps a eliminar
    for i, field in enumerate(layer_clone.fields()):
        # Si el nom del camp no es troba a la llista de camps a mantenir passada com a paràmetre
        # Afegir el seu índex a la llista buida
        if field.name() not in camps:
            index_eliminar.append(i)
    
    # Edició de la capa i eliminació dels camps
    with edit(layer_clone):
        layer_clone.deleteAttributes(index_eliminar)
   
   
    return layer_clone


def desar_carregar_capa(layer_clone):
    """
    Funció que desa la capa neta per la funció `netejar_capa()` en un arxiu GPKG i carrega la capa al projecte
    """

    # Desat de la capa neta
    transform_context = QgsProject.instance().transformContext()
    
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.driverName = "GPKG"
    
    QgsVectorFileWriter.writeAsVectorFormatV3(layer_clone, 
                                              f"C:/projectes_git/Dades/PyQGIS_Repo/Dades_netes/{layer_clone.name()}_clean.gpkg", 
                                              transform_context, 
                                              save_options)

    # Importació de la capa al projecte
    layer_clean = QgsVectorLayer(f"C:/projectes_git/Dades/PyQGIS_Repo/Dades_netes/{layer_clone.name()}_clean.gpkg",
                                 layer_clone.name(),
                                 "ogr")

    return layer_clean 
    

def netejar_grup(dict_layers, configuracio):
    """
    Funció que genera un nou diccionari de capes netejades a partir de la funció `netejar_capa()`
    """

    for grup, capes in dict_layers.items():
        
        for nom, layer in capes.items():
            
            camps = configuracio[grup][nom]
            
            dict_layers[grup][nom] = netejar_capa(layer, camps) 

    return dict_layers
