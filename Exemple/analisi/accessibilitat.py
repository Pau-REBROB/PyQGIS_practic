from qgis.core import (
    QgsField,
    QgsFeatureRequest,
    QgsSpatialIndex,
    QgsVectorLayer
)

from PyQt5.QtCore import QVariant


import os
from statistics import median
import processing

import config


def generar_centroides_clusters(layer):
    """
    Genera els centroides d'una capa vectorial de clústers.
    
    Dissol els clústers a partir del seu identificador i crea
    una nova capa en memòria formada pels centroides de les
    geometries.
    
    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa vectorial de la qual es volen obtenir els centroides.

    Retorna
    -------
    QgsVectorLayer
        Capa vectorial dels centroides.
    """

    dissolucio = processing.run(
        "native:dissolve",
        {
            "INPUT": layer,
            "FIELD": ["CLUSTER_ID"],
            "OUTPUT": "memory:"
        }
    )

    centroids = processing.run(
        "native:centroids",
        {
            'INPUT': dissolucio['OUTPUT'],
            'ALL_PARTS': False,
            'OUTPUT': 'memory:'
        }
    )
    
    return centroids['OUTPUT']


def generar_isoarees(graf, points, strat, max_dist, interval):
    """
    Genera isoàrees de proximitat sobre la xarxa viària utilitzant
    el complement QNEAT3.

    La funció calcula àrees d'accessibilitat al voltant d'un conjunt de punts
    utilitzant el graf viari.

    Paràmetres
    ----------
    graf: QgsVectorLayer
        Capa vectorial del graf viari.
    points: QgsVectorLayer
        Capa vectorial de punts que defineixen els orígens.
    strat: int
        Estratègia de càlcul.
        0 - distància més curta.
        1 - temps més curt.
    max_dist: float
        Distància o temps màxim de càlcul.
    interval: float
        Interval de distància o temps entre isoàrees consecutives.
    
    Retorna
    -------
    QgsVectorLayer
        Capa vectorial amb les isoàrees generades.
    """

    output_interpolation = config.EXPORTACIO_ISOAREES["interpolation"]
    output_polygon = config.EXPORTACIO_ISOAREES["polygons"]

    # Netejar fitxers anteriors
    for path in [output_interpolation, output_polygon]:
        if os.path.exists(path):
            os.remove(path)


    processing.run(
        "qneat3:isoareaaspolygonsfromlayer",
        {
            'INPUT': graf,
            'START_POINTS': points,
            'ID_FIELD': "fid",
            'MAX_DIST': max_dist,
            'INTERVAL': interval,
            'STRATEGY': strat,
            'OUTPUT_INTERPOLATION': output_interpolation,
            'OUTPUT_POLYGONS': output_polygon
        }
    )

    layer_isoareas = QgsVectorLayer(
        output_polygon,
        "Isoarees",
        "ogr"
    )

    return layer_isoareas   


def analisi_accessibilitat(graf, origen, estrategia=0, distancia_max=5000, interval=250):
    """
    Calcula les isoàrees d'accessibilitat a partir d'una capa d'origen.

    La funció genera els centroides de la capa d'origen i crea les isoàrees
    sobre el graf viari utilitzant QNEAT3.

    Paràmetres
    ----------
    graf: QgsVectorLayer
        Capa vectorial del graf viari.
    origen: QgsVectorLayer
        Capa vectorial de punts que defineixen els orígens.
    estrategia: int
        Estratègia de càlcul.
        0 - distància més curta.
        1 - temps més curt.
    distancia_max: float
        Distància o temps màxim de càlcul.
    interval: float
        Interval de distància o temps entre isoàrees consecutives.
    
    Retorna
    -------
    QgsVectorLayer
        Capa vectorial amb les isoàrees generades.
    """

    centroides = generar_centroides_clusters(origen)

    isoarees = generar_isoarees(
        graf=graf,
        points=centroides,
        strat=estrategia,
        max_dist=distancia_max,
        interval=interval
    )

    return isoarees


