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

from qgis.core import (
    QgsGeometry,
    QgsFeatureRequest
)

import config

def calcular_densitat_per_zona(edificis, idx_edificis, camp_id_edifici, zones, camp_id_zona):
    """
    Calcula la densitat d'edificis (edificis/km²) per cada zona.

    Fa un join espacial entre els edificis i els polígons de zonificació:
    primer descarta candidats per bounding box mitjançant l'índex espacial
    (fase ràpida i aproximada) i després verifica la intersecció exacta amb
    un geometry engine preparat (fase lenta i precisa). Compta els edificis
    per identificador real (no per fid intern de QGIS) i divideix pel valor
    de la superfície de la zona en km².

    Paràmetres
    ----------
    edificis : QgsVectorLayer
        Capa d'edificis a comptar.
    idx_edificis: QgsSpatialIndex
        Índex espacial de la capa d'edificis.
    camp_id_edifici : str
        Nom del camp identificador de l'edifici dins de `edificis`
        (p. ex. "gml_id" o "referenciaCadastral"), usat per identificar
        cada edifici de manera estable, en lloc del fid intern de QGIS.
    zones : QgsVectorLayer
        Capa de polígons de zonificació (barris, districtes, etc.).
    camp_id_zona : str
        Nom del camp identificador de la zona dins de `zones`
        (p. ex. "BARRI" o "DISTRICTE").

    Retorna
    -------
    dict
        Diccionari { id_zona: densitat_edificis_km2 }.
        Les zones sense cap edifici assignat hi apareixen amb valor 0.
    """
    densitats = {}

    for zona in zones.getFeatures():
        id_zona = zona[camp_id_zona]
        geometria_zona = zona.geometry()
        # Superfície de la zona en km^2
        superficie_zona = geometria_zona.area() / 1000000

        # Fase ràpida: edificis candidats per bbox
        candidats = idx_edificis.intersects(geometria_zona.boundingBox())

        # Geometry engine preparat un sol cop per zona, reutilitzat per
        # a cada candidat (més ràpid que geometria_zona.intersects(...)
        # cridat repetidament dins del bucle)
        engine = QgsGeometry.createGeometryEngine(geometria_zona.constGet())
        engine.prepareGeometry()

        # Recuperació en bloc dels candidats (una sola consulta a la capa,
        # en lloc d'una crida a getFeature() per cada fid)
        request = QgsFeatureRequest().setFilterFids(candidats)

        # Fase precisa: verificació exacta + identificador real per evitar duplicats
        ids_edificis_zona = {
            feature[camp_id_edifici]
            for feature in edificis.getFeatures(request)
            if engine.intersects(feature.geometry().constGet())
        }
        
        recommpte = len(ids_edificis_zona)

        densitats[id_zona] = recommpte / superficie_zona if superficie_zona > 0 else 0

    return densitats

### FUNCIÓ DE REFERÈNCIA!!!



def agregar_usos_zones(edificis, zones, idx_zones):
    """
    Agrupa el nombre d'edificis de cada ús per cada zona.

    Per a cada edifici, determina la unitat administrativa a la qual
    pertany a partir del centroide de la seva geometria i
    incrementa el comptador de l'ús corresponent.

    Utilitza l'índex espacial precalculat per optimitzar la
    cerca de la zona corresponent a cada edifici.

    Paràmetres
    ----------
    edificis: QgsVectorLayer
        Capa vectorial dels edificis.
    zona: QgsVectorLayer
        Capa vectorial de les unitats administratives.
    idx_zones: QgsSpatialIndex
        Índex espacials de les unitats administratives.

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

    # ######
    # resultats = {}

    # zones_llista = list(zones.getFeatures())

    # # Iteració sobre cada zona
    # for zona in zones_llista:
        
    #     nom = str(zona["NOM"]).strip()
        
    #     # Creació de valors 0 inicials per cada categoria d'ús a la zona
    #     resultats[nom] = {
    #         us: 0
    #         for us in config.USOS
    #     }

    # # Iteració sobre cada edifici
    # for edifici in edificis.getFeatures():
    #     # Extracció geometria de l'edifici
    #     geom_edifici = edifici.geometry()

    #     # Obtenció de l'ús de l'edifici
    #     us = str(edifici["currentUse"]).strip()

    #     # descartar els usos nuls
    #     if us == "NULL":
    #         continue

    #     # Cerca de la zona a la qual pertany l'edifici
    #     # amb la comprovació d'on es troba el seu centroide
    #     for zona in zones_llista:
    #         if geom_edifici.centroid().within(zona.geometry()):
    #             nom = zona["NOM"]
    #             # Actualització del comptador d'usos
    #             resultats[nom][us] += 1

    #             break
    
    # return resultats


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


def analisi_usos_zones(edificis, zones, idx_zones):
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
    idx_zones: QgsSpatialIndex
            Índex espacials de les unitats administratives.
    
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
