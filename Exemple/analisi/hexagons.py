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

#from qgis.core import ()

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
