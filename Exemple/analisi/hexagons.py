"""
Anàlisi amb malla hexagonal (hexgrid)
=====================================

Mòdul que agrupa les funcions per a l'anàlisi funcional mitjançant malla hexagonal.

Aquest mòdul permet:
    - generar una malla hexagonal,
    - assignar cada edifici al seu hexagon,
    - agregar els usos dels edificis,
    - calcular indicadors d'especialització funcional,
    - classificar els indicadors,
    - incorporar els indicadors a una nova malla hexagonal.

Els indicadors calculats son:
    - Ús predominant
    - Percentatge de l'ús predominant
    - Dominància
    - Índex de Shannon
    - Índex de Shannon normalitzat
    - Classificació bivariant
"""

from qgis.core import (
    QgsFeatureRequest,
    QgsField
)
from PyQt5.QtCore import QVariant

import processing
import math

import config

def crear_malla_hexagonal(capa_extent, mida_hexagon):
    """
    Crea una malla regular d'hexàgons.

    La funció crea una capa vectorial formada per hexàgons que
    cobreixen totalment l'extensió de la capa de referència.

    Paràmetres
    ----------
    capa_extent: QgsVectorLayer
        Capa vectorial utilitzada per definir l'extensió de la malla.
    mida_hexagon: int
        Amplada de cada hexagon, en unitats del SRC.

    Retorna
    -------
    QgsVectorLayer
        Capa vectorial de la malla hexagonal.
    """

    resultat = processing.run(
        "native:creategrid",
        {
            'TYPE': 4,
            'EXTENT': capa_extent,
            'HSPACING': mida_hexagon,
            'VSPACING': mida_hexagon,
            'HOVERLAY': 0,
            'VOVERLAY': 0,
            'CRS': capa_extent.crs(),
            'OUTPUT': "memory:"
        }
    )

    return resultat["OUTPUT"]


def retallar_malla_hexagonal(malla, capa_extent):
    """
    Retalla una malla hexagonal segons l'àmbit d'estudi.

    Elimina tots els hexàgons o parts d'hexàgons situats
    fora del límit de la capa de referència.

    Paràmetres
    ----------
    malla: QgsVectorLayer
        Capa vectorial de la malla hexagonal.
    capa_extent: QgsVectorLayer
        Capa vectorial que defineix l'extensió d'estudi.

    Retorna
    -------
    QgsVectorLayer
        Malla hexagonal retallada.
    """

    resultat = processing.run(
        "native:clip",
        {
            'INPUT': malla,
            'OVERLAY': capa_extent,
            'OUTPUT': "memory:"
        }
    )

    return resultat["OUTPUT"]


def generar_malla_retallada(capa_extent, mida_hexagon):
    """
    Genera una malla hexagonal retallada a la capa d'estudi.

    La funció crea la malla i, posteriorment, la retalla 
    utilitzant una capa de referència.

    Paràmetres
    ----------
    capa_extent: QgsVectorLayer
        Capa vectorial que defineix l'extensió d'estudi.
    mida_hexagon: int
        Amplada de l'hexagon de la malla.

    Retorna
    -------
    QgsVectorLayer
        Malla hexagonal retallada.
    """

    malla = crear_malla_hexagonal(
        capa_extent=capa_extent,
        mida_hexagon=mida_hexagon
    )

    malla_retallada = retallar_malla_hexagonal(
        malla=malla,
        capa_extent=capa_extent
    )

    return malla_retallada


def filtrar_capa_edificis(layer, expressio):
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


