"""
Anàlisi espacial
================

Mòdul que agrupa les funcions d'anàlisi espacial del projecte.

Organització
------------

- Clústers
    Funcions per a la generació de clústers espacials d'edificis,
    obtenció de les seves envolvents i càlcul d'estadístiques.


Les funcions s'organitzen en tres nivells:
    - funcions bàsiques de processament;
    - funcions de resum dels resultats;
    - funcions d'alt nivell que orquestren el procés complet.
"""

from qgis.core import QgsFeatureRequest

import processing

import config


def filtrar_capa(layer, expressio):
    """
    Genera una nova capa en memòria amb les entitats que compleixen una expressió.

    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa vectorial sobre la qual s'aplica el filtratge.
    expressio: str
        Expressió de filtratge escrita amb la sintaxi d'expressions de QGIS.

    Retorna
    -------
    QgsVectorLayer
        Nova capa en memòria que conté únicament les entitats seleccionades.
    """
    
    request = QgsFeatureRequest().setFilterExpression(expressio)

    return layer.materialize(request)


def clusters_dbscan(layer, eps, min_size):
    """
    Genera una capa de clústers aplicant l'algoritme DBSCAN als centroides d'una capa.

    La funció genera primer els centroides de les entitats de la capa d'entrada i
    posteriorment aplica l'algoritme DBSCAN per identificar agrupacions espacials.

    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa vectorial sobre la qual es calcula la clusterització
    eps: float
        Distància màxima entre dos centroides perquè es considerin veïns.
    min_size: int
        Nombre mínim de centroides necessaris per a formar un clúster.

    Retorna
    -------
    QgsVectorLayer
        Capa en memòria amb els centroides classificats en clústers.
    """

    # Generació dels centroides
    layer_centroides = processing.run("native:centroids", {
        'INPUT': layer,
        'ALL_PARTS': False,
        'OUTPUT': 'memory:'
    })["OUTPUT"]
    
    # Generació de clústers amb el mètode DBSCAN a partir dels centroides
    resultat_clusters = processing.run("native:dbscanclustering", {
        'INPUT': layer_centroides,
        'EPS': eps,                 
        'MINSIZE': min_size,        
        'FIELD_NAME': 'CLUSTER_ID',
        'SIZE_FIELD_NAME': 'CLUSTER_SIZE',
        'OUTPUT': 'memory:'
    })
    
    return resultat_clusters["OUTPUT"]


def envolvent_clusters(layer):
    """
    Genera les zones - geometria mínima envolvent - que delimiten els clústers identificats.

    La funció elimina els elements que no pertanyen a cap clúster identificat,
    calcula la geometria mínima envolvent de cada agrupació i dissol
    les geometries resultants.

    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa de centroides classificada en clústers.

    Retorna
    -------
    QgsVectorLayer
        Capa en memòria amb les zones que delimiten els clústers.
    """

    # Filtratge dels clústers
    request = QgsFeatureRequest().setFilterExpression('"CLUSTER_ID" is not \'NULL\' AND "CLUSTER_ID" != -1')
    
    layer_clusters_valids = layer.materialize(request)

    # Generacio geometria mínima envolvent per cada clúster
    resultat_hull = processing.run("qgis:minimumboundinggeometry", {
        'INPUT': layer_clusters_valids,
        'FIELD': 'CLUSTER_ID',
        'TYPE': 2,
        'OUTPUT': 'memory:'
    })

    # Dissolució de les geometria de les envolents per unificar-les
    resultat_dissolved = processing.run("native:dissolve", {
        'INPUT': resultat_hull['OUTPUT'],
        'FIELD': [],
        'SEPARATE_DISJOINT': True,
        'OUTPUT': 'memory:'
    })
    
    layer_zones = resultat_dissolved['OUTPUT']

    return layer_zones


