"""
Agregacions estadístiques
=========================

Mòdul que agrupa les funcions d'agregació i càlcul estadístic
sobre edificis i zones territorials.

Organització
------------

- Recompte d'edificis per zona.
- Càlcul de superfícies construïdes per zona.
- Càlcul de densitats d'edificis i de superfície construïda.
- Classificació de zones segons intervals de valors.
- Escriptura de resultats en capes vectorials.
- Agrupació de valors i comparació de medianes per zona.
"""

from qgis.core import (
    QgsSpatialIndex,
    QgsGeometry,
    QgsFeatureRequest,
    QgsField
)
from qgis.PyQt.QtCore import QVariant

from statistics import median


def calcular_edificis_per_zona(edificis, camp_id_edifici, zones, camp_id_zona):
    """
    Compta el nombre d'edificis assignats a cada zona.

    Cada edifici s'assigna a la zona que conté el seu centroide.
    Així, un edifici només es compta en una zona, encara que
    la seva geometria travessi diversos polígons.

    Els edificis amb geometria buida o sense centroide vàlid
    s'ignoren. Si el camp identificador és nul, s'utilitza
    el FID intern de QGIS com a identificador alternatiu.

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
        Diccionari { id_zona: nombre_edificis }.
        Les zones sense cap edifici assignat hi apareixen amb valor 0.
    """
    index_edificis = QgsSpatialIndex(edificis.getFeatures())

    recompte = {}

    for zona in zones.getFeatures():
        id_zona = zona[camp_id_zona]
        geometria_zona = zona.geometry()

        # Geometria de zona buida: no es poden fer assignacions
        if geometria_zona.isNull() or geometria_zona.isEmpty():
            recompte[id_zona] = 0
            continue
        
        # Índex espacial: selecció ràpida dels edificis candidats per bbox
        candidats = index_edificis.intersects(
            geometria_zona.boundingBox()
        )

        request = QgsFeatureRequest().setFilterFids(candidats)

        # Geometry engine preparat un sol cop per zona, reutilitzat per
        # a cada candidat
        engine = QgsGeometry.createGeometryEngine(
            geometria_zona.constGet()
        )
        engine.prepareGeometry()

        # Fase precisa: verificació exacta + identificador real per evitar duplicats
        ids_edificis_zona = set()

        for feature in edificis.getFeatures(request):
            geometria_edifici = feature.geometry()

            if geometria_edifici.isNull() or geometria_edifici.isEmpty():
                continue

            centroide = geometria_edifici.centroid()

            if centroide.isNull() or centroide.isEmpty():
                continue

            # Assignació d'edifici a zona per centroide,
            # no per intersecció de l'edifici
            if engine.contains(centroide.constGet()):
                id_edifici = feature[camp_id_edifici]

                # Fallback al FID si l'identificador propi és nul
                if id_edifici is None:
                    id_edifici = ("fid", feature.id())

                ids_edificis_zona.add(id_edifici)

        recompte[id_zona] = len(ids_edificis_zona)

    return recompte


