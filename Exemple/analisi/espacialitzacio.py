from qgis.core import (
    QgsFeatureRequest,
    QgsField
)

from PyQt5.QtCore import QVariant

import math

import config

def agrupar_edificis_per_zones(zones, edificis):
    """
    Agrupa els edificis segons la unitat administrativa on es
    troba el seu centroide.

    Per a cada edifici, es calcula el centroide i es comprova
    a quina zona pertany.

    El resultat és un diccionari on cada clau correspon al nom
    d'una unitat administrataiva i el valor és una llista d'edificis
    - els features - que hi pertanyen.

    Paràmetres
    ----------
    zones: QgsVectorLayer
        Capa vectorial de les unitats administratives.
    edificis: QgsVectorLayer
        Capa vectorial dels edificis.

    Retorna
    -------
    dict
        Diccionari amb l'estructura:
        {
            "zona": [QgsFeature, QgsFeature,...],
            ...
        }
    """

    llista_zones = list(zones.getFeatures())

    edificis_per_zona = {
        zona["NOM"]: [] for zona in llista_zones
    }

    for edifici in edificis.getFeatures():
        centroide = edifici.geometry().centroid()

        for zona in llista_zones:
            nom_zona = zona["NOM"]

            if centroide.within(zona.geometry()):
                edificis_per_zona[nom_zona].append(edifici)

                break
    
    return edificis_per_zona


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


def analisi_especialitzacio(zones, edificis, usos_exclosos=None):
    """
    Clacula els indicadors d'especialització funcional de cada unitat
    administrativa.

    Per a cada zona:
        - Agrupa els edificis que hi pertanyen.
        - Compta el nombre d'edificis per a cada ús.
        - Calcula els indicadors d'especialització.
        - Calcula els índex de Shannon.

    Paràmetres
    ----------
    zones: QgsVectorLayer
        Capa vectorial de les unitats administratives.
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
            "nom_zona": {
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
            "nom_zona": {
                ...
            }
        }
    """

    edificis_zones = agrupar_edificis_per_zones(
        zones=zones,
        edificis=edificis
    )

    resultats = {}

    for nom, edificis in edificis_zones.items():
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

    for nom, dades in resultats.items():
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

        # Generar interpretació
        us = config.ETIQUETES_USOS[dades["us_predominant"]]

        if classe_dominancia == "Alta":
            if classe_diversitat == "Alta":
                interpretacio = (
                    f"Zona de {nom} clarament especialitzat en ús {us} "
                    f"({dades['percentatge']:.1f}% dels edificis)"
                    f" amb una alta diversitat d'usos"
                )
            else:
                interpretacio = (
                    f"Zona de {nom} clarament especialitzat en ús {us} "
                    f"({dades['percentatge']:.1f}% dels edificis)"
                    f" però amb baixa diversitat d'usos"
                )
        
        elif classe_dominancia == "Mitjana":
            interpretacio = (
                f"Zona de {nom} mostra una especialització moderada "
                f"en ús {us} ({dades['percentatge']:.1f}% dels edificis)"
            )

        elif classe_dominancia == "Baixa":
            if classe_diversitat == "Alta":
                interpretacio = (
                    f"Zona de {nom} presenta una distribució bastant equilibrada entre els usos "
                    f" amb una alta diversitat d'usos"
                )
            else:
                interpretacio = (
                    f"Zona de {nom} presenta una distribució bastant equilibrada entre "
                    f"els usos, amb poca diversitat d'aquests"
                )

        else:
            interpretacio = (
                f"Zona {nom} no presenta cap especialització clara "
                f"i mostra una estructura funcional molt diversa"
            )
        
        # Assignar classificacions
        dades["classe_dominancia"] = classe_dominancia
        dades["classe_diversitat"] = classe_diversitat
        dades["interpretacio"] = interpretacio

    return resultats


