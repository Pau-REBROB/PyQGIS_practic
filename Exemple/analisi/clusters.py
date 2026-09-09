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

from qgis.core import (
    QgsSpatialIndex,
    QgsFeature,
    QgsFeatureRequest,
    QgsField,
    QgsVectorLayer
)
from qgis.PyQt.QtCore import QVariant

import hdbscan
import numpy as np
import processing

import config

def distancia_veins_propers(layer):
    """
    Calcula la distància de cada entitat al seu veí més proper, a partir
    dels centroides de la capa.

    Pensada com a pas exploratori previ a l'aplicació de DBSCAN: dona una
    referència numèrica de l'escala espacial típica entre elements, útil
    per triar un valor de partida raonable per al paràmetre `eps`.

    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa vectorial sobre la qual es calculen les distàncies.

    Retorna
    -------
    list[float]
        Llista de distàncies (una per entitat) al seu veí més proper.
        Les entitats sense cap veí (capa d'una sola entitat) queden excloses.
    """
    index = QgsSpatialIndex(layer.getFeatures())

    distancies = []

    for feat in layer.getFeatures():
        centroide = feat.geometry().centroid()
        veins = index.nearestNeighbor(centroide.asPoint(), 2)

        if len(veins) > 1:
            vei = layer.getFeature(veins[1])
            dist = centroide.distance(vei.geometry().centroid())
            distancies.append(dist)

    return distancies


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


def clusters_hdbscan(layer, min_size, min_samples=None):
    """
    Genera una capa de clústers aplicant l'algoritme HDBSCAN als centroides d'una capa.

    La funció genera primer els centroides de les entitats de la capa d'entrada,
    aplica l'algoritme HDBSCAN per identificar agrupacions espacials i retorna
    una capa amb els centroides classificats.

    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa vectorial sobre la qual es calcula la clusterització.
    min_size: int
        Nombre mínim de centroides necessaris per a formar un clúster.
    min_samples: int, optional
        Nombre mínim de mostres al voltant d'un punt per considerar-lo nucli.
        Per defecte igual a min_size.

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
    
    # Extreure coordenades i features
    features = list(layer_centroides.getFeatures())

    if not features:
        return layer_centroides

    coords = np.array([
        [f.geometry().asPoint().x(), f.geometry().asPoint().y()]
        for f in features
    ])

    # Aplicar HDBSCAN
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_size,
        min_samples=min_samples if min_samples else min_size,
        core_dist_n_jobs=1  # desactivar paral·lelisme
    )
    labels = clusterer.fit_predict(coords)

    # Capa mínima amb només CLUSTER_ID
    crs = layer_centroides.crs().authid()
    layer_result = QgsVectorLayer(f"Point?crs={crs}", "clusters_hdbscan", "memory")
    provider = layer_result.dataProvider()
    provider.addAttributes([QgsField("CLUSTER_ID", QVariant.Int)])
    layer_result.updateFields()

    # Afegir features amb el CLUSTER_ID assignat
    noves_features = []
    for feature, label in zip(features, labels):
        nova = QgsFeature(layer_result.fields())
        nova.setGeometry(feature.geometry())
        nova.setAttribute("CLUSTER_ID", int(label))
        noves_features.append(nova)

    provider.addFeatures(noves_features)

    return layer_result


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

    layer_clusters = clusters_dbscan(
        layer_filtrada,
        eps,
        min_size
    )

    # layer_clusters = clusters_hdbscan(
    #     layer=layer_filtrada,
    #     min_size=min_size,
    #     min_samples=min_samples
    # )

    layer_zones = envolvent_clusters(layer_clusters)

    return {
        "clusters": layer_clusters,
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

        # resultats_clusters[us] = generar_cluster(
        #     layer=layer,
        #     expressio=f'"currentUse" = \'{us}\'',
        #     min_size=config.CONFIG_ANALISI["Clusters"]["min_size"],
        #     min_samples=config.CONFIG_ANALISI["Clusters"]["min_samples"]
        # )

        resultats_clusters[us]["resum"] = resum_clusters(
            layer=resultats_clusters[us]["clusters"]
        )


    return resultats_clusters


def analisi_clusters_per_districtes(edificis, districtes, idx_districtes, us, config_districtes):
    """
    Genera clústers espacials per cada districte amb paràmetres específics.

    Per a cada districte:
        - Filtra els edificis que hi pertanyen espacialment.
        - Aplica l'algoritme DBSCAN amb paràmetres específics per districte.
        - Genera les envolvents dels clústers resultants.
    
    Paràmetres
    ----------
     edificis: QgsVectorLayer
        Capa vectorial dels edificis.
    districtes: QgsVectorLayer
        Capa vectorial dels districtes.
    idx_districtes: QgsSpatialIndex
        Índex espacial dels districtes.
    us: str
        Ús dels edificis a analitzar.
    config_districtes: dict
        Diccionari amb els paràmetres de clusterització per districte,
        amb l'estructura:
        {
            "Nom_districte": {
                "eps": float,
                "min_size": int
            },
            "default": {
                "eps": float,
                "min_size": int
            }
        }

    Retorna
    -------
    dict
        Diccionari amb els resultats per districte, amb l'estructura:
        {
            "Nom_districte": {
                "clusters": QgsVectorLayer,
                "zones": QgsVectorLayer,
                "resum": dict
            },
            ...
        }
    """

    resultats = {}

    for districte in districtes.getFeatures():
        nom = districte["NOM"]
        geom_districte = districte.geometry()

        # Filtrar edificis pel districte per ús
        edificis_districtes_features = [
            feat for feat in edificis.getFeatures(
                QgsFeatureRequest().setFilterRect(geom_districte.boundingBox())
            )
            if feat["currentUse"] == us
            and geom_districte.contains(feat.geometry().centroid())
        ]

        if not edificis_districtes_features:
            print(f"Districte {nom} sense cap edificis amb ús {us}")
            continue

        # Crear capa en memòria amb els edificis filtrats
        # wkb_type = QgsWkbTypes.displayString(edificis.wkbType())
        # layer_districte = QgsVectorLayer(
        #     f"{wkb_type}?crs={edificis.crs().authid()}",
        #     f"{nom}_{us}",
        #     "memory:"
        # )
        # provider = layer_districte.dataProvider()
        # provider.addAttributes(edificis.fields())
        # layer_districte.updateFields()
        # provider.addFeatures(edificis_districtes_features)
        layer_districte = edificis.materialize(
            QgsFeatureRequest().setFilterFids(
                [feat.id() for feat in edificis_districtes_features]
            )
        )
        layer_districte.setName(f"{nom}_{us}")

        # Paràmetres específics per districte o per defecte
        cfg = config_districtes.get(nom, config_districtes["default"])

        # Generar clústers
        resultats[nom] = generar_cluster(
            layer=layer_districte,
            expressio=f'"currentUse" = \'{us}\'',
            #eps=cfg["eps"],
            min_size=cfg["min_size"],
            min_samples=cfg["min_samples"]
        )

        resultats[nom]["resum"] = resum_clusters(
            layer=resultats[nom]["clusters"]
        )

    return resultats