def calcular_superficie_per_zona(edificis, zones, camp_id_zona):
    """
    Calcula la superfície construïda d'edificis industrials dins
    de cada zona.

    La superfície s'assigna proporcionalment a la intersecció
    entre la geometria de cada edifici i la geometria de la zona.

    Paràmetres
    ----------
    edificis : QgsVectorLayer
        Capa d'edificis a comptar.
    zones : QgsVectorLayer
        Capa de polígons de zonificació (barris, districtes, etc.).
    camp_id_zona : str
        Nom del camp identificador de la zona dins de `zones`
        (p. ex. "BARRI" o "DISTRICTE").

    Retorna
    -------
    dict
        Diccionari { id_zona: superficie_m2 }.
        Les zones sense cap edifici assignat hi apareixen amb valor 0.
    """
    # Comprovació del SRC
    if edificis.crs() != zones.crs():
        raise ValueError(
            "Les capes d'edificis i zones han de tenir el mateix CRS (25831)"
        )

    if edificis.crs().isGeographic():
        raise ValueError(
            "Cal utilitzar un CRS projectat per calcular les superfícies"
        )

    # Índex espacial dels edificis
    index_edificis = QgsSpatialIndex(edificis.getFeatures())

    superficies = {}

    for zona in zones.getFeatures():
        id_zona = zona[camp_id_zona]
        geometria_zona = zona.geometry()

        # Zona sense geometria vàlida
        if geometria_zona.isNull() or geometria_zona.isEmpty():
            superficies[id_zona] = 0.0
            continue

        # Cerca d'edificis candidats per bbox
        candidats = index_edificis.intersects(
            geometria_zona.boundingBox()
        )

        request = QgsFeatureRequest().setFilterFids(candidats)

        superficie_total = 0.0

        for edifici in edificis.getFeatures(request):
            geometria_edifici = edifici.geometry()

            if geometria_edifici.isNull() or geometria_edifici.isEmpty():
                continue

            # Calcular la part de l'edifici situada dins de la zona
            interseccio = geometria_edifici.intersection(
                geometria_zona
            )

            if interseccio.isNull() or interseccio.isEmpty():
                continue

            superficie_total += interseccio.area()

        superficies[id_zona] = superficie_total

    return superficies


def calcular_densitat_edificis_per_zona(edificis, camp_id_edifici, zones, camp_id_zona):
    """
    Calcula la densitat d'edificis per km² per cada zona.

    Cada edifici s'assigna a la zona que conté el seu centroide.
    Per tant, cada edifici només es compta en una zona, sempre
    que les zones no se solapin.

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
        Diccionari { id_zona: edificis_per_km2 }.
        Les zones sense cap edifici assignat hi apareixen amb valor 0.
    """
    # Comprovació del sistema de coordenades
    if edificis.crs() != zones.crs():
        raise ValueError(
            "Les capes d'edificis i zones han de tenir el mateix CRS."
        )

    if edificis.crs().isGeographic():
        raise ValueError(
            "Cal utilitzar un CRS projectat per calcular densitats."
        )

    # Índex espacial dels edificis
    index_edificis = QgsSpatialIndex(edificis.getFeatures())

    densitats = {}

    for zona in zones.getFeatures():
        id_zona = zona[camp_id_zona]
        geometria_zona = zona.geometry()

        if geometria_zona.isNull() or geometria_zona.isEmpty():
            densitats[id_zona] = 0.0
            continue
        
        # Superfície de la zona en km^2
        superficie_zona = geometria_zona.area() / 1000000

        if superficie_zona <= 0:
            raise ValueError(
                f"La zona {id_zona} té una superfície nul·la o negativa."
            )

        # Cerca d'edificis candidats per bbox
        candidats = index_edificis.intersects(
            geometria_zona.boundingBox()
        )

        request = QgsFeatureRequest().setFilterFids(candidats)

        # Geometry engine preparat un sol cop per zona, reutilitzat per
        # a cada candidat
        engine = QgsGeometry.createGeometryEngine(geometria_zona.constGet())
        engine.prepareGeometry()  

        # Verificació exacta + identificador real per evitar duplicats
        ids_edificis_zona = set()

        for edifici in edificis.getFeatures(request):
            geometria_edifici = edifici.geometry()

            if geometria_edifici.isNull() or geometria_edifici.isEmpty():
                continue

            centroide = geometria_edifici.centroid()

            if centroide.isNull() or centroide.isEmpty():
                continue

            # Assignació per centroide
            if engine.contains(centroide.constGet()):
                id_edifici = edifici[camp_id_edifici]

                # Fallback al FID si l'identificador és nul
                if id_edifici is None:
                    id_edifici = ("fid", edifici.id())

                ids_edificis_zona.add(id_edifici)
        
        # Càlcul de la densitat
        densitats[id_zona] = (
            len(ids_edificis_zona) / superficie_zona
        )

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


