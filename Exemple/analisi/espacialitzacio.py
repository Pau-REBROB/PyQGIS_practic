from qgis.core import (
    QgsFeatureRequest,
    QgsField
)

from PyQt5.QtCore import QVariant

import math

def agrupar_edificis_per_districte(districtes, edificis):
    """
    Agrupa els edificis segons el districte on es troba el seu centroide.

    Per a cada edifici, es calcula el centroide i es comprova
    a quin districte pertany.

    El resultat és un diccionari on cada clau correspon al nom
    d'un districte i el valor és una llista d'edificis - els
    features - que hi pertanyen.

    Paràmetres
    ----------
    districtes: QgsVectorLayer
        Capa vectorial dels districtes.
    edificis: QgsVectorLayer
        Capa vectorial dels edificis.

    Retorna
    -------
    dict
        Diccionari amb l'estructura:
        {
            "districte": [QgsFeature, QgsFeature,...],
            ...
        }
    """

    districtes = list(districtes.getFeatures())

    edificis_per_districte = {
        districte["NOM"]: [] for districte in districtes
    }

    for edifici in edificis.getFeatures():
        centroide = edifici.geometry().centroid()

        for districte in districtes:
            nom_districte = districte["NOM"]

            if centroide.within(districte.geometry()):
                edificis_per_districte[nom_districte].append(edifici)

                break
    
    return edificis_per_districte


def comptar_usos(edificis, usos_exclosos=None):
    """
    Calcula el nombre d'edificis de cada ús.

    Recórrer una col·lecció d'edificis i genera un
    recompte del camp "currentUse" - és a dir, el seu
    ús.

    Es poden excloure determinats usos de l'anàlisi.

    Paràmetres
    ----------
    edificis: list[QgsFeature]
        Edificis sobre els quals es calcula el recompte per ús.
    usos_exclosos: list[str], opcional
        Usos a no tenir en compte.

    Retorna
    -------
    dict
        Diccionari amb el nombre d'edificis per ús, amb l'estructura:
        {
            "1_residential": int,
            "2_agriculture": int,
            ...
        }
    """

    if usos_exclosos is None:
        usos_exclosos = []

    comptador = {}

    for edifici in edificis:

        us = edifici["currentUse"]

        if us is None:
            continue

        if us in usos_exclosos:
            continue

        comptador[us] = comptador.get(us, 0) + 1

    return comptador


def calcular_especialitzacio(comptador):
    """
    Calcula els principals indicadors d'especialització funcional.

    A partir del recompte d'usos obté:
        - l'ús predominant,
        - el percentatge que representa,
        - la dominància respecte el segon ús,
        - el nombre total d'edificis,
        - el rànquing complet dels usos.

    Paràmetres
    ----------
    comptador: dict
        Diccionari amb el nombre d'edificis per cada ús.
    
    Retorna
    -------
    dict
        Diccionari amb els indicadors d'especialització, 
        amb l'estructura:
        {
            "us_predominant": str,
            "percentatge": float,
            "dominancia": float,
            "total_edificis": int,
            "rànquing": list[
                ("ús", int),
                ("ús", int),
                ...
            ]
        }
    """
   
    # Ordenar usos en ordre descendent per nombre d'edificis
    usos_ordenats = sorted(
        comptador.items(),
        key=lambda item: item[1],
        reverse=True
    )

    # Total d'edificis    
    total = sum(comptador.values())

    us_predominant = usos_ordenats[0][0]
    valor_predominant = usos_ordenats[0][1]

    percentatge_predominant = valor_predominant / total * 100

    # Càlcul de dominància
    if len(comptador) == 1:
        dominancia = percentatge_predominant
    else:
        us_segon = usos_ordenats[1][0]
        valor_segon = usos_ordenats[1][1]

        dominancia = (valor_predominant - valor_segon) / total * 100
    
    return {
        "us_predominant": us_predominant,
        "percentatge": percentatge_predominant,
        "dominancia": dominancia,
        "total_edificis": total,
        "rànquing": usos_ordenats
    }