def assignar_hexagons_a_edificis(edificis, malla, expressio=None):
    """
    Assigna a cada edifici l'identificador de l'hexagon on es troba.

    La funció genera una nova capa en memòria amb totes les geometries
    dels edificis i incorpora el camp identificador de la malla
    hexagonal.

    Paràmetres
    ----------
    edificis: QgsVectorLayer
        Capa vectorial dels edificis.
    malla: QgsVectorLayer
        Capa vectorial de la malla hexagonal.
    expressio: str, optional
        Expressió de filtratge escrita amb la sintaxi d'expressions de QGIS.
        Per defecte és None.

    Retorna
    -------
    QgsVectorLayer
        Nova capa dels edificis amb el camp identificador de l'hexagon.
    """

    if expressio: 
        edificis = filtrar_capa_edificis(
            layer=edificis,
            expressio=expressio
        )

    resultat = processing.run(
        "native:joinattributesbylocation",
        {
            'INPUT': edificis,
            'JOIN': malla,
            'JOIN_FIELDS': 'id',
            'PREDICATE': 0, # Intersecció
            'METHOD': 1, # Primer element coincident
            'DISCARD_NONMATCHING': False,
            'PREFIX': "hex_",
            'OUTPUT': "memory:"
        }
    )

    return resultat["OUTPUT"]


def agregar_usos_per_hexagons(edificis_hex):
    """
    Agrupa els edificis per hexàgons i calcula el nombre total
    d'edificis i el nombre total d'usos diferents.

    Paràmetres
    ----------
    edificis_hex: QgsVectorLayer
        Capa vectorial d'edificis amb el camp "hex_id".

    Retorna
    -------
    dict
        Diccionari amb l'estructura:
        {
            hex_id: {
                "n_edificis": int,
                "comptador_usos": {
                    "1_residential": int,
                    "2_agriculture": int,
                    ...
                }
            }
            ...
        }
    """

    hexagons = {}

    for edifici in edificis_hex.getFeatures():
        hex_id = edifici["hex_id"]
        us = edifici["currentUse"]

        if hex_id is None:
            continue

        if hex_id not in hexagons:
            hexagons[hex_id] = {
                "n_edificis": 0,
                "comptador_usos": {}
            }

        hexagons[hex_id]["n_edificis"] += 1

        if us is not None:
            hexagons[hex_id]["comptador_usos"][us] = hexagons[hex_id]["comptador_usos"].get(us, 0) +1

    return hexagons
    

