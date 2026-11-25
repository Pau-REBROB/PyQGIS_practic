"""
Anàlisi temporal
================

Mòdul que agrupa les funcions d'anàlisi temporal i estadística del projecte.

Organització
------------

- ###

Les funcions s'organitzen en tres nivells:
    - funcions bàsiques d'agregació;
    - funcions de transformació dels resultats;
    - funcions d'alt nivell que orquestren el procés complet.
"""

from qgis.core import (
    QgsFeatureRequest,
    QgsField,
    QgsGeometry,
    QgsSpatialIndex
)

from PyQt5.QtCore import QVariant

from datetime import datetime
from collections import Counter

def extreure_any(valor):
    """
    Extreu l'any d'un camp de data en format ISO 8601,
    és a dir yyyy-mm-ddThh:mm:ss.
    """
    if valor is None:
        return None

    try:
        # Convertir string a datetime i extreure l'any
        data = datetime.strptime(str(valor)[:10], "%Y-%m-%d")
        return data.year
    except ValueError:
        return None


def extreure_any_edificis(edificis):
    """
    Extreu l'any de la capa vectorials d'edificis
    per al seu anàlisi.
    """
    # Validacions
    if edificis is None or not edificis.isValid():
        raise ValueError(
            "La capa d'edificis no és vàlida."
        )

    if edificis.fields().indexFromName("end") == -1:
        raise ValueError(
            "La capa no conté el camp obligatori `end`."
        )

    anys = [
        extreure_any(feat["end"])
        for feat in edificis.getFeatures()
        if feat["end"] is not None
    ]

    # Filtrar anys nuls
    anys = [
        a 
        for a in anys
        if a is not None and a >= 1500
    ]

    distribucio = Counter(anys)

    distribucio_anys = {
        "<1859": 0,
        "1859-1900": 0,
        "1900-1936": 0,
        "1936-1945": 0,
        "1945-1960": 0,
        "1960-1980": 0,
        "1980-2000": 0,
        "2000-2008": 0,
        "2008-2015": 0,
        "2015-2026": 0 
    }

    for any, n in sorted(distribucio.items()):
        #print(f"{any}: {n}")
        if any < 1859:
            distribucio_anys["<1859"] += n
        elif any >= 1859 and any < 1900:
            distribucio_anys["1859-1900"] += n
        elif any >= 1900 and any < 1936:
            distribucio_anys["1900-1936"] += n
        elif any >= 1936 and any < 1945:
            distribucio_anys["1936-1945"] += n
        elif any >= 1945 and any < 1960:
            distribucio_anys["1945-1960"] += n
        elif any >= 1960 and any < 1980:
            distribucio_anys["1960-1980"] += n
        elif any >= 1980 and any < 2000:
            distribucio_anys["1980-2000"] += n
        elif any >= 2000 and any < 2008:
            distribucio_anys["2000-2008"] += n
        elif any >= 2008 and any < 2015:
            distribucio_anys["2008-2015"] += n
        else:
            distribucio_anys["2015-2026"] += n

    return distribucio_anys


def afegir_any_construccio(edificis):
    """
    Crea una còpia de la capa d'edificis i hi incorpora l'any de construcció.

    Extreu l'any del camp 'end' mitjançant extreure_any(). Els anys
    anteriors a 1500 es consideren invàlids i s'assignen com a NULL.

    Si el camp 'any_construccio' no existeix, el crea com a enter.
    Si ja existeix, en recalcula els valors.

    Parameters
    ----------
    edificis : QgsVectorLayer
        Capa d'edificis amb el camp 'end'.

    Returns
    -------
    QgsVectorLayer
        Còpia de la capa d'entrada amb el camp 'any_construccio'
        actualitzat.

    Raises
    ------
    ValueError
        Si la capa d'entrada no és vàlida o no conté el camp 'end'.
    RuntimeError
        Si no es pot crear la còpia, afegir el camp o actualitzar
        els atributs.
    """
    # Validacions
    if edificis is None or not edificis.isValid():
        raise ValueError(
            "La capa d'edificis no és vàlida."
        )

    if edificis.fields().indexFromName("end") == -1:
        raise ValueError(
            "La capa no conté el camp obligatori 'end'."
        )

    # Crear una còpia de la capa
    layer = edificis.materialize(QgsFeatureRequest())

    if not layer.isValid():
        raise RuntimeError("No s'ha pogut crear una còpia vàlida de la capa.")

    provider = layer.dataProvider()

    # Comprovar si el camp ja existeix
    idx_any = layer.fields().indexFromName("any_construccio")

    # Crear el camp si no existeix
    if idx_any == -1:
        resultat = provider.addAttributes([
            QgsField("any_construccio", QVariant.Int)
        ])

        if not resultat:
            raise RuntimeError(
                "No s'ha pogut crear el camp 'any_construccio'."
            )

        layer.updateFields()

        idx_any = layer.fields().indexFromName("any_construccio")

    # Calcul dels anys de construcció
    canvis = {}

    for feature in layer.getFeatures():

        any_construccio = extreure_any(feature["end"])

        if any_construccio is not None and any_construccio < 1500:
            any_construccio = None

        canvis[feature.id()] = {
            idx_any: any_construccio
        }

    if not provider.changeAttributeValues(canvis):
        raise RuntimeError(
            "No s'han pogut actualitzar els anys de construcció."
        )

    return layer


