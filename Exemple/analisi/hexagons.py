"""
analisi_hexagonal.py

│
├── crear_malla_hexagonal()
│
├── eliminar_hexagons_buits()
│
├── agregar_activitats_hexagons()
│
├── calcular_indicadors_hexagons()
│
└── generar_layout_hexagonal()
"""

from qgis.core import (QgsFeatureRequest)

import processing

def crear_malla_hexagonal(capa_extent, mida_hexagon):
    """
    Crea una malla regular d'hexàgons.

    La funció crea una capa vectorial formada per hexàgons que
    cobreixen totalment l'extensió de la capa de referència.

    Paràmetres
    ----------
    capa_extent: QgsVectorLayer
        Capa vectorial utilitzada per definir l'extensió de la malla.
    mida_hexagon: int
        Amplada de cada hexagon, en unitats del SRC.

    Retorna
    -------
    QgsVectorLayer
        Capa vectorial de la malla hexagonal.
    """

    resultat = processing.run(
        "native:creategrid",
        {
            'TYPE': 4,
            'EXTENT': capa_extent,
            'HSPACING': mida_hexagon,
            'VSPACING': mida_hexagon,
            'HOVERLAY': 0,
            'VOVERLAY': 0,
            'CRS': capa_extent.crs(),
            'OUTPUT': "memory:"
        }
    )

    return resultat["OUTPUT"]


def retallar_malla_hexagonal(malla, capa_extent):
    """
    """

    resultat = processing.run(
        "native:clip",
        {
            'INPUT': malla,
            'OVERLAY': capa_extent,
            'OUTPUT': "memory:"
        }
    )

    return resultat["OUTPUT"]


def filtrar_capa_edificis(layer, expressio):
    """
    Genera una nova capa en memòria amb les entitats que compleixen una expressió.

    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa vectorial sobre la qual s'aplica el filtratge.
    expressio: str
        Expressió de filtratge escrita amb la sintaxi d'expressions de QGIS.

    Retorna
    -------
    QgsVectorLayer
        Nova capa en memòria que conté únicament les entitats seleccionades.
    """
    
    request = QgsFeatureRequest().setFilterExpression(expressio)

    return layer.materialize(request)


def agregar_usos_a_hexagons(edificis, malla, camp, expressio=None):
    """
    """

    if expressio: 
        edificis = filtrar_capa_edificis(
            layer=edificis,
            expressio=expressio
        )

    resultat = processing.run(
        "native:joinattributesbylocation",
        {
            'INPUT': malla,
            'JOIN': edificis,
            'JOIN_FIELDS': camp,
            'PREDICATE': 0, # Intersecció
            'METHOD': 1, # 1 a 1
            'DISCARD_NONMATCHING': False,
            'OUTPUT': "memory:"
        }
    )

    return resultat["OUTPUT"]