def calcular_shannon(comptador):
    """
    Calcula l'índex de diversitat de Shannon.

    L'índex mesura el grau de diversitat funcional dels usos
    presents. Valors elevats indiquen una distribució més 
    equilibrada dels usos, mentre que valors més baixos
    indiquen una major especialització.

    Paràmetres
    ----------
    comptador: dict
        Diccionari amb el nombre d'edificis per cada ús.

    Retorna
    -------
    dict
        Diccionari amb els indicadors de diversitat, amb l'estructura:
        {
            "shannon": float,
            "shannon_normalitzat": float
        }
        on:
            - "shannon" és l'índex de Shannon
            - "shannon_normalitzat" és l'índex de Shannon normalitzat 
    """

    # Total d'edificis    
    total = sum(comptador.values())

    shannon = 0

    for valor in comptador.values():
        p = valor / total

        shannon -= p * math.log(p)

    if len(comptador) > 1:
        shannon_normalitzat = shannon / math.log(len(comptador))
    else:
        shannon_normalitzat = 0
    
    return {
        "shannon": shannon,
        "shannon_normalitzat": shannon_normalitzat
    }


def analisi_especialitzacio(districtes, edificis, usos_exclosos=None):
    """
    Clacula els indicadors d'especialització funcional de cada districte.

    Per a cada districte:
        - Agrupa els edificis que hi pertanyen.
        - Compta el nombre d'edificis per a cada ús.
        - Calcula els indicadors d'especialització.
        - Calcula els índex de Shannon.

    Paràmetres
    ----------
    districtes: QgsVectorLayer
        Capa vectorial dels districtes.
    edificis: QgsVectorLayer
        Capa vectorial dels edificis.
    usos_exclosos: list[str], opcional
        Llista d'usos que no es volen considerar en l'anàlisi.

    Retorna
    -------
    dict
        Diccionari amb els càlculs d'especialització
        de cada districte, amb l'estructura:
        {
            "nom_districte": {
                "us_predominant": str,
                "percentatge": float,
                "dominancia": float,
                "total_edificis": int,
                "ranquing": list[
                    ("ús", int),
                    ("ús", int),
                    ...],
                "shannon": float,
                "shannon_normalitzat": float
            },
            "nom_districte": {
                ...
            }
        }
    """

    edificis_districtes = agrupar_edificis_per_districte(
        districtes=districtes,
        edificis=edificis
    )

    resultats = {}

    for nom, edificis in edificis_districtes.items():
        comptador = comptar_usos(
            edificis=edificis,
            usos_exclosos=usos_exclosos
        )

        especialitzacio = calcular_especialitzacio(
            comptador=comptador
        )

        especialitzacio.update(
            calcular_shannon(comptador=comptador)
        )

        resultats[nom] = especialitzacio
    
    return resultats


def afegir_resultats_especialitzacio(districtes, resultats):
    """
    Genera una nova capa de districtes incorporant els indicadors
    d'especialització funcional calculats.

    A partir de la capa original de districtes, crea una còpia
    i afegeix els nous atributs.

    Paràmetres
    ----------
    districtes: QgsVectorLayer
        Capa vectorial dels districtes.
    resultats: dict
        Diccionari retornat de `analisi_especialitzacio()`.

    Retorna
    -------
    QgsVectorLayer
        Nova capa de districtes amb els camps d'anàlisi incorporats.
    """

    layer = districtes.materialize(QgsFeatureRequest())

    provider = layer.dataProvider()

    provider.addAttributes([
        QgsField("us_predominant", QVariant.String),
        QgsField("perc_predominant", QVariant.Double),
        QgsField("dominancia", QVariant.Double),
        QgsField("shannon", QVariant.Double),
        QgsField("shannon_norm", QVariant.Double)
    ])

    layer.updateFields()

    idx_us = layer.fields().indexOf("us_predominant")
    idx_perc = layer.fields().indexOf("perc_predominant")
    idx_dominancia = layer.fields().indexOf("dominancia")
    idx_shannon = layer.fields().indexOf("shannon")
    idx_shan_norm = layer.fields().indexOf("shannon_norm")

    layer.startEditing()

    for feature in layer.getFeatures():
        nom = feature["NOM"]

        dades = resultats.get(nom)

        if dades is None:
            continue

        feature[idx_us] = dades["us_predominant"]
        feature[idx_perc] = dades["percentatge"]
        feature[idx_dominancia] = dades["dominancia"]
        feature[idx_shannon] = dades["shannon"]
        feature[idx_shan_norm] = dades["shannon_normalitzat"]

        layer.updateFeature(feature)
    
    layer.commitChanges()

    return layer


def classificar_especialitzacio():
    """
    Classifica qualitativament el grau de diversitat funcional
    d'un districte a partir de l'índex de Shannon normalitzat.

    """