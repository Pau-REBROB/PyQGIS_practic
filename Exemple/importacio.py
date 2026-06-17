"""IMPORTACIÓ DE CAPES"""

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsSpatialIndex
)

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
        dict_layers.setdefault(grup, {})
        dict_indexs.setdefault(grup, {})
        
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


def carregar_basemap():
    """
    Funció per a carregar un mapa de fons
    """
    uri = ("type=xyz&url=https://basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png&zmax=19&zmin=0")

    layer = QgsRasterLayer(
        uri,
        "CartoDB Positron No Labels",
        "wms"
    )

    return layer