def assignar_isoarees_a_edificis(edificis, isoarees):
    """
    Assigna a cada edifici el nivell d'accessibilitat corresponent
    a la isoàrea on es troba.

    Es crea l'índex espacial de les isoàrees i es copia el valor del
    camp 'cost_level' al nou camp 'accessibilitat' dels edificis.

    Paràmetres
    ----------
    edificis: QgsVectorLayer
        Capa vectorial dels edificis.
    isoarees: QgsVectorLayer
        Capa vectorial de les isoàrees.
    
    Retorna
    -------
    QgsVectorLayer
        Capa d'edificis amb el nou camp 'accessibilitat'.
    """

    # Crea la capa de sortida - còpia de la capa d'edificis
    layer = edificis.materialize(QgsFeatureRequest())

    provider = layer.dataProvider()

    provider.addAttributes([
        QgsField("accessibilitat", QVariant.Double)
    ])

    layer.updateFields()

    # Ús d'índexs espacials
    # Crea l'índex del camp accessibilitat d'edificis
    idx_accessibilitat = layer.fields().indexOf("accessibilitat")
    # Crea l'índex de les isoàrees
    idx_isoarea = QgsSpatialIndex(isoarees.getFeatures())

    # Crea un diccionari de cada isoàrea amb el seu id
    # per poder recuperar cada isoàrea
    dict_isoarees = {
        feat.id(): feat 
        for feat in isoarees.getFeatures()
    }

    layer.startEditing()

    canvis = {}

    # Per cada edifici:
    #   buscar les isoàrees candidates
    #   recuperar-les
    #   comprovar quines contenen l'edifici
    #   guardar el cost
    for feature in layer.getFeatures():
        geom = feature.geometry()
        centroide = geom.centroid()

        candidats = idx_isoarea.intersects(geom.boundingBox())

        costs = [
            dict_isoarees[c]["cost_level"]
            for c in candidats
            if dict_isoarees[c].geometry().contains(centroide)
        ]

        if costs:
            canvis[feature.id()] = {idx_accessibilitat: min(costs)}

    provider.changeAttributeValues(canvis)
    layer.commitChanges()

    return layer


# def afegir_accessibilitat_edificis(edificis, edificis_access):
#     """
#     Afegeix el valor d'accessibilitat als edificis a partir del 
#     seu identificador únic.

#     Paràmetres
#     ----------
#     edificis: QgsVectorLayer
#         Capa vectorial d'edificis que conté la informació funcional.
#     edificis_access: QgsVectorLayer
#         Capa vectorial d'edificis que conté el valor d'accessibilitat.

#     Retorna
#     -------
#     QgsVectorLayer
#         Capa vectorial d'edificis amb el valor d'accessibilitat incorporat.
#     """

#     layer = edificis.materialize(QgsFeatureRequest())

#     provider = layer.dataProvider()

#     provider.addAttributes([
#         QgsField("accessibilitat", QVariant.Int)
#     ])

#     layer.updateFields()

#     idx_accessibilitat = layer.fields().indexOf("accessibilitat")

#     # Diccionari id()-accessibilitat
#     dict_access = {
#         feature["fid"]: feature["accessibilitat"]
#         for feature in edificis_access.getFeatures()
#     }

#     layer.startEditing()

#     for feature in layer.getFeatures():
#         fid = feature["fid"]

#         if fid in dict_access:
#             feature[idx_accessibilitat] = dict_access[fid]
#             layer.updateFeature(feature)

#     layer.commitChanges()

#     return layer


def assignar_accessibilitat_per_hexagons(edificis, malla):
    """
    Agrega l'accessibilitat dels edificis a cada hexagon de la malla.

    Aprofita el camp 'hex_id' dels edificis per evitar un join espacial
    i fer un sol bucle sobre els edificis.

    Paràmetres
    ----------
    edificis: QgsVectorLayer
        Capa vectorial dels edificis amb el camp d'accessibilitat
    malla: QgsVectorLayer
        Capa vectorial de la malla hexagonal amb els camps de
        funcionalitat.
    
    Retorna
    -------
    QgsVectorLayer
        Capa vectorial de la malla hexagonal amb els resultats
        d'accessibilitat de cada hexagon.
    """

    # Agrupar els valors d'accessibilitat dels edificis
    # per hexagon
    # {
    #     id_hex1: [cost1, cost2...costN], # N edificis dins l'hexagon
    #     id_hex2: ...,
    #     ...
    # }
    hex_access = {}

    for edifici in edificis.getFeatures():
        hex_id = edifici["hex_id"]
        cost = edifici["accessibilitat"]

        if hex_id is None or cost is None:
            continue

        if hex_id not in hex_access:
            hex_access[hex_id] = []

        hex_access[hex_id].append(cost)

    # Crear la capa de sortida
    layer = malla.materialize(QgsFeatureRequest())

    provider = layer.dataProvider()

    provider.addAttributes([
        QgsField("accessibilitat", QVariant.Double)
    ])

    layer.updateFields()

    idx_access = layer.fields().indexOf("accessibilitat")

    # Escriure els resultats a la capa
    ## Per cada hexagon, recullir el seu índex
    ## comprovar que existeix en el diccionari anterior tret dels edificis
    ## d'aquest diccionari, obtenir el llistat de costos de l'hexagon
    ## establir el canvi en el diccionari de canvis com a
    ## id_hexagon: {id_camp_accessibilitat: mediana(cost)}
    ## Aplicar tots els canvis de cop
    layer.startEditing()

    canvis = {}

    for feature in layer.getFeatures():
        hex_id = feature["id"]

        if hex_id not in hex_access:
            continue

        costs = hex_access[hex_id]

        canvis[feature.id()] = {
            idx_access : median(costs)
        }

    provider.changeAttributeValues(canvis)
    layer.commitChanges()

    return layer