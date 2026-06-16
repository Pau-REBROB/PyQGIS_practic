"""ANÀLISI ESPACIAL"""

# Definició de funcions per a les diferents operacions d'anàlisi espacial

from qgis.core import (QgsFeatureRequest, QgsVectorLayer)
import processing

# 1 - Clusterització

def seleccio_atribut(layer, expressio):
    """
    Funció que aplica una selecció dels elements d'una capa passada com a argument segons una expressió passada com a argument 
    """
    
    # Generació de la consulta a partir de l'expressió argument
    request = QgsFeatureRequest().setFilterExpression(expressio)

    # Retorn dels elements de la capa que compleixen amb la condició, com a nova capa 
    return layer.materialize(request)


def clusters_dbscan(layer, eps, min_size):
    """
    Funció que a partir d'una capa vectorial genera els centroides dels seus elements i la seva agrupació en clústers
    Mètode de clusterització: DBSCAN
    Els paràmetres de la funció DBSCAN son introduïts com a paràmetres de la funció
    """

    # Generació dels centroides
    centroids = processing.run("native:centroids", {
        'INPUT': layer,
        'ALL_PARTS': False,
        'OUTPUT': 'memory:'
    })
    
    # Generació de clústers amb el mètode DBSCAN a partir dels centroides
    clusters = processing.run("native:dbscanclustering", {
        'INPUT': centroids['OUTPUT'],
        'EPS': eps,                 # 100 metres de distància màxima entre edificis
        'MINSIZE': min_size,        # mínim 5 edificis per formar un clúster
        'FIELD_NAME': 'CLUSTER_ID',
        'SIZE_FIELD_NAME': 'CLUSTER_SIZE',
        'OUTPUT': 'memory:'
    })
    
    return clusters['OUTPUT']


def envolvent_clusters(layer):
    """
    Funció que, prèviament a un filtratge dels clústers no nuls, genera la geometria mínima envolvent per cada clúster
    De la geometria resultant, s'uneixen i es disolen
    """

    # Filtratge dels clústers
    # Generació d'una consulta per filtrar la capa de clústers a aquells no nuls
    request_clusters = QgsFeatureRequest().setFilterExpression('"CLUSTER_ID" is not \'NULL\' AND "CLUSTER_ID" != -1')
    
    clusters_notNull = layer.materialize(request_clusters)

    # Generacio geometria mínima envolvent per cada clúster
    hull = processing.run("qgis:minimumboundinggeometry", {
        'INPUT': clusters_notNull,
        'FIELD': 'CLUSTER_ID',
        'TYPE': 2,
        'OUTPUT': 'memory:'
    })

    # Dissolució de les geometria de les envolents per unificar-les
    dissolved = processing.run("native:dissolve", {
        'INPUT': hull['OUTPUT'],
        'FIELD': [],
        'SEPARATE_DISJOINT': True,
        'OUTPUT': 'memory:'
    })
    
    # Desat del resultat en una capa
    layer_zones = dissolved['OUTPUT']

    return layer_zones

def zones_us(layer, expressio, eps, min_size):
    """
    Funció d'alt nivell que
        Selecciona d'una capa vectorial els elements que compleixen amb una condició en una nova capa
        Genera els seus centroides i aplica una anàlisi de clusterització DBSCAN
        Genera la geometria mínima envolent de cada clúster i dissol totes les geometries
    """

    layer_request = seleccio_atribut(layer, expressio)

    ##
    print("Selecció:", layer_request.featureCount())

    for f in layer_request.getFeatures():
        print(f.hasGeometry(), f.geometry().isNull())
        break
    ##


    clusters = clusters_dbscan(layer_request, eps, min_size)

    ##
    print("Clusters:", clusters.featureCount())

    for f in clusters.getFeatures():
        print(f.hasGeometry(), f.geometry().isNull())
        break
    ##

    layer_zones = envolvent_clusters(clusters)

    ##
    print("Zones:", layer_zones.featureCount())

    for f in layer_zones.getFeatures():
        print(f.hasGeometry(), f.geometry().isNull())
        break   
    ##

    return layer_zones


# 2 - Anàlisi de xarxes

def generacio_centroides(layer):
    """
    Funció per a generar centroides
    """

    centroids = processing.run("native:centroids", {
        'INPUT': layer,
        'ALL_PARTS': False,
        'OUTPUT': 'memory:'
    })
    
    return centroids['OUTPUT']

def isoarees_qneat3(graf_layer, points_layer, strat, max_dist, interval):
    """
    Funció d'alt nivell per generar isoàrees de proximitat a partir del plugin QNEAT3
    Es defineix com a paràmetes 
        Capa vectorial que conté el graf viari
        Capa vectorial amb els punts objectiu a la que s'aplica la funció `generacio_centroides()`
        Estratègia: 0 shortest path - 1 shortest time
        Distància màxima / Temps màxim
        Interval (metres o segons)
    """

    centroides = generacio_centroides(points_layer)

    processing.run("qneat3:isoareaaspolygonsfromlayer", {
        'INPUT': graf_layer,
        'START_POINTS': centroides,
        'ID_FIELD': "id",
        'MAX_DIST': max_dist, # 5000 DISTÀNCIA MÀXIMA
        'INTERVAL': interval,    # 100 interval
        'STRATEGY': strat, # 0 SHORTEST PATH
        'OUTPUT_INTERPOLATION': "C:/projectes_git/PyQGIS_practic/Resultats/output_interpolation.tif",
        'OUTPUT_POLYGONS': "C:/projectes_git/PyQGIS_practic/Resultats/output_polygons.shp"
        }
    )

    layer_isoareas = QgsVectorLayer(
        "C:/projectes_git/PyQGIS_practic/Resultats/output_polygons.shp",
        "Isoarees",
        "ogr"
    )

    return layer_isoareas   
    