def calcular_especialitzacio(comptador):
    """
    Calcula els principals indicadors d'especialització funcional.

    A partir del recompte d'usos obté:
        - l'ús predominant,
        - el percentatge que representa,
        - la dominància respecte el segon ús.

    Paràmetres
    ----------
    comptador: dict
        Diccionari amb el nombre d'edificis per hexagon i
        el nombre d'usos diferents.
    
    Retorna
    -------
    dict
        Diccionari amb els indicadors d'especialització, 
        amb l'estructura:
        {
            "us_predominant": str,
            "percentatge": float,
            "dominancia": float
        }
    """
   
    # Ordenar usos en ordre descendent per nombre d'edificis
    usos_ordenats = sorted(
        comptador["comptador_usos"].items(),
        key=lambda item: item[1],
        reverse=True
    )

    total = comptador["n_edificis"]

    us_predominant = usos_ordenats[0][0]
    valor_predominant = usos_ordenats[0][1]

    percentatge_predominant = valor_predominant / total * 100

    # Càlcul de dominància
    if len(usos_ordenats) == 1:
        dominancia = percentatge_predominant
    else:
        us_segon = usos_ordenats[1][0]
        valor_segon = usos_ordenats[1][1]

        dominancia = (valor_predominant - valor_segon) / total * 100
    
    return {
        "us_predominant": us_predominant,
        "percentatge": percentatge_predominant,
        "dominancia": dominancia
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
        Diccionari amb el nombre d'edificis per hexagon i
        el nombre d'usos diferents.
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

    total = comptador["n_edificis"]

    shannon = 0

    for valor in comptador["comptador_usos"].values():
        p = valor / total

        shannon -= p * math.log(p)

    if len(comptador["comptador_usos"]) > 1:
        shannon_normalitzat = shannon / math.log(len(comptador["comptador_usos"]))
    else:
        shannon_normalitzat = 0
    
    return {
        "shannon": shannon,
        "shannon_normalitzat": shannon_normalitzat
    }


def analisi_especialitzacio(malla, edificis, expressio=None):
    """
    Clacula els indicadors d'especialització funcional de cada hexagon.

    Per a cada hexagon:
        - Agrega els usos dels edificis,
        - Calcula l'ús predominant,
        - Calcula el percentatge de l'ús predominant,  
        - Compta el nombre d'edificis per a cada ús,
        - Calcula la dominància,
        - Calcula els índex de Shannon.

    Paràmetres
    ----------
    edificis: QgsVectorLayer
        Capa vectorial dels edificis.
    malla: QgsVectorLayer
        Malla hexagonal.
    expressio: str, opcional
        Expressió de filtratge escrita amb la sintaxi d'expressions de QGIS.
        Per defecte és None.

    Retorna
    -------
    dict
        Diccionari amb els càlculs d'especialització
        de cada hexagon, amb l'estructura:
        {
            "hex_id": {
                "n_edificis": int,
                "comptador_usos": {
                    "1_residential": int,
                    "2_agriculture": int,
                    ...
                }
                "percentatge": float,
                "dominancia": float,
                "shannon": float,
                "shannon_normalitzat": float
            },
            "hex_id": {
                ...
            }
        }
    """

    edificis_hex = assignar_hexagons_a_edificis(
        edificis=edificis,
        malla=malla,
        expressio=expressio
    )

    edificis_hex_usos = agregar_usos_per_hexagons(
        edificis_hex=edificis_hex
    )

    resultats = {}

    for hex_id, data in edificis_hex_usos.items():
        if not data["comptador_usos"]:
            continue

        especialitzacio = calcular_especialitzacio(
            comptador=data
        )

        especialitzacio.update(
            calcular_shannon(
                comptador=data
            )
        )

        resultats[hex_id] = data.copy()
        resultats[hex_id].update(especialitzacio)

    return resultats


def classificar_especialitzacio(resultats):
    """
    Classifica qualitativament els indicadors d'especialització
    funcional.

    A partir dels indicadors calculats assigna una
    categoria qualitativa al grau de dominància i de diversitat
    funcional, així com una breu interpretació automàtica.

    Paràmetres
    ----------
    resultats: dict
        Diccionari retornat per `analisi_especialitzacio()`.
    
    Retorna
    -------
    dict
        Diccionari d'entrada actualitzat amb els camps
        {
            "classe_dominancia": str,
            "classe_diversitat": str,
            "interpretacio": str
        }
    """

    for hex_id, dades in resultats.items():
        # Classificar dominància
        dominancia = dades["dominancia"]

        if dominancia >= config.CLASSIFICACIO_DOMINANCIA["Alta"]:
            classe_dominancia = "Alta"
        
        elif dominancia >= config.CLASSIFICACIO_DOMINANCIA["Mitjana"]:
            classe_dominancia = "Mitjana"

        elif dominancia >= config.CLASSIFICACIO_DOMINANCIA["Baixa"]:
            classe_dominancia = "Baixa"

        else:
            classe_dominancia = "Molt baixa"

        # Classificar índex Shannon
        shannon = dades["shannon_normalitzat"]

        if shannon >= config.CLASSIFICACIO_SHANNON["Alta"]:
            classe_diversitat = "Alta"
        
        elif shannon >= config.CLASSIFICACIO_SHANNON["Mitjana"]:
            classe_diversitat = "Mitjana"
        
        elif shannon >= config.CLASSIFICACIO_SHANNON["Baixa"]:
            classe_diversitat = "Baixa"
        
        else:
            classe_diversitat = "Molt baixa"
        
        # Assignar classificacions
        dades["classe_dominancia"] = classe_dominancia
        dades["classe_diversitat"] = classe_diversitat
        #dades["interpretacio"] = interpretacio

    return resultats


def classificar_bivariant(resultats):
    """
    Assigna una categoria bivariant combinant les classificacions
    de dominància i diversitat funcional.

    Paràmetres
    ----------
    resultats: dict
        Diccionari retornat per `analisi_especialitzacio()`.
    
    Retorna
    -------
    dict
        Diccionari d'entrada amb la combinació
        de totes les entrades de diversitat i dominància.
        {
            "classe_bivariant": str
        }
    """

    for dades in resultats.values():
        # Classificació de la dominància 
        dominancia = dades["dominancia"]

        if dominancia >= 20:
            classe_dominancia = "Alta"
        elif dominancia >= 10:
            classe_dominancia = "Mitjana"
        else:
            classe_dominancia = "Baixa"

        # Classificació de la diversitat funcional (Shannon)
        diversitat = dades["shannon_normalitzat"]

        if diversitat >= 0.85:
            classe_diversitat = "Alta"
        elif diversitat >= 0.75:
            classe_diversitat = "Mitjana"
        else:
            classe_diversitat = "Baixa"

        # Creació de la classificació bivariant
        dades["classe_bivariant"] = (
            f"{classe_dominancia}_{classe_diversitat}"
        )

    return resultats


def afegir_resultats_especialitzacio(malla, resultats, min_edificis=config.MIN_EDIFICIS):
    """
    Genera una nova capa de malla hexagonal incorporant els indicadors
    d'especialització funcional calculats.

    A partir de la capa original de la malla, crea una còpia
    i afegeix els nous atributs.

    Paràmetres
    ----------
    malla: QgsVectorLayer
        Capa vectorial malla hexagonal.
    resultats: dict
        Diccionari retornat de `analisi_especialitzacio()`.
    min_edificis: int
        Nombre mínim d'edificis necessaris perquè un hexagon
        incorpori els indicadors.
        Els hexàgons amb menys edificis mantenen els camps
        d'anàlisi a valor nul.

    Retorna
    -------
    QgsVectorLayer
        Nova capa malla hexagonal amb els camps d'anàlisi incorporats.
    """

    layer = malla.materialize(QgsFeatureRequest())

    provider = layer.dataProvider()

    provider.addAttributes([
        QgsField("us_predominant", QVariant.String),
        QgsField("perc_predominant", QVariant.Double),
        QgsField("dominancia", QVariant.Double),
        QgsField("shannon", QVariant.Double),
        QgsField("shannon_norm", QVariant.Double),
        QgsField("classe_bivariant", QVariant.String),
        QgsField("n_edificis", QVariant.Int)
    ])

    layer.updateFields()

    idx_us = layer.fields().indexOf("us_predominant")
    idx_perc = layer.fields().indexOf("perc_predominant")
    idx_dominancia = layer.fields().indexOf("dominancia")
    idx_shannon = layer.fields().indexOf("shannon")
    idx_shan_norm = layer.fields().indexOf("shannon_norm")
    idx_bivariant = layer.fields().indexOf("classe_bivariant")
    idx_n_edificis = layer.fields().indexOf("n_edificis")

    layer.startEditing()

    for feature in layer.getFeatures():
        hex_id = feature["id"]

        dades = resultats.get(hex_id)

        if dades is None:
            continue

        if dades["n_edificis"] < min_edificis:
            feature[idx_us] = None
            feature[idx_perc] = None
            feature[idx_dominancia] = None
            feature[idx_shannon] = None
            feature[idx_shan_norm] = None
            feature[idx_bivariant] = None
            feature[idx_n_edificis] = None

            layer.updateFeature(feature)

            continue

        feature[idx_us] = dades["us_predominant"]
        feature[idx_perc] = dades["percentatge"]
        feature[idx_dominancia] = dades["dominancia"]
        feature[idx_shannon] = dades["shannon"]
        feature[idx_shan_norm] = dades["shannon_normalitzat"]
        feature[idx_bivariant] = dades["classe_bivariant"]
        feature[idx_n_edificis] = dades["n_edificis"]

        layer.updateFeature(feature)
    
    layer.commitChanges()

    return layer

