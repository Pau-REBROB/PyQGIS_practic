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
    QgsFeatureRequest,
    QgsExpression
)

import processing

import math

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
        Si la capa conté menys de dues entitats, retorna una llista buida.
    """
    # Validacions
    if not layer or not layer.isValid():
        raise ValueError(
            "La capa d'entrada no existeix o no és vàlida."
        )

    if layer.featureCount() < 2:
        raise ValueError(
            "Calen almenys dues entitats per calcular les distàncies"
            " al veí més proper."
        )

    if any(
        not feature.hasGeometry() or feature.geometry().isEmpty()
        for feature in layer.getFeatures()
    ):
        raise ValueError(
            "Totes les entitats han de tenir una geometria vàlida i no buida."
        )

    if not layer.crs().isValid() or layer.crs().isGeographic():
        raise ValueError(
            "La capa ha de tenir un SRC projectat per calcular les distàncies"
        )

    # Càlcul de distàncies
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


def distancia_k_vei(layer, k):
    """
    Calcula la distància de cada entitat al seu k-èsim veí més proper,
    a partir dels centroides de la capa.

    Pensada per construir un gràfic de colze (k-distance plot) com a
    mètode de suport per seleccionar el paràmetre `eps` de DBSCAN.
    Ordenant les distàncies de menor a major, el punt d'inflexió de
    la corba pot orientar la identificació d'un valor adequat de `eps`.

    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa vectorial sobre la qual es calculen les distàncies.
    k: int
        Nombre de veïns a considerar, normalment relacionat amb el
        paràmetre `min_size` de DBSCAN.

    Retorna
    -------
    list[float]
        Llista de distàncies al k-èsim veí, ordenada de menor a major.
        Les entitats sense prou veïns queden excloses.
    """
    # Validacions
    if not layer or not layer.isValid():
        raise ValueError(
            "La capa d'entrada no existeix o no és vàlida."
        )

    if layer.featureCount() < 2:
        raise ValueError(
            "Calen almenys dues entitats per calcular les distàncies"
            " al veí més proper."
        )

    if any(
            not feature.hasGeometry() or feature.geometry().isEmpty()
            for feature in layer.getFeatures()
        ):
            raise ValueError(
                "Totes les entitats han de tenir una geometria vàlida i no buida."
            )

    if not layer.crs().isValid() or layer.crs().isGeographic():
        raise ValueError(
            "La capa ha de tenir un SRC projectat per calcular les distàncies"
        )

    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise ValueError(
            "El paràmetre k ha de ser un enter positiu."
        )

    if k >= layer.featureCount():
        raise ValueError(
            "El valor de k no pot ser igual o superior al nombre d'entitats."
        )

    # Càlcul de distàncies
    index = QgsSpatialIndex(layer.getFeatures())
    
    distancies = []

    for feat in layer.getFeatures():
        centroide = feat.geometry().centroid()
        veins = index.nearestNeighbor(centroide.asPoint(), k + 1)

        if len(veins) > k:
            vei_k = layer.getFeature(veins[k])
            dist = centroide.distance(vei_k.geometry().centroid())
            distancies.append(dist)

    return sorted(distancies)


def filtrar_capa(layer, expressio):
    """
    Genera una nova capa en memòria amb les entitats que compleixen
    una expressió de filtratge de QGIS.

    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa vectorial sobre la qual s'aplica el filtratge.
    expressio: str
        Expressió de filtratge escrita amb la sintaxi d'expressions de QGIS.

    Retorna
    -------
    QgsVectorLayer
        Nova capa en memòria amb les entitats seleccionades.
    """
    # Validacions
    if not layer or not layer.isValid():
        raise ValueError(
            "La capa d'entrada no existeix o no és vàlida."
        )

    if not isinstance(expressio, str) or not expressio.strip():
        raise ValueError(
            "L'expressió de filtre no pot estar buida."
        )

    expressio_qgis = QgsExpression(expressio)

    if expressio_qgis.hasParserError():
        raise ValueError(
            f"L'expressió de filtre no és vàlida: "
            f"{expressio_qgis.parserErrorString()}"
        )

    camps_referenciats = expressio_qgis.referencedColumns()
    camps_existents = {camp.name() for camp in layer.fields()}

    camps_inexistents = camps_referenciats - camps_existents

    if camps_inexistents:
        raise ValueError(
            f"L'expressió fa referència a camps inexistents: "
            f"{', '.join(sorted(camps_inexistents))}"
        )

    # Aplicació del filtre
    request = QgsFeatureRequest().setFilterExpression(expressio)

    resultat = layer.materialize(request)

    if not resultat or not resultat.isValid():
        raise RuntimeError(
            "No s'ha pogut generar la capa filtrada."
        )

    return resultat


def clusters_dbscan(layer, eps, min_size):
    """
    Aplica l'algoritme DBSCAN als centroides de les entitats d'una capa
    vectorial per identificar agrupacions espacials.

    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa vectorial sobre la qual es calcula la clusterització
    eps: float
        Distància màxima entre dos centroides perquè es considerin veïns,
        expressada en les unitats del sistema de referència de la capa.
    min_size: int
        Nombre mínim de centroides necessaris per a formar un clúster.

    Retorna
    -------
    QgsVectorLayer
        Capa en memòria amb els centroides classificats en clústers i els
        camps CLUSTER_ID i CLUSTER_SIZE.
    """
    # Validacions de la capa
    if not layer or not layer.isValid():
        raise ValueError(
            "La capa d'entrada no existeix o no és vàlida."
        )

    if layer.featureCount() < 1:
        raise ValueError(
            "La capa d'entrada no conté cap entitat."
        )

    if not layer.crs().isValid() or layer.crs().isGeographic():
        raise ValueError(
            "La capa ha de tenir un CRS projectat per calcular distàncies."
        )

    if any(
        not feature.hasGeometry() or feature.geometry().isEmpty()
        for feature in layer.getFeatures()
    ):
        raise ValueError(
            "Totes les entitats han de tenir una geometria vàlida i no buida."
        )

    # Validacions dels paràmetres
    if (
        not isinstance(eps, (int, float))
        or isinstance(eps, bool)
        or not math.isfinite(eps)
        or eps <= 0
    ):
        raise ValueError(
            "El paràmetre eps ha de ser un nombre finit positiu."
        )

    if not isinstance(min_size, int) or isinstance(min_size, bool) or min_size < 1:
        raise ValueError(
            "El paràmetre min_size ha de ser un enter positiu."
        )
    
    # Generació dels centroides
    layer_centroides = processing.run("native:centroids", {
        'INPUT': layer,
        'ALL_PARTS': False,
        'OUTPUT': 'memory:'
    })["OUTPUT"]

    if not layer_centroides or not layer_centroides.isValid():
        raise RuntimeError(
            "No s'ha pogut generar una capa vàlida de centroides."
        )
    
    # Generació de clústers amb el mètode DBSCAN a partir dels centroides
    resultat_clusters = processing.run("native:dbscanclustering", {
        'INPUT': layer_centroides,
        'EPS': eps,        
        'MIN_SIZE': min_size,   
        'FIELD_NAME': 'CLUSTER_ID',
        'SIZE_FIELD_NAME': 'CLUSTER_SIZE',
        'OUTPUT': 'memory:'
    })

    capa_clusters = resultat_clusters["OUTPUT"]

    if not capa_clusters or not capa_clusters.isValid():
        raise RuntimeError(
            "L'algoritme DBSCAN no ha generat una capa vàlida."
        )
    
    return capa_clusters


def envolvent_clusters(layer):
    """
    Genera els polígons d'envolvent convexa que delimiten els clústers.

    La funció exclou els elements que no pertanyen a cap clúster identificat
    (classificats com a soroll per DBSCAN), calcula l'envolvent convexa de 
    cada agrupació i dissol les geometries resultants per obtenir-ne les zones
    delimitadores.

    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa de centroides classificada en clústers.

    Retorna
    -------
    QgsVectorLayer
        Capa poligonal en memòria amb les envolvents convexes que 
        delimiten els clústers.
    """
    # Validacions de la capa
    if not layer or not layer.isValid():
        raise ValueError("La capa d'entrada no existeix o no és vàlida.")

    if layer.featureCount() < 1:
        raise ValueError("La capa d'entrada no conté cap entitat.")

    if not layer.crs().isValid() or layer.crs().isGeographic():
        raise ValueError(
            "La capa ha de tenir un CRS projectat per calcular distàncies."
        )

    if any(
        not feature.hasGeometry() or feature.geometry().isEmpty()
        for feature in layer.getFeatures()
    ):
        raise ValueError(
            "Totes les entitats han de tenir una geometria vàlida i no buida."
        )

    if layer.fields().indexFromName("CLUSTER_ID") == -1:
        raise ValueError(
            "La capa ha de contenir el camp CLUSTER_ID."
        )
    
    # Filtratge dels clústers
    request = QgsFeatureRequest().setFilterExpression('"CLUSTER_ID" IS NOT NULL AND "CLUSTER_ID" != -1')
    
    layer_clusters_valids = layer.materialize(request)

    if not layer_clusters_valids or not layer_clusters_valids.isValid():
        raise RuntimeError(
            "No s'ha pogut generar la capa de clústers vàlids."
        )

    if layer_clusters_valids.featureCount() == 0:
        raise ValueError(
            "La capa no conté cap clúster identificat."
        )

    # Generació de les envolvents convexes per cada clúster
    resultat_hull = processing.run("qgis:minimumboundinggeometry", {
        'INPUT': layer_clusters_valids,
        'FIELD': 'CLUSTER_ID',
        'TYPE': 2,
        'OUTPUT': 'memory:'
    })

    layer_hull = resultat_hull['OUTPUT']

    if not layer_hull or not layer_hull.isValid():
        raise RuntimeError(
            "No s'ha pogut generar les envolvents convexes."
        )

    # Dissolució de les geometries de les envolents convexes per unificar-les
    resultat_dissolved = processing.run("native:dissolve", {
        'INPUT': resultat_hull['OUTPUT'],
        'FIELD': 'CLUSTER_ID',
        'SEPARATE_DISJOINT': True,
        'OUTPUT': 'memory:'
    })
    
    layer_zones = resultat_dissolved['OUTPUT']

    if not layer_zones or not layer_zones.isValid():
        raise RuntimeError(
            "No s'ha pogut generar la capa final d'envolvents."
        )

    return layer_zones


def generar_cluster(layer, expressio, eps, min_size):
    """
    Genera els clústers espacials i les seves zones envolvents 
    a partir dels centroides dels edificis i una expressió de filtratge.

    La funció filtra les entitats que compleixen amb una expressió,
    aplica una clusterització mitjançant DBSCAN als seus centroides i
    calcula les envolvents convexes dels clústers resultants.

    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa vectorial sobre la qual es realitza l'anàlisi.
    expressio: str
        Expressió de filtratge amb la sintaxi d'expressions de QGIS.
    eps: float
        Distància màxima entre centroides perquè es considerin veïns, en
        unitats del SRC.
    min_size: int
        Nombre mínim de centroides necessaris per a formar un clúster.

    Retorna
    -------
    dict
        Diccionari de dues capes amb l'estructura:
        {
            "clusters": QgsVectorLayer,
            "zones": QgsVectorLayer
        }

        on:
            - "clusters": centroides classificats per DBSCAN.
            - "zones": envolvents convexes dels clústers.
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

    layer_zones = envolvent_clusters(layer_clusters)

    return {
        "clusters": layer_clusters,
        "zones": layer_zones
    }



