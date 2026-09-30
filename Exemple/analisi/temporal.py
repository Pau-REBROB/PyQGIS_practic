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
    except:
        return None


def extreure_any_edificis(edificis):
    """
    Extreu l'any de la capa vectorials d'edificis
    per al seu anàlisi.
    """

    anys = [
        extreure_any(feat["end"])
        for feat in edificis.getFeatures()
        if feat["end"] is not None
    ]

    # Filtrar anys nuls
    anys = [
        a 
        for a in anys
        if a is not None
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
    Afegeix el camp any de construcció a la capa
    d'edificis.
    """

    layer = edificis.materialize(QgsFeatureRequest())

    provider = layer.dataProvider()

    provider.addAttributes([
        QgsField("any_construccio", QVariant.Int)
    ])

    layer.updateFields()

    idx_any = layer.fields().indexOf("any_construccio")

    layer.startEditing()

    canvis = {}

    for feature in layer.getFeatures():

        any_construccio = extreure_any(feature["end"])

        if any_construccio is not None and any_construccio < 1500:
            any_construccio = None

        canvis[feature.id()] = {
            idx_any: any_construccio
        }

    provider.changeAttributeValues(canvis)

    layer.commitChanges()

    return layer


def percentatges_distribucio(distribucio):
    """
    """
    total = sum(distribucio.values())

    return {
        periode: round(nombre / total * 100)
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
    layer = edificis_industrial.materialize(QgsFeatureRequest())

    provider = layer.dataProvider()
    provider.addAttributes([QgsField("diferencia_any_barri", QVariant.Double)])
    layer.updateFields()

    idx_diferencia = layer.fields().indexOf("diferencia_any_barri")
    index_edificis = QgsSpatialIndex(layer.getFeatures())

    canvis = {}

    for zona in zones.getFeatures():
        id_zona = zona[camp_id_zona]
        mediana_zona = mediana_resta_per_zona.get(id_zona)

        if mediana_zona is None:
            continue

        geometria_zona = zona.geometry()
        engine = QgsGeometry.createGeometryEngine(geometria_zona.constGet())
        engine.prepareGeometry()

        candidats = index_edificis.intersects(geometria_zona.boundingBox())
        request = QgsFeatureRequest().setFilterFids(candidats)

        for edifici in layer.getFeatures(request):
            any_edifici = edifici[camp_any]
            if any_edifici is None:
                continue
            if engine.intersects(edifici.geometry().centroid().constGet()):
                canvis[edifici.id()] = {idx_diferencia: any_edifici - mediana_zona}

    provider.changeAttributeValues(canvis)

    return layer