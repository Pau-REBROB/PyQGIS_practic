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
    QgsSpatialIndex,
    QgsGeometry,
    QgsFeatureRequest,
    QgsField
)
from qgis.PyQt.QtCore import QVariant

import config

def calcular_densitat_per_zona(edificis, camp_id_edifici, zones, camp_id_zona):
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
    index_edificis = QgsSpatialIndex(edificis.getFeatures())

    densitats = {}

    for zona in zones.getFeatures():
        id_zona = zona[camp_id_zona]
        geometria_zona = zona.geometry()
        # Superfície de la zona en km^2
        superficie_zona = geometria_zona.area() / 1000000

        # Fase ràpida: edificis candidats per bbox
        candidats = index_edificis.intersects(geometria_zona.boundingBox())

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
# La pròpia documentació de QgsSpatialIndex.intersects() ho diu explícitament: 
# la comprovació d'intersecció es fa només amb els bounding boxes de les geometries, de manera que per a geometries 
# que no són punts cal comprovar manualment la intersecció exacta amb les features retornades quan es necessiti precisió. 
# És literalment el "broad phase / narrow phase" que comentàvem — és el comportament documentat i esperat de l'índex.

# L'algorisme oficial de QGIS "Count points in polygon" (el que hi ha al Processing Toolbox) segueix exactament aquesta
#  mateixa lògica en dos passos: primer obté els punts candidats amb spatialIndex.intersects(geom.boundingBox()), i després, 
# per a cada candidat, verifica la intersecció exacta. 

# Dues diferències respecte a la teva versió, que val la pena que coneguis:
# QgsGeometry.createGeometryEngine() + engine.prepareGeometry() en comptes de geometria_zona.intersects(...) repetit.
#  El codi font oficial crea un "geometry engine" preparat una sola vegada per polígon (engine.prepareGeometry()) i
#  després el reutilitza per a cada comprovació d'intersecció exacta contra els candidats. És una optimització de GEOS: si 
# vas a comprovar la mateixa geometria de zona contra molts candidats (com fas tu, dins del bucle de zones), preparar-la un cop
#  és més ràpid que cridar .intersects() directament cada vegada, perquè evita recalcular estructures internes de la geometria 
# a cada crida. 
# QgsFeatureRequest().setFilterFids(candidats) en comptes de getFeature(fid) dins d'un bucle. El mateix exemple oficial 
# construeix una QgsFeatureRequest amb setFilterFids() per recuperar tots els candidats d'un cop, en lloc de cridar getFeature()
#  una vegada per cada fid — més eficient quan hi ha molts candidats, perquè és una sola consulta a la capa en comptes de moltes.


def escriure_valors_zonals_a_capa(zones, dict_valors, camp_id_zona, nom_camp_resultat):
    """
    Escriu un diccionari de resultats { id_zona: valor } com a nou camp
    d'una còpia de la capa de zones, sense modificar la capa original.

    Paràmetres
    ----------
    zones : QgsVectorLayer
        Capa de polígons de zonificació (barris, districtes, hexàgons, etc.).
    diccionari_valors : dict
        Diccionari { id_zona: valor }, típicament la sortida d'una funció
        d'agregació (p. ex. calcular_densitat_per_zona).
    camp_id_zona : str
        Nom del camp identificador de la zona, usat per fer coincidir
        cada feature amb la seva entrada al diccionari.
    nom_camp_resultat : str
        Nom del nou camp on s'escriurà el valor.

    Retorna
    -------
    QgsVectorLayer
        Còpia en memòria de `zones` amb el nou camp afegit i emplenat.
        Les zones sense entrada al diccionari queden amb el camp a NULL.
    """
    capa_resultat = zones.materialize(QgsFeatureRequest())
    capa_resultat.setName(f"{zones.name()}_{nom_camp_resultat}")

    provider = capa_resultat.dataProvider()
    provider.addAttributes([
        QgsField(nom_camp_resultat, QVariant.Double)
    ])
    capa_resultat.updateFields()

    idx_camp = capa_resultat.fields().indexOf(nom_camp_resultat)

    # Diccionari de canvis en bloc: { id_feature: {idx_camp: valor} }
    canvis = {
        feature.id(): {idx_camp: dict_valors.get(feature[camp_id_zona])}
        for feature in capa_resultat.getFeatures()
    }

    provider.changeAttributeValues(canvis)
    capa_resultat.updateFields()

    return capa_resultat

###FUNCIÓ DE REFERÈNCIA
# changeAttributeValues() en bloc (provider), no changeAttributeValue() un per un dins un bucle amb startEditing()
# Aquí sí hi ha una diferència real. El tutorial oficial mostra que actualitzar valors és responsabilitat del dataProvider,
#  amb changeAttributeValues() (plural) rebent un diccionari de tots els canvis d'un cop: { id_feature: {idx_camp: valor} }.
#  Això és més eficient que el meu bucle startEditing() + changeAttributeValue() feature a feature, perquè és una
#  sola crida en lloc de N crides transaccionades.
# ja no hi ha startEditing()/commitChanges() ni bucle amb changeAttributeValue() un a un — es construeix el diccionari complet
#  de canvis i s'aplica d'un sol cop amb provider.changeAttributeValues(canvis). És el patró que la documentació oficial mostra
#  per actualitzar valors després d'afegir un camp.



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