def generar_cluster(layer, expressio, eps, min_size):
    """
    Genera les agrupacions espacials corresponents a un ús determinat.

    La funció filtra les entitats que compleixen amb una expressió,
    aplica una clusterització mitjançant DBSCAN
    i calcula les zones que delimiten cada agrupació.

    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa vectorial sobre la qual es realitza l'anàlisi.
    expressio: str
        Expressió de filtratge.
    eps: float
        Distància màxima entre dos elements perquè es considerin veïns.
    min_size: int
        Nombre mínim d'elements per a formar un clúster.

    Retorna
    -------
    dict
        Diccionari de dues capes amb l'estructura:
        {
            "clusters": QgsVectorLayer,
            "zones": QgsVectorLayer
        }

        on:
            - "clusters": centroides classificats per clústers.
            - "zones": zones envolvents dels clústers.
    """

    layer_filtrada = filtrar_capa(
        layer,
        expressio
    )

    clusters = clusters_dbscan(
        layer_filtrada,
        eps,
        min_size
    )

    layer_zones = envolvent_clusters(clusters)

    return {
        "clusters": clusters,
        "zones": layer_zones
    }


def resum_clusters(layer):
    """
    Retorna el resum estadístic dels clústers d'una capa.

    A partir d'una capa de clústers obtinguda amb DBSCAN, calcula
    el nombre de clústers identificats, el nombre total d'elements agrupats,
    i la mida mínima, màxima i mitjana dels clústers.

    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa vectorial de centroides classificats en clústers.

    Retorna
    -------
    dict
        Diccionari amb les estadístiques resum dels clústers amb l'estructura:
        {
        "n_clusters": int,
        "n_edificis_totals": int,
        "max_edificis_cluster": int,
        "min_edificis_cluster": int,
        "mitjana_edificis_cluster": float
        }

        on:
        "n_clusters": nombre total de clústers,
        "n_edificis_totals": nombre total d'edificis inclosos en els clústers,
        "max_edificis_cluster": nombre màxim d'edificis inclosos en un clúster,
        "min_edificis_cluster": nombre mínim d'edificis inclosos en un clúster,
        "mitjana_edificis_cluster": mitjana del nombre d'edificis inclosos en els clústers
    """

    cluster_sizes = {}

    for feat in layer.getFeatures():
        cluster_id = feat["CLUSTER_ID"]
        cluster_size = feat["CLUSTER_SIZE"]

        if cluster_id is None or cluster_size is None:
            continue
        
        cluster_sizes[cluster_id] = cluster_size
    
    if not cluster_sizes:
        return {
            "n_clusters": 0,
            "n_edificis_totals": 0,
            "max_edificis_cluster": 0,
            "min_edificis_cluster": 0,
            "mitjana_edificis_cluster": 0
        }
    
    sizes = list(cluster_sizes.values())
    
    dict_resum = {
        "n_clusters": len(cluster_sizes),
        "n_edificis_totals": sum(sizes),
        "max_edificis_cluster": max(sizes),
        "min_edificis_cluster": min(sizes),
        "mitjana_edificis_cluster": sum(sizes)/len(cluster_sizes)
    }

    return dict_resum


def analisi_clusters(layer, usos):
    """
    Executa l'anàlisi de clústers per als diferents usos dels edificis.

    Per a cada ús:
        - filtra els edificis corresponents,
        - calcula els clústers espacials mitjançant l'algoritme DBSCAN,
        - genera les zones envolvents,
        - calcula el resum estadístic.

    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa vectorial dels edificis.
    usos: list[str]
        Llista dels usos que s'han d'analitzar.

    Retorna
    -------
    dict
        Diccionari amb els resultats de cada ús.

        {
        "1_residential": {
            "clusters": QgsVectorLayer,
            "zones": QgsVectorLayer,
            "resum": dict,
        },

        "2_agriculture": {
            ...
        },

        ...
        }
    """
    
    resultats_clusters = {}

    for us in usos:
        resultats_clusters[us] = generar_cluster(
            layer=layer,
            expressio=f'"currentUse" = \'{us}\'',
            eps=config.CONFIG_ANALISI["Clusters"]["eps"],
            min_size=config.CONFIG_ANALISI["Clusters"]["min_size"]
        )

        resultats_clusters[us]["resum"] = resum_clusters(
            layer=resultats_clusters[us]["clusters"]
        )


    return resultats_clusters