def percentatges_distribucio(distribucio):
    """
    Calcula el percentatge que representa cada període
    respecte el total d'elements de la distribució.

    Parameters
    ----------
    distribucio : dict
        Diccionari amb el nombre d'elements per període.

    Returns
    -------
    dict
        Diccionari amb els percentatges de cada període,
        arrodonits a dos decimals.

    Raises
    ------
    ValueError
        Si la distribució és buida, conté valors negatius
        o el total és zero.
    """
    # Validacions
    if not distribucio:
        raise ValueError(
            "La distribució és buida."
        )

    if any(
        not isinstance(n, (int, float)) or n < 0 or isinstance(n, bool) or n < 0
        for n in distribucio.values()
    ):
        raise ValueError(
            "La distribució ha de contenir valors numèrics no negatius."
        )
    
    total = sum(distribucio.values())

    if total == 0:
        raise ValueError(
            "El total de la distribució és zero."
        )

    return {
        periode: round(nombre / total * 100, 2)
        for periode, nombre in distribucio.items()
    }


def assignar_diferencia_any_a_edificis(edificis_industrial, camp_any, zones, camp_id_zona, mediana_resta_per_zona):
    """
    Assigna a cada edifici industrial la diferència entre el seu propi
    any de construcció i la mediana d'anys de construcció de la resta
    d'usos del barri on es troba.

    Un valor positiu indica que l'edifici és més modern que la mediana
    del seu barri; un valor negatiu, que és més antic.

    Paràmetres
    ----------
    edificis_industrial: QgsVectorLayer
        Capa d'edificis industrials.
    camp_any: str
        Camp amb l'any de construcció de cada edifici.
    zones: QgsVectorLayer
        Capa de polígons de zonificació (barris).
    camp_id_zona: str
        Nom del camp identificador de la zona dins de `zones`.
    mediana_resta_per_zona: dict
        Diccionari { id_zona: mediana_any }, sortida de calcular la
        mediana d'anys de la resta d'usos per zona.

    Retorna
    -------
    QgsVectorLayer
        Còpia dels edificis industrials amb el nou camp
        'diferencia_any_barri'.
    """
    # Validacions
    if edificis_industrial is None or not edificis_industrial.isValid():
        raise ValueError(
            "La capa d'edificis industrials no és vàlida."
        )

    if zones is None or not zones.isValid():
        raise ValueError(
            "La capa de zones no és vàlida."
        )

    if not isinstance(camp_any, str) or not camp_any:
        raise ValueError(
            "El nom del camp d'any no és vàlid."
        )

    if edificis_industrial.fields().indexFromName(camp_any) == -1:
        raise ValueError(
            f"La capa d'edificis no conté el camp obligatori '{camp_any}'."
        )

    if not isinstance(camp_id_zona, str) or not camp_id_zona:
        raise ValueError(
            "El nom del camp identificador de zona no és vàlid."
        )

    if zones.fields().indexFromName(camp_id_zona) == -1:
        raise ValueError(
            f"La capa de zones no conté el camp obligatori '{camp_id_zona}'."
        )

    if not isinstance(mediana_resta_per_zona, dict):
        raise ValueError(
            "Les medianes per zona han de ser un diccionari."
        )

    if edificis_industrial.crs() != zones.crs():
        raise ValueError(
            "Les capes d'edificis i zones tenen SRC diferents."
        )

    # Crear una còpia de la capa
    layer = edificis_industrial.materialize(QgsFeatureRequest())

    if not layer.isValid():
        raise RuntimeError(
            "No s'ha pogut crear una còpia vàlida de la capa d'edificis."
        )
    
    provider = layer.dataProvider()

    resultat = provider.addAttributes([
        QgsField("diferencia_any_barri", QVariant.Double)
    ])
    
    if not resultat:
        raise RuntimeError(
            "No s'ha pogut crear el camp 'diferencia_any_barri'."
        )
    
    layer.updateFields()

    idx_diferencia = layer.fields().indexOf("diferencia_any_barri")

    if idx_diferencia == -1:
        raise RuntimeError(
            "El camp 'diferencia_any_barri' no s'ha incorporat correctament."
        )
    
    index_edificis = QgsSpatialIndex(layer.getFeatures())

    canvis = {}

    for zona in zones.getFeatures():
        id_zona = zona[camp_id_zona]
        mediana_zona = mediana_resta_per_zona.get(id_zona)

        if mediana_zona is None:
            continue

        geometria_zona = zona.geometry()

        if geometria_zona.isNull() or geometria_zona.isEmpty():
            raise ValueError(
                f"La zona amb identificador '{id_zona}' té una geometria buida."
            )
        
        engine = QgsGeometry.createGeometryEngine(geometria_zona.constGet())
        engine.prepareGeometry()

        candidats = index_edificis.intersects(geometria_zona.boundingBox())
        request = QgsFeatureRequest().setFilterFids(candidats)

        for edifici in layer.getFeatures(request):
            any_edifici = edifici[camp_any]
            
            if any_edifici is None:
                continue
            
            geometria_edifici = edifici.geometry()

            if geometria_edifici.isNull() or geometria_edifici.isEmpty():
                continue

            centroide = geometria_edifici.centroid()

            if centroide.isNull() or centroide.isEmpty():
                continue

            if engine.contains(centroide.constGet()):
                canvis[edifici.id()] = {idx_diferencia: any_edifici - mediana_zona}

    if canvis:
        resultat = provider.changeAttributeValues(canvis)
    if not resultat:
        raise RuntimeError(
            "No s'han pogut actualitzar els valors del camp "
            "'diferencia_any_barri'."
        )

    return layer