"""
Importació de dades
===================

Mòdul que agrupa les funcions d'importació de les dades del projecte.

Organització
------------

- Importació de capes vectorials.
- Importació del mapa base.
"""

from qgis.core import (
    QgsProject,
    QgsRasterLayer,
    QgsSpatialIndex,
    QgsVectorLayer
)

def carregar_capes(layers):
    """
    Importa les capes vectorials del projecte i genera els seus índex espacials.

    Per a cada capa:
        - crea la capa vectorial,
        - comprova que sigui vàlida,
        - l'afegeix al projecte (sense mostrar-la al canvas),
        - genera el seu índex espacial,
        - comprova que el sistema de referència sigui EPSG:25831.

    Paràmetres
    ----------
    layers: dict
        Diccionari de capes amb l'estructura:
        {
            "Grup": {
                "Nom_capa": ruta,
                ...
            },

            ...
        }

    Retorna
    -------
    tupla
        (
            dict_layers,
            dict_indexs_espacials
        )
    
    on:
        dict_layers = {
            "Grup": {
                "Nom_capa": QgsVectorLayer
            }
        }

        dict_indexs_espacials = {
            "Grup": {
                "Nom_capa": QgsSpatialIndex
            }
        }
    """

    # Diccionari buit de diccionaris de capes per temàtica
    dict_layers = {}

    # Diccionari buit dels índex de les capes
    dict_indexs_espacials = {}

    for grup, grup_capes in layers.items():
        dict_layers.setdefault(grup, {})
        dict_indexs_espacials.setdefault(grup, {})
        
        for nom, path in grup_capes.items():
            layer = QgsVectorLayer(path, nom, "ogr")
            
            if not layer.isValid():
                print(f"Error al carregar la capa {nom}")
            
            else:
                # Addició de la capa al projecte - no al canvas
                QgsProject.instance().addMapLayer(layer, False)

                # Addició de la capa al diccionari de diccionaris de capes
                # Es crea un grup de capes amb el nom del grup
                # Per cada grup, el key és el nom de la capa, i el value és la capa vectorial pròpiament (QgsVectorLayer)
                dict_layers[grup][nom] = layer

                dict_indexs_espacials[grup][nom] = QgsSpatialIndex(layer.getFeatures())

                # Comparació amb el SRC del projecte
                if layer.crs().authid() == "EPSG:25831":
                    print(f"La capa {layer.name()} està en el SRC correcte")
                else:
                    print(f"La capa {layer.name()} està en el SRC {layer.crs().authid()} i necessita ser reprojectada a EPSG:25831!")


    return dict_layers, dict_indexs_espacials


def carregar_basemap():
    """
    Carrega el mapa base del projecte.

    Retorna
    -------
    QgsRasterLayer
        Capa ràster XYZ corresponent al mapa base CartoDB Positron No Labels.
    """
    uri = ("type=xyz&url=https://basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png&zmax=19&zmin=0")

    layer = QgsRasterLayer(
        uri,
        "CartoDB Positron No Labels",
        "wms"
    )

    return layer