# =================================================================================
# Criteris de configuració de DBSCAN
# -----------------------------------------------
# Per identificar les zones de concentració industrial real (a diferència
# de naus disperses o aïllades), s'aplica l'algorisme DBSCAN (Density-Based
# Spatial Clustering of Applications with Noise) sobre els centroides dels
# edificis amb ús industrial.

# DBSCAN classifica cada edifici en un de tres grups:
#     - Punt nucli: té almenys min_size edificis veïns dins d'una
#       distància eps. Evidencia per si sol una zona de densitat suficient.
#     - Punt frontera: no compleix el llindar de densitat per ser nucli,
#       però es troba dins d'eps d'algun punt nucli, i s'hi incorpora
#       com a membre del mateix clúster.
#     - Soroll (CLUSTER_ID = -1): no compleix cap dels dos criteris
#       anteriors; queda exclòs de qualsevol clúster.

# Selecció dels paràmetres:
#     - eps (distància màxima entre veïns, en metres): s'ha calibrat a
#       partir d'un gràfic de distàncies al k-èsim veí més proper
#       (k-distance plot), comparant diversos valors candidats i
#       validant visualment que no es produïa fusió indeguda entre
#       zones industrials properes però diferenciades. Valor final: 200 m.
#     - min_size (nombre mínim d'edificis per formar un clúster): s'ha
#       fixat a 10, prioritzant la identificació de concentracions
#       industrials consolidades per sobre de bosses petites o naus
#       aïllades, d'acord amb l'objectiu de l'anàlisi.
 