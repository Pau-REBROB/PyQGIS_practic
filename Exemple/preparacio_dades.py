"""
Preparació de dades
==================

Mòdul que agrupa les funcions de preparació de les capes vectorials del projecte.

Organització
------------

- Eliminació dels camps no necessaris.
- Emmagatzematge de les capes preparades.
- Construcció del conjunt de dades preparades.
"""

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsFeatureRequest,
    QgsProject,
    QgsSpatialIndex,
    QgsVectorFileWriter,
    QgsVectorLayer, 
    edit
)

import processing

import os

import config

def preparar_capa(layer, camps):
    """
    Prepara una capa vectorial eliminant els camps no necessaris.

    La funció crea una còpia de la capa original i
    elimina tots els atributs que no formen part de la llista de camps a conservar.

    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa vectorial d'entrada.

    camps: list[str]
        Llista de camps que s'han de conservar.

    Retorna
    -------
    QgsVectorLayer
        Nova capa en memòria amb únicament els camps a conservar especificats.
    """

    layer_clone = layer.materialize(QgsFeatureRequest())

    indexs_eliminar = []

    # Cerca dels índexs dels camps a eliminar
    for i, camp in enumerate(layer_clone.fields()):
        # Si el nom del camp no es troba a la llista de camps a mantenir passada com a paràmetre
        # Afegir el seu índex a la llista buida
        if camp.name() not in camps:
            indexs_eliminar.append(i)
    
    # Edició de la capa i eliminació dels camps
    with edit(layer_clone):
        layer_clone.deleteAttributes(indexs_eliminar)

    layer_clone.updateFields()

    return layer_clone


def reprojectar_capa(layer, crs_desti):
    """
    Reprojecta una capa vectorial a un sistema de referència de coordenades
    desitjat, si cal.

    Si la capa ja es troba en el CRS de destinació, es retorna com ha entrat,
    sense cap operació addicional.

    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa vectorial a reprojectar.
    crs_desti: str
        Codi EPSG de destinació (p. ex. "EPSG:25831").

    Retorna
    -------
    QgsVectorLayer
        Capa en el CRS de destinació (en memòria si calia reprojectar,
        o la mateixa capa d'entrada si ja hi era).
    """
    crs_desti_obj = QgsCoordinateReferenceSystem(crs_desti)

    if layer.crs() == crs_desti_obj:
        return layer

    resultat = processing.run("native:reprojectlayer", {
        'INPUT': layer,
        'TARGET_CRS': crs_desti_obj,
        'OUTPUT': 'memory:'
    })

    layer_reproj = resultat['OUTPUT']
    layer_reproj.setName(layer.name())

    return layer_reproj


def desar_i_carregar_capa(layer_clone):
    """
    Desa una capa preparada en format GeoPackage i la torna a carregar al projecte.

    Si l'arxiu ja existeix, no es torna a escriure i simplement es carrega des de local.
    """

    clean_path = f"{config.PATH_DADES_NETES}/{layer_clone.name()}_clean.gpkg"

    if not os.path.exists(clean_path):
        # Desat de la capa neta
        transform_context = QgsProject.instance().transformContext()
    
        save_options = QgsVectorFileWriter.SaveVectorOptions()
        save_options.driverName = "GPKG"
        save_options.layerName = layer_clone.name()
            
        QgsVectorFileWriter.writeAsVectorFormatV3(layer_clone,
                                                  clean_path, 
                                                  transform_context, 
                                                  save_options)
        
    else:
        print(f"La capa {layer_clone.name()} ja existeix")

    # Importació de la capa al projecte
    layer_clean = QgsVectorLayer(f"{config.PATH_DADES_NETES}/{layer_clone.name()}_clean.gpkg|layername={layer_clone.name()}",
                                 layer_clone.name(),
                                 "ogr")

    return layer_clean 
    

def preparar_grup(dict_layers, configuracio):
    """
    Prepara les capes d'un conjunt de dades.

    Per a cada capa:
        - selecciona els camps a conservar,
        - genera una capa preparada,
        - la desa en format GeoPackage,
        - la recarrega al projecte,
        - actualitza el diccionari de capes.

    Paràmetres
    ----------
    dict_layers: dict
        Diccionari de capes agrupades per temàtica amb l'estructura:
        {
            "Nom_grup": {
                "Nom_capa": QgsVectorLayer,
                ...
            },

            ...
        }

    configuracio: dict
        Diccionari que defineix els camps que s'han de conservar per a cada capa.

    Retorna
    -------
    dict
        Diccionari de capes amb la mateixa estructura que la capa d'entrada, però
        on cada capa ha estat substituïda per la seva versió preparada.
        {
            "Nom_grup": {
                "Nom_capa": QgsVectorLayer,
                ...
            },

            ...
        }
    """
    for grup, capes in dict_layers.items():
        
        for nom, capa in capes.items():

            clean_path = f"{config.PATH_DADES_NETES}/{nom}_clean.gpkg"

            if os.path.exists(clean_path):
                # Carregar capa directament sense netejar
                print(f"Carregant capa {nom} des del disc...")

                layer_clean = QgsVectorLayer(
                    f"{clean_path}|layername={nom}", nom, "ogr"
                )

            else:
                # Netejar, desar i carregar capa
                if nom in configuracio[grup]:
                    camps = configuracio[grup][nom]
                else:
                    camps = configuracio[grup]["*"]      

                layer_reproj = reprojectar_capa(
                    layer=capa,
                    crs_desti=config.SRC_PROJECTE
                )

                layer_clone = preparar_capa(layer_reproj, camps)
                layer_clean = desar_i_carregar_capa(layer_clone)
                print(f"Capa {nom} preparada i desada.")
            
            dict_layers[grup][nom] = layer_clean 

    return dict_layers


def crear_indexs(dict_layers):
    """
    Crea els índexs espacials per a totes les capes del projecte.

    Paràmetres
    ----------
    dict_layers: dict
        Diccionari de capes agrupades per temàtica.

    Retorna
    -------
    dict
        Diccionari d'índexs amb l'estructura:

        on:
            dict_indexs = {
                "Grup": {
                    "Nom_capa": QgsSpatialIndex,
                    ...
                },
                ...
            }
    """

    dict_indexs = {}

    for grup, capes in dict_layers.items():
        dict_indexs.setdefault(grup, {})

        for nom, layer in capes.items():
            dict_indexs[grup][nom] = QgsSpatialIndex(layer.getFeatures())

    return dict_indexs