import config

def assignar_cluster_id_a_edificis(edificis, clusters, camp_id_edifici="gml_id"):
    """
    Assigna a cada edifici el CLUSTER_ID corresponent a partir de la
    capa de centroides classificats per DBSCAN.

    Com que els centroides es generen directament a partir dels edificis
    d'entrada, la relació es fa mitjançant un identificador comú entre les
    dues capes, evitant possibles ambigüitats d'una assignació basada en la
    proximitat espacial.

    Paràmetres
    ----------
    edificis: QgsVectorLayer
        Capa d'edificis industrials.
    clusters: QgsVectorLayer
        Capa de centroides classificats per DBSCAN, amb els camps CLUSTER_ID
        i l'identificador dels edificis.
    camp_id_edifici: str
        Nom del camp identificador comú entre totes dues capes.
        Per defecte, "gml_id".

    Retorna
    -------
    QgsVectorLayer
        Còpia dels edificis amb el nou camp CLUSTER_ID afegit.
        Els edificis classificats com a soroll conserven el valor -1 
        i els que no tenen correspondència queden amb valor NULL.
    """
    dict_cluster_per_edifici = {
        feat[camp_id_edifici]: feat["CLUSTER_ID"]
        for feat in clusters.getFeatures()
    }

    layer = edificis.materialize(QgsFeatureRequest())

    provider = layer.dataProvider()
    provider.addAttributes([QgsField("CLUSTER_ID", QVariant.Int)])
    layer.updateFields()

    idx_cluster = layer.fields().indexOf("CLUSTER_ID")

    canvis = {
        feat.id(): {idx_cluster: dict_cluster_per_edifici[feat[camp_id_edifici]]}
        for feat in layer.getFeatures()
        if feat[camp_id_edifici] in dict_cluster_per_edifici
    }

    provider.changeAttributeValues(canvis)

    return layer


def identificar_clusters_per_mida(clusters, noms_ordenats):
    """
    Assigna un nom descriptiu a cada clúster segons la seva posició en
    un rànquing de mida (àrea), en comptes de dependre del CLUSTER_ID
    assignat per DBSCAN, que no és estable entre execucions.

    Paràmetres
    ----------
    clusters: QgsVectorLayer
        Capa d'envolupants de clústers, amb els camps CLUSTER_ID i area.
    noms_ordenats: list[str]
        Noms a assignar, en ordre de mida decreixent (el primer nom
        correspon al clúster més gran, i així successivament).

    Retorna
    -------
    dict
        Diccionari { cluster_id: nom }, amb tants elements com
        len(noms_ordenats), corresponents als clústers més grans.
    """
    clusters_per_mida = sorted(
        ((feat["CLUSTER_ID"], feat["area"]) for feat in clusters.getFeatures()),
        key=lambda x: x[1],
        reverse=True
    )

    return {
        cluster_id: nom
        for (cluster_id, _), nom in zip(clusters_per_mida, noms_ordenats)
    }


def resum_clusters(layer):
    """
    Calcula el resum estadístic dels clústers d'una capa identificats per
    DBSCAN.

    A partir dels camps CLUSTER_ID i CLUSTER_SIZE, calcula el nombre de 
    clústers, el nombre total d'elements agrupats i la mida mínima, màxima
    i mitjana dels clústers.

    Els elements classificats com a soroll (CLUSTER_ID = -1) queden exclosos.

    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa vectorial de centroides classificats en clústers per DBSCAN.

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

        if cluster_id is None or cluster_size is None or cluster_id == -1:
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
    Executa l'anàlisi espacial de clústers per als diferents usos indicats.

    Per a cada ús:
        - filtra els edificis corresponents;
        - aplica DBSCAN als seus centroides;
        - genera les zones envolvents dels clústers;
        - calcula el resum estadístic.

    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa vectorial dels edificis.
    usos: list[str]
        Llista dels usos que s'han d'analitzar, segons els valors del camp
        `currentUse`.

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
    
        on:
        - "clusters": capa de centroides classificats per DBSCAN.
        - "zones": capa amb les envolvents convexes.
        - "resum": diccionari amb les estadístiques dels clústers.
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