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
    QgsFeatureRequest,
    QgsProject,
    QgsVectorFileWriter,
    QgsVectorLayer, 
    edit
)

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
                layer_clone = preparar_capa(capa, camps)
                layer_clean = desar_i_carregar_capa(layer_clone)
            
            dict_layers[grup][nom] = layer_clean 

    return dict_layers