def calcular_densitat_superficie_per_zona(edificis, zones, camp_id_zona):
    """
    Calcula el percentatge de superfície de cada zona ocupat
    per les petjades dels edificis.

    La superfície dels edificis s'assigna proporcionalment
    a la intersecció amb cada zona.

    Paràmetres
    ----------
    edificis : QgsVectorLayer
        Capa d'edificis a comptar.
    zones : QgsVectorLayer
        Capa de polígons de zonificació (barris, districtes, etc.).
    camp_id_zona : str
        Nom del camp identificador de la zona dins de `zones`
        (p. ex. "BARRI" o "DISTRICTE").

    Retorna
    -------
    dict
        Diccionari { id_zona: percentatge_superficie_ocupada }.
    """
    # Comprovació del sistema de coordenades
    if edificis.crs() != zones.crs():
        raise ValueError(
            "Les capes d'edificis i zones han de tenir el mateix CRS."
        )

    if edificis.crs().isGeographic():
        raise ValueError(
            "Cal utilitzar un CRS projectat per calcular superfícies."
        )

    # Índex espacial dels edificis
    index_edificis = QgsSpatialIndex(edificis.getFeatures())

    densitats = {}

    for zona in zones.getFeatures():
        id_zona = zona[camp_id_zona]
        geometria_zona = zona.geometry()

        if geometria_zona.isNull() or geometria_zona.isEmpty():
            densitats[id_zona] = 0.0
            continue

        # Superfície de la zona en m²
        superficie_zona = geometria_zona.area()

        if superficie_zona <= 0:
            raise ValueError(
                f"La zona {id_zona} té una superfície nul·la o negativa."
            )

        # Cerca d'edificis candidats per bbox
        candidats = index_edificis.intersects(geometria_zona.boundingBox())

        request = QgsFeatureRequest().setFilterFids(candidats)

        superficie_edificis = 0.0

        for edifici in edificis.getFeatures(request):
            geometria_edifici = edifici.geometry()

            if geometria_edifici.isNull() or geometria_edifici.isEmpty():
                continue

            # Superfície de l'edifici situada dins de la zona
            interseccio = geometria_edifici.intersection(
                geometria_zona
            )

            if interseccio.isNull() or interseccio.isEmpty():
                continue

            superficie_edificis += interseccio.area()
       
        # Percentatge de superfície ocupada
        densitats[id_zona] = (
            superficie_edificis / superficie_zona
        ) * 100

    return densitats


def comptar_zones_per_classe(dict_valors, breaks):
    """
    Compta quantes zones cauen a cada classe d'una classificació de breaks,
    útil per diagnosticar l'efecte MAUP (Modifiable Areal Unit Problem):
    com més gran és la unitat d'agregació, més es concentren els valors
    en poques classes.

    La primera classe és tancada als dos costats [breaks[0], breaks[1]]
    (pensada per capturar exactament el valor 0 com a classe pròpia);
    la resta de classes són obertes per l'esquerra i tancades per la
    dreta (breaks[i], breaks[i+1]].

    Paràmetres
    ----------
    dict_valors : dict
        Diccionari { id_zona: valor }, amb els valors que es volen
        classificar per a cada zona.
    breaks : list[float]
        Llindars de classificació compartits (p. ex. config.BREAKS_DENSITAT_INDUSTRIAL).

    Retorna
    -------
     dict
        Diccionari { etiqueta_interval: recompte_zones }, amb tantes
        entrades com classes (len(breaks) - 1). La primera clau és
        "Sense indústria"; la resta, "lower-upper" amb 2 decimals.
    """
    valors = list(dict_valors.values())

    recomptes = {}

    for i in range(len(breaks) - 1):
        lower, upper = breaks[i], breaks[i + 1]

        if i == 0:
            recompte = sum(1 for valor in valors if lower <= valor <= upper)
            etiqueta = "Sense indústria"
        else:
            recompte = sum(1 for valor in valors if lower < valor <= upper)
            etiqueta = f"{lower:.2f}-{upper:.2f}"

        recomptes[etiqueta] = recompte

    return recomptes