def afegir_resultats_especialitzacio(zones, resultats):
    """
    Genera una nova capa d'unitats administratives incorporant
    els indicadors d'especialització funcional calculats.

    A partir de la capa original de zones, crea una còpia
    i afegeix els nous atributs.

    Paràmetres
    ----------
    zones: QgsVectorLayer
        Capa vectorial de les unitats administratives.
    resultats: dict
        Diccionari retornat de `analisi_especialitzacio()`.

    Retorna
    -------
    QgsVectorLayer
        Nova capa de districtes amb els camps d'anàlisi incorporats.
    """

    layer = zones.materialize(QgsFeatureRequest())

    provider = layer.dataProvider()

    provider.addAttributes([
        QgsField("us_predominant", QVariant.String),
        QgsField("perc_predominant", QVariant.Double),
        QgsField("dominancia", QVariant.Double),
        QgsField("shannon", QVariant.Double),
        QgsField("shannon_norm", QVariant.Double),
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


def assignar_especialitzacio_per_hexagons(edificis, malla, usos_exclosos=None):
    """
    Agrega els indicadors d'especialització funcional dels edificis
    a cada hexagon de la malla.

    Aprofita el camp 'hex_id' dels edificis per evitar un join espacial
    i fer un sol bucle sobre els edificis.

    Paràmetres
    ----------
    edificis: QgsVectorLayer
        Capa vectorial dels edificis amb els camp d'especialització.
    malla: QgsVectorLayer
        Capa vectorial de la malla hexagonal amb els camps de
        funcionalitat.
    usos_exclosos: list[str], opcional
        Usos que no es volen considerar en l'anàlisi.
    
    Retorna
    -------
    dict
        Diccionari amb els resultats d'especialització de cada
        hexagon, amb l'estructura:
        {
            "hex_id": {
                "us": int,
                "dominancia": int
                "shannon":
                ....
            },
            ...
        }
    """

    # Agrupar els valors d'ús dels edificis i el seu recompte
    # per hexagon
    # {
    #     id_hex1: {
    #           us1: int,
    #           us2: int,
    #           usN: int
    #               },
    #     id_hex2: {...},
    #     ...
    # }
    usos_hexagons = {}

    for edifici in edificis.getFeatures():
        hex_id = edifici["hex_id"]
        hex_us = edifici["currentUse"]

        if hex_id is None or hex_us is None:
            continue

        if usos_exclosos and hex_us in usos_exclosos:
            continue

        if hex_id not in usos_hexagons:
            usos_hexagons[hex_id] = {}

        usos_hexagons[hex_id][hex_us] = (
            usos_hexagons[hex_id].get(hex_us, 0) + 1
        )

    # Crear la capa de sortida
    layer = malla.materialize(QgsFeatureRequest())

    provider = layer.dataProvider()

    provider.addAttributes([
        QgsField("us_predominant", QVariant.String),
        QgsField("perc_predominant", QVariant.Double),
        QgsField("dominancia", QVariant.Double),
        QgsField("shannon", QVariant.Double),
        QgsField("shannon_norm", QVariant.Double),
        #QgsField("classe_bivariant", QVariant.String)
    ])

    layer.updateFields()

    idx_us = layer.fields().indexOf("us_predominant")
    idx_perc = layer.fields().indexOf("perc_predominant")
    idx_dominancia = layer.fields().indexOf("dominancia")
    idx_shannon = layer.fields().indexOf("shannon")
    idx_shan_norm = layer.fields().indexOf("shannon_norm")

    # Escriure els resultats a la capa
    ## Per cada hexagon, recullir el seu índex
    ## comprovar que existeix en el diccionari anterior dels edificis per hex_id
    ## d'aquest diccionari, obtenir el diccionari de recompte d'usos
    ## generar les funcions d'especialització funcional per aquell hexagon
    ## establir el canvi en el diccionari de canvis com a
    ##  id_hexagon: {idx_camp_especialitzacio: resultat_especialitzacio}
    ## Aplicar tots els canvis de cop
    layer.startEditing()

    canvis = {}

    for feature in layer.getFeatures():
        hex_id = feature["id"]

        if hex_id not in usos_hexagons:
            continue

        comptador = usos_hexagons[hex_id]

        if not comptador:
            continue

        especialitzacio = calcular_especialitzacio(
            comptador=comptador
        )

        shannon = calcular_shannon(
            comptador=comptador
        )

        especialitzacio.update(shannon)

        # Guardar els valors
        canvis[feature.id()] = {
            idx_us: especialitzacio["us_predominant"],
            idx_perc: especialitzacio["percentatge"],
            idx_dominancia: especialitzacio["dominancia"],
            idx_shannon: especialitzacio["shannon"],
            idx_shan_norm: especialitzacio["shannon_normalitzat"]
        }

    provider.changeAttributeValues(canvis)
    layer.commitChanges()

    return layer


# =======================================
# BIVARIANT
# ========================================

def calcular_classe_bivariant(dominancia, diversitat):
    """
    Calcula la classe bivariant a partir de la dominància
    i la diversitat funcional normalitzada.
    """

    if dominancia >= 20:
        classe_dominancia = "Alta"
    elif dominancia >= 10:
        classe_dominancia = "Mitjana"
    else:
        classe_dominancia = "Baixa"

    if diversitat >= 0.85:
        classe_diversitat = "Alta"
    elif diversitat >= 0.75:
        classe_diversitat = "Mitjana"
    else:
        classe_diversitat = "Baixa"

    return f"{classe_dominancia}_{classe_diversitat}"


def classificar_bivariant(resultats):
    """
    Genera una classificació bivariant combinant les
    classificacions de dominància i diversitat funcional.

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
        
        dades["classe_bivariant"] = calcular_classe_bivariant(
            dominancia=dades["dominancia"],
            diversitat=dades["diversitat"]
        )

    return resultats


def afegir_classe_bivariant(layer):
    """
    Afegeix la classificació bivariant a una capa vectorial que ja conté
    els indicadors de dominància i diversitat funcional.

    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa vectorial amb els indicadors.

    Retorna
    -------
    QgsVectorLayer
        Nova capa vectorial amb el camp bivariant incorporats.
    """

    layer_clone = layer.materialize(QgsFeatureRequest())

    provider = layer_clone.dataProvider()

    provider.addAttributes([
        QgsField("classe_bivariant", QVariant.String)
    ])

    layer_clone.updateFields()

    idx_bivariant = layer_clone.fields().indexOf("classe_bivariant")

    layer_clone.startEditing()

    for feature in layer_clone.getFeatures():
        dominancia = feature["dominancia"]
        diversitat = feature["shannon_norm"]

        if dominancia is None or diversitat is None:
            continue 

        feature[idx_bivariant] = calcular_classe_bivariant(
            dominancia=dominancia,
            diversitat=diversitat
        )

        layer_clone.updateFeature(feature)
    
    layer_clone.commitChanges()

    return layer_clone
