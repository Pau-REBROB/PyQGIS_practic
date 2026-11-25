
"""
Anàlisi dels usos dels edificis per zones
=========================================

Flux de treball aparcat.

Agrupa els edificis segons el seu ús cadastral per unitat
administrativa i calcula els percentatges corresponents.

Aquest mòdul es conserva com a referència, però no forma
part del flux principal d'anàlisi actual.
"""

import config


def agregar_usos_zones(edificis, zones, idx_zones):
    """
    Agrupa el nombre d'edificis de cada ús per cada zona.

    Per a cada edifici, determina la unitat administrativa
    a partir del centroide de la seva geometria.

    Utilitza un índex espacial precalculat per optimitzar
    la cerca de la zona corresponent a cada edifici.

    Retorna
    -------
    dict
        Diccionari amb el recompte d'edificis per ús i zona.
    """

    resultats = {}

    zones_dict = {
        feat.id(): feat
        for feat in zones.getFeatures()
    }

    # Inicialitzar resultats
    for zona in zones.getFeatures():
        nom = str(zona["NOM"]).strip()
        resultats[nom] = {
            us: 0
            for us in config.USOS
        }

    # Iteració sobre cada edifici
    for edifici in edificis.getFeatures():
        centroide = edifici.geometry().centroid()
        us = str(edifici["currentUse"]).strip()

        if us == "NULL":
            continue

        zones_candidats = idx_zones.intersects(centroide.boundingBox())

        for c in zones_candidats:
            zona = zones_dict[c]

            if centroide.within(zona.geometry()):
                nom = str(zona["NOM"]).strip()
                resultats[nom][us] += 1
                break

    return resultats


def calcular_percentatges_usos(resultats):
    """
    Calcula el percentatge d'edificis de cada ús per zona.

    Els percentatges s'expressen com a proporció del total
    d'edificis de cada unitat administrativa.

    Retorna
    -------
    dict
        Diccionari amb la mateixa estructura que l'entrada,
        però amb els valors expressats com a proporcions.
    """

    percentatges = {}

    for unitat, usos in resultats.items():
        total = sum(usos.values())

        if total == 0:
            percentatges[unitat] = {
                us: 0
                for us in usos
            }
            continue

        percentatges[unitat] = {
            us: valor / total
            for us, valor in usos.items()
        }

    return percentatges


def analisi_usos_zones(edificis, zones, idx_zones):
    """
    Executa l'anàlisi dels usos dels edificis per zones.

    Genera el recompte d'edificis per ús i zona i calcula
    els percentatges corresponents.

    Retorna
    -------
    dict
        Diccionari amb dues claus:
        - dades: recomptes absoluts per ús i zona.
        - percentatges: proporcions per ús i zona.
    """

    dades = agregar_usos_zones(
        edificis=edificis,
        zones=zones,
        idx_zones=idx_zones
    )

    percentatges = calcular_percentatges_usos(
        resultats=dades
    )

    return {
        "dades": dades,
        "percentatges": percentatges
    }