def escriure_valors_zonals_a_capa(zones, dict_valors, camp_id_zona, nom_camp_resultat):
    """
    Escriu un diccionari de resultats { id_zona: valor } com a nou camp
    d'una còpia de la capa de zones, sense modificar la capa original.

    Les zones sense entrada al diccionari queden amb valor NULL.

    Paràmetres
    ----------
    zones : QgsVectorLayer
        Capa de polígons de zonificació (barris, districtes, hexàgons, etc.).
    diccionari_valors : dict
        Diccionari { id_zona: valor }, típicament la sortida d'una funció
        d'agregació (p. ex. calcular_densitat_per_zona).
    camp_id_zona : str
        Nom del camp identificador de la zona.
    nom_camp_resultat : str
        Nom del nou camp resultat on s'escriurà el valor.

    Retorna
    -------
    QgsVectorLayer
        Còpia en memòria de `zones` amb el nou camp afegit i emplenat.
    
    Raises
    ------
    ValueError
        Si la capa o els paràmetres no son vàlids.
    RuntimeError
        Si falla alguna operació del proveïdor de dades.
    """
    # Validacions inicials
    if not zones or not zones.isValid():
        raise ValueError(
            "La capa de zones no és vàlida."
        )

    if not isinstance(dict_valors, dict):
        raise ValueError(
            "dict_valors ha de ser un diccionari."
        )

    if not nom_camp_resultat:
        raise ValueError(
            "Cal indicar un nom per al camp de resultats."
        )

    if zones.fields().indexOf(camp_id_zona) == -1:
        raise ValueError(
            f"El camp identificador {camp_id_zona} no existeix a la capa."
        )

    if zones.fields().indexOf(nom_camp_resultat) != -1:
        raise ValueError(
            f"El camp '{nom_camp_resultat}' ja existeix a la capa."
        )

    # Creació d'una còpia en memòria
    capa_resultat = zones.materialize(QgsFeatureRequest())

    if not capa_resultat.isValid():
        raise RuntimeError(
            "No s'ha pogut crear la còpia de la capa de zones."
        )
    
    capa_resultat.setName(f"{zones.name()}_{nom_camp_resultat}")

    provider = capa_resultat.dataProvider()

    # Addició del camp resultat
    resultat = provider.addAttributes([
        QgsField(nom_camp_resultat, QVariant.Double)
    ])

    if not resultat:
        raise RuntimeError(
            f"No s'ha pogut afegir el camp '{nom_camp_resultat}'."
        )
    
    capa_resultat.updateFields()

    idx_camp = capa_resultat.fields().indexOf(nom_camp_resultat)

    if idx_camp == -1:
        raise RuntimeError(
            "El camp de resultat no apareix després d'afegir-lo."
        )

    # Preparació del diccionari de canvis en bloc
    canvis = {
        feature.id(): {idx_camp: dict_valors.get(feature[camp_id_zona])}
        for feature in capa_resultat.getFeatures()
    }

    # Escriptura dels valors en bloc
    resultat = provider.changeAttributeValues(canvis)

    if not resultat:
        raise RuntimeError(
            "No s'han pogut escriure els valors al camp de resultat."
        )
    
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


