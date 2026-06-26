"""ANÀLISI ESPACIAL"""

import pandas as pd


def resum_usos_districtes(edificis, districtes):
    """
    Funció que retorna el nombre d'edificis destinats a cada ús en cada districte
    """

    # Definició de les categories
    usos = [
        "1_residential",
        "2_agriculture",
        "3_industrial",
        "4_1_office",
        "4_2_retail",
        "4_3_publicServices"
    ]

    # Diccionari per emmagatzemar els resultats per districtes
    resultats = {}

    # Llistat de districtes
    districtes_llista = list(districtes.getFeatures())

    # Iteració sobre cada districte
    for districte in districtes_llista:
        # Obtenció del nom del districte
        nom = str(districte["NOM"]).strip()
        
        # Creació de valors 0 inicials per cada categoria d'ús en el districte
        resultats[nom] = {
            us: 0
            for us in usos
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
    Funció que retorna una taula DataFrame a partir d'un diccionari de valors
    """

    # Transformació de diccionari a DataFrame
    df = pd.DataFrame(resultats)

    # Transposició de la matriu i addició de nom dels índex 
    df = df.T

    df.index.name = "Districte"

    return df


def percentatge_usos_districtes(df):
    """
    Funció que retorna una taula DataFrame del percentatge d'ús de cada edifici a cada districte
    Paràmetres: df resultat de la funció *taula_usos_districtes()*
    """

    # Obtenció del número total d'edificis per districte
    df_totals = df.sum(axis=1)

    # Càlcul del percentatge de cada ús
    df_pct = df.div(df_totals, axis=0) * 100

    return df_pct