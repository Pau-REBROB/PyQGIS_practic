"""
Agregacions estadístiques
=========================

Mòdul que agrupa les funcions d'agregació estadística del projecte.

Organització
------------

- Agregació per districtes
    Funcions per calcular el nombre i el percentatge d'edificis
    segons el seu ús dins de cada districte.

Les funcions s'organitzen en tres nivells:
    - funcions bàsiques d'agregació;
    - funcions de transformació dels resultats;
    - funcions d'alt nivell que orquestren el procés complet.
"""

import pandas as pd

import config


def agregar_usos_districtes(edificis, districtes):
    """
    Agrupa el nombre d'edificis de cada ús per cada districte.

    Per a cada edifici, determina el districte al qual pertany a partir del
    centroide de la seva geometria i incrementa el comptador de l'ús
    corresponent.

    Paràmetres
    ----------
    edificis: QgsVectorLayer
        Capa vectorial dels edificis.
    districtes: QgsVectorLayer
        Capa vectorial dels districtes.

    Retorna
    -------
    dict
        Diccionari amb el recompte d'edificis destinats a cada ús per districte
        {
            "Nom_districte": {
                "1_residential": int,
                "2_agriculture": int,
                ...
            },
            ...
        }
    """

    resultats = {}

    districtes_llista = list(districtes.getFeatures())

    # Iteració sobre cada districte
    for districte in districtes_llista:
        # Obtenció del nom del districte
        nom = str(districte["NOM"]).strip()
        
        # Creació de valors 0 inicials per cada categoria d'ús en el districte
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

        # Cerca del districte al qual pertany l'edifici
        # amb la comprovació de a quin districte es troba el seu centroide
        for districte in districtes_llista:
            if geom_edifici.centroid().within(districte.geometry()):
                nom = districte["NOM"]
                # Actualització del comptador d'usos
                resultats[nom][us] += 1

                break
    
    return resultats


def taula_usos_districtes(resultats):
    """
    Construeix una taula amb el nombre d'edificis de cada ús per districte.

    Transforma el diccionari retornat per `agregar_usos_districtes()` en un
    DataFrame, on cada fila representa un districte i cada columna un ús
    dels edificis.

    Paràmetres
    ----------
    resultats: dict

    Retorna
    -------
    pandas.DataFrame

        Índex
            Districte
        Columnes
            - 1_residential
            - 2_agriculture
            - 3_industrial
            - 4_1_office
            - 4_2_retail
            - 4_3_publicServices   
    """

    df = pd.DataFrame(resultats)

    df = df.T

    df.index.name = "Districte"

    return df


def percentatge_usos_districtes(df):
    """
    Calcula el percentatge d'edificis de cada ús per districte.

    A partir de la taula amb el nombre d'edificis de cada ús,
    calcula el pes percentual de cada categoria respecte el total
    d'edificis del districte.

    Paràmetres
    ----------
    df: pandas.DataFrame

    Retorna
    -------
    df_pct: pandas.DataFrame
        Mateixa estructura que la taula d'entrada,
        però amb els valors expressats en percentatge.
    """

    # Obtenció del número total d'edificis per districte
    df_totals = df.sum(axis=1)

    df_pct = df.div(df_totals, axis=0) * 100

    return df_pct


def analisi_districtes(edificis, districtes):
    """
    Executa l'anàlisi dels usos dels edificis per districtes.

    L'anàlisi genera, de forma consecutiva:
        - el recompte d'edificis per ús i per districte,
        - la taula resum amb els valors absoluts,
        - la taula amb els percentatges corresponents.
    
    Paràmetres
    ----------
    edificis: QgsVectorLayer
        Capa vectorial dels edificis.
    districtes: QgsVectorLayer
        Capa vectorial dels districtes.
    
    Retorna
    -------
    dict
        {
            "dades": {
                "Nom_districte": {
                    "1_residential": int,
                    "2_agriculture": int,
                    "3_industrial": int,
                    "4_1_office": int,
                    "4_2_retail": int,
                    "4_3_publicServices": int
                },
                ...
            },

            "taula": pandas.DataFrame,

            "percentatges": pandas.DataFrame
        }
    """

    resultats = {}

    resultats["dades"] = agregar_usos_districtes(
        edificis=edificis,
        districtes=districtes
    )

    resultats["taula"] = taula_usos_districtes(
        resultats=resultats["dades"]
    )

    resultats["percentatges"]= percentatge_usos_districtes(
        df=resultats["taula"]
    )

    return resultats