def agrupar_valors_per_zona(edificis, camp_valor, zones, camp_id_zona):
    """
    Agrupa el valor d'un camp dels edificis per zona.

    Cada edifici s'assigna a la zona que conté el seu centroide.

    Les zones sense edificis vàlids apareixen amb una llista buida.

    Paràmetres
    ----------
    edificis : QgsVectorLayer
        Capa d'edificis.
    camp_valor : str
        Camp dels edificis a agrupar (p. ex. "any_construccio").
    zones : QgsVectorLayer
        Capa de polígons de zonificació (barris, districtes, etc.).
    camp_id_zona : str
        Nom del camp identificador de la zona dins de `zones`.

    Retorna
    -------
    dict
        Diccionari { id_zona: [valors] }.
    
    Raises
    ------
    ValueError
        Si les capes, els camps o els sistemes de referència
        de coordenades no son vàlids.
    """
    # Validacions inicials
    if not edificis or not edificis.isValid():
        raise ValueError(
            "La capa d'edificis no és vàlida."
        )

    if not zones or not zones.isValid():
        raise ValueError(
            "La capa de zones no és vàlida."
        )

    if edificis.fields().indexOf(camp_valor) == -1:
        raise ValueError(
            f"El camp '{camp_valor}' no existeix a la capa d'edificis."
        )

    if zones.fields().indexOf(camp_id_zona) == -1:
        raise ValueError(
            f"El camp identificador '{camp_id_zona}' no existeix a la capa de zones."
        )

    if edificis.crs() != zones.crs():
        raise ValueError(
            "Les capes d'edificis i zones tenen SRC diferents."
        )

    # Índex espacial dels edificis
    index_edificis = QgsSpatialIndex(edificis.getFeatures())

    valors_per_zona = {}

    # Recórrer les zones
    for zona in zones.getFeatures():
        geometria_zona = zona.geometry()

        if geometria_zona.isNull() or geometria_zona.isEmpty():
            raise ValueError(
                f"La zona amb identificador '{zona[camp_id_zona]}' "
                "té una geometria buida."
            )

        engine = QgsGeometry.createGeometryEngine(geometria_zona.constGet())
        engine.prepareGeometry()

        candidats = index_edificis.intersects(geometria_zona.boundingBox())
        
        request = QgsFeatureRequest().setFilterFids(candidats)

        valors = []

        for feature in edificis.getFeatures(request):
            valor = feature[camp_valor]

            # Ignorar valors nuls
            if valor is None:
                continue

            geometria_edifici = feature.geometry()
                        
            # Ignorar geometries buides
            if geometria_edifici.isNull() or geometria_edifici.isEmpty():
                continue

            centroide = geometria_edifici.centroid()

            if centroide.isNull() or centroide.isEmpty():
                continue

            # Assignació de l'edifici només si la zona conté estrictament el centroide
            if engine.contains(centroide.constGet()):
                valors.append(valor)

        valors_per_zona[zona[camp_id_zona]] = valors

    return valors_per_zona


def calcular_diferencia_mediana_per_zona(valors_industrial, valors_resta, minim_edificis=5):
    """
    Calcula la diferència entre la mediana d'un valor de dos conjunts
    d'edificis (industrials i resta) per zona.

    La diferència es calcula com:
        mediana industrial - mediana resta

    Només es calcula quan tots dos grups tenen com a mínim
    el nombre d'edificis indicat a minim_edificis.

    Un valor positiu indica que el conjunt industrial té valors
    més alts (p. ex. anys de construcció més recents) que la resta.

    Paràmetres
    ----------
    valors_industrial, valors_resta : dict
        Diccionaris { id_zona: [valors] }, sortida d'agrupar_valors_per_zona.
    minim_edificis : int
        Nombre mínim d'edificis que ha de tenir cadascun dels dos grups
        perquè es calculi la diferència de medianes.

    Retorna
    -------
    dict
        Diccionari { id_zona: diferencia_mediana o None }.
    
    Raises
    ------
    ValueError
        Si el nombre mínim d'edificis no és un enter positiu.
    """
    if not isinstance(minim_edificis, int) or isinstance(minim_edificis, bool) or minim_edificis < 1:
        raise ValueError(
            "minim_edificis ha de ser un enter positiu"
        )
    
    diferencia = {}

    # Considerar totes les zones presents en qualsevol dels dos diccionaris
    totes_les_zones = set(valors_industrial) | set(valors_resta)

    for id_zona in totes_les_zones:
        valors_ind = valors_industrial.get(id_zona, [])
        valors_res = valors_resta.get(id_zona, [])

        # Exigir el mínim d'edificis en tots dos grups
        if (
            len(valors_ind) < minim_edificis or
            len(valors_res) < minim_edificis
        ):
            diferencia[id_zona] = None

        else:
            diferencia[id_zona] = (
                median(valors_ind) - median(valors_res)
            )

    return diferencia
