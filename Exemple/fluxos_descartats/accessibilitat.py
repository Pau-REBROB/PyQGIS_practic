from qgis.core import (
    QgsField,
    QgsFeatureRequest,
    QgsGeometry,
    QgsProcessing,
    QgsSpatialIndex
)

from PyQt5.QtCore import QVariant

import analisi.clusters as clusters

from statistics import median
import processing

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


def generar_isoarees(graf, points, strat, max_dist, interval, tolerance=100):
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
    tolerance: float
        Distància màxima (en unitats del CRS) per "lligar" cada punt
        d'origen al node/aresta més proper de la xarxa viària. QNEAT3
        fa aquest ajust internament; cal indicar-lo explícitament perquè
        centroides que no cauen exactament sobre la xarxa (habitual amb
        clústers grans, on el centroide pot quedar dins d'un pati o
        illa d'edificis) es puguin connectar igualment al graf.
    
    Retorna
    -------
    QgsVectorLayer
        Capa vectorial amb les isoàrees generades.
    """
    resultat = processing.run(
        "qneat3:isoareaaspolygonsfromlayer",
        {
            'INPUT': graf,
            'START_POINTS': points,
            'ID_FIELD': "CLUSTER_ID",
            'MAX_DIST': max_dist,
            'INTERVAL': interval,
            'STRATEGY': strat,
            'TOLERANCE': tolerance,
            'OUTPUT_INTERPOLATION': QgsProcessing.TEMPORARY_OUTPUT,
            'OUTPUT_POLYGONS': QgsProcessing.TEMPORARY_OUTPUT
        }
    ) 

    layer_isoareas = resultat["OUTPUT_POLYGONS"]

    layer_isoareas.setName("Isoàrees")

    return layer_isoareas   


def analisi_accessibilitat(graf, origen, distancia_max, interval, estrategia=0):
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
    tolerancia: float
        Distància màxima (en unitats del CRS) per "lligar" cada punt
        d'origen al node/aresta més proper de la xarxa viària.
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


def analisi_accessibilitat_individual(graf, origen, distancia_max, interval, estrategia=0):
    """
    Calcula les isoàrees d'accessibilitat de manera independent per a
    cada clúster present a la capa d'origen.

    A diferència de analisi_accessibilitat, que calcula un únic mapa
    de cost amb tots els orígens competint entre si (com un diagrama
    de Voronoi de cost), aquesta funció executa QNEAT3 una vegada per
    clúster, evitant que la proximitat entre clústers veïns talli
    o fragmenti les seves isoàrees respectives.

    Paràmetres
    ----------
    graf: QgsVectorLayer
        Capa vectorial del graf viari.
    origen: QgsVectorLayer
        Capa vectorial de punts (amb camp CLUSTER_ID) que defineixen
        els clústers a analitzar.
    estrategia: int
        Estratègia de càlcul.
        0 - distància més curta.
        1 - temps més curt.
    tolerancia: float
        Distància màxima (en unitats del CRS) per "lligar" cada punt
        d'origen al node/aresta més proper de la xarxa viària.
    distancia_max: float
        Distància o temps màxim de càlcul.
    interval: float
        Interval de distància o temps entre isoàrees consecutives.

    Retorna
    -------
    dict
        Diccionari { cluster_id: QgsVectorLayer } amb les isoàrees
        calculades de manera independent per a cada clúster.
    """
    cluster_ids = {
        feat["CLUSTER_ID"]
        for feat in origen.getFeatures()
        if feat["CLUSTER_ID"] is not None and feat["CLUSTER_ID"] != -1
    }

    resultats = {}

    for cluster_id in cluster_ids:
        origen_cluster = clusters.filtrar_capa(origen, f'"CLUSTER_ID" = {cluster_id}')

        isoarees = analisi_accessibilitat(
            graf=graf,
            origen=origen_cluster,
            estrategia=estrategia,
            distancia_max=distancia_max,
            interval=interval
        )

        resultats[cluster_id] = isoarees

    return resultats


def area_coberta_per_llindar(isoarees, llindars):
    """
    Calcula l'àrea acumulada coberta per una capa d'isoàrees fins a
    cadascun dels llindars de distància/temps indicats.

    Permet comparar l'accessibilitat de diversos orígens de manera
    objectiva (a diferència de la forma visual del polígon), mirant
    quanta superfície de territori queda coberta a la mateixa distància
    per a cadascun.

    Paràmetres
    ----------
    isoarees: QgsVectorLayer
        Capa de polígons d'isoàrees, amb el camp 'cost_level' indicant
        el llindar superior de cada anell.
    llindars: list[float]
        Llista de distàncies/temps per als quals es vol calcular
        l'àrea acumulada coberta.

    Retorna
    -------
    dict
        Diccionari { llindar: area_m2 }, amb l'àrea total coberta
        per tots els anells amb cost_level <= llindar.
    """
    resultats = {}

    for llindar in llindars:
        geometries = [
            feat.geometry().makeValid()
            for feat in isoarees.getFeatures()
            if feat["cost_level"] <= llindar
        ]

        if geometries:
            area_total = QgsGeometry.unaryUnion(geometries).area()
        else:
            area_total = 0

        resultats[llindar] = area_total

    return resultats


def assignar_isoarees_a_edificis(edificis, isoarees):
    """
     Assigna a cada edifici el nivell d'accessibilitat corresponent
    a la isoàrea més ajustada que el conté.

    Les isoàrees generades per QNEAT3 són polígons niats: cadascuna
    cobreix tot el territori accessible fins al seu cost_level,
    incloent el territori de tots els nivells inferiors. Per això,
    s'itera de la isoàrea de cost més baix a la més alta i s'assigna
    a cada edifici el primer (i per tant més ajustat) cost_level que
    el conté, sense tornar a processar-lo als nivells superiors.

    Paràmetres
    ----------
    edificis: QgsVectorLayer
        Capa vectorial dels edificis.
    isoarees: QgsVectorLayer
        Capa vectorial de les isoàrees, amb el camp 'cost_level'.

    Retorna
    -------
    QgsVectorLayer
        Capa d'edificis amb el nou camp 'accessibilitat'.
    """
    layer = edificis.materialize(QgsFeatureRequest())

    provider = layer.dataProvider()
    provider.addAttributes([
        QgsField("accessibilitat", QVariant.Double)
    ])
    layer.updateFields()

    # Crea l'índex del camp accessibilitat d'edificis
    idx_accessibilitat = layer.fields().indexOf("accessibilitat")

    # Índex espacial dels edificis, construït un sol cop i reutilitzat
    # a cada iteració
    index_edificis = QgsSpatialIndex(layer.getFeatures())

    # Isoàrees ordenades, de menor cost a major
    isoarees_ordenades = sorted(
        (feat for feat in isoarees.getFeatures()
         if feat["cost_level"] is not None),
         key=lambda feat: feat["cost_level"]
    )

    assignats = set()

    canvis = {}

    for isoarea in isoarees_ordenades:
        geom_isoarea = isoarea.geometry()

        if not geom_isoarea.isGeosValid():
            geom_isoarea = geom_isoarea.makeValid()

        cost = isoarea["cost_level"]

        # Motor de geometria preparat un sol cop per isoàrea,
        # reutilitzat per a tots els edificis candidats
        engine = QgsGeometry.createGeometryEngine(geom_isoarea.constGet())
        engine.prepareGeometry()

        candidats = index_edificis.intersects(geom_isoarea.boundingBox())
        request = QgsFeatureRequest().setFilterFids(candidats)

        for edifici in layer.getFeatures(request):
            if edifici.id() in assignats:
                continue

            centroide = edifici.geometry().centroid()

            if engine.intersects(centroide.constGet()):
                canvis[edifici.id()] = {idx_accessibilitat: cost}
                assignats.add(edifici.id())

    provider.changeAttributeValues(canvis)

    return layer

##FUNCIÓ PATRÓ ESTÀNDARD!!


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




# -------------------
def distribucio_distancia(layer, camp="accessibilitat"):

    intervals = [
        (0, 250),
        (250, 500),
        (500, 1000),
        (1000, 2000),
        (2000, 3000),
        (3000, 5000),
    ]

    total = 0
    resultat = []

    valors = [
        f[camp]
        for f in layer.getFeatures()
        if f[camp] is not None
    ]

    total = len(valors)

    for baix, alt in intervals:
        n = sum(
            baix <= valor < alt
            for valor in valors
        )

        resultat.append({
            "interval": f"{baix}-{alt} m",
            "n": n,
            "percentatge": n / total * 100
        })

    return resultat

def frequencies(layer):
    from collections import Counter

    valors = [
        f["accessibilitat"]
        for f in layer.getFeatures()
        if f["accessibilitat"] is not None
    ]

    freq = Counter(valors)

    for valor, n in sorted(freq.items()):
        print(f"{valor:>6} m → {n:>6} ({n / len(valors) * 100:5.1f} %)")

