"""
Agregacions estadístiques
=========================

Mòdul que agrupa les funcions d'agregació estadística del projecte.

Organització
------------

- Agregació per zones
    Funcions per calcular el nombre i el percentatge d'edificis
    segons el seu ús dins de cada unitat administrativa.

Les funcions s'organitzen en tres nivells:
    - funcions bàsiques d'agregació;
    - funcions de transformació dels resultats;
    - funcions d'alt nivell que orquestren el procés complet.
"""


import config


def agregar_usos_zones(edificis, zones):
    """
    Agrupa el nombre d'edificis de cada ús per cada zona.

    Per a cada edifici, determina la unitat administrativa al qual
    pertany a partir del centroide de la seva geometria i
    incrementa el comptador de l'ús corresponent.

    Paràmetres
    ----------
    edificis: QgsVectorLayer
        Capa vectorial dels edificis.
    zona: QgsVectorLayer
        Capa vectorial de les unitats administratives.

    Retorna
    -------
    dict
        Diccionari amb el recompte d'edificis destinats a cada ús per zona
        {
            "Nom_UA": {
                "1_residential": int,
                "2_agriculture": int,
                ...
            },
            ...
        }
    """

    resultats = {}

    zones_llista = list(zones.getFeatures())

    # Iteració sobre cada zona
    for zona in zones_llista:
        
        nom = str(zona["NOM"]).strip()
        
        # Creació de valors 0 inicials per cada categoria d'ús a la zona
        resultats[nom] = {
            us: 0
            for us in config.USOS
        }

    # Iteració sobre cada edifici
    for edifici in edificis.getFeatures():
        # Extracció geometria de l'edifici
        geom_edifici = edifici.geometry()

        # Obtenció de l'ús de l'edifici
        us = str(edifici["currentUse"]).strip()

        # descartar els usos nuls
        if us == "NULL":
            continue

        # Cerca de la zona a la qual pertany l'edifici
        # amb la comprovació d'on es troba el seu centroide
        for districte in zones_llista:
            if geom_edifici.centroid().within(districte.geometry()):
                nom = zona["NOM"]
                # Actualització del comptador d'usos
                resultats[nom][us] += 1

                break
    
    return resultats


def calcular_percentatges_usos(resultats):
    """
    Calcula el percentatge d'edificis de cada ús per unitat administrativa.

    A partir de la taula amb el nombre d'edificis de cada ús,
    calcula el pes percentual de cada categoria respecte el total
    d'edificis de la unitat administrativa.

    Paràmetres
    ----------
    resultats: dict
        Diccionari amb el nombre d'edificis de cada ús per unitat administrativa.

    Retorna
    -------
    dict
        Mateixa estructura que el diccionari d'entrada,
        però amb els valors expressats en percentatge.
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


def analisi_usos_zones(edificis, zones):
    """
    Executa l'anàlisi dels usos dels edificis per unitats
    administratives.

    L'anàlisi genera, de forma consecutiva:
        - el recompte d'edificis per ús i per zona,
        - la taula resum amb els valors absoluts,
        - la taula amb els percentatges corresponents.
    
    Paràmetres
    ----------
    edificis: QgsVectorLayer
        Capa vectorial dels edificis.
    zones: QgsVectorLayer
        Capa vectorial de les unitats administratives.
    
    Retorna
    -------
    dict
        {
            "dades": {
                "Nom_UA": {
                    "1_residential": int,
                    "2_agriculture": int,
                    "3_industrial": int,
                    "4_1_office": int,
                    "4_2_retail": int,
                    "4_3_publicServices": int
                },
                ...
            },

            "percentatges": pandas.DataFrame
        }
    """

    dades = agregar_usos_zones(
        edificis=edificis,
        zones=zones
    )

    percentatges = calcular_percentatges_usos(
        resultats=dades
    )

    return {
        "dades": dades,
        "percentatges": percentatges
    }
