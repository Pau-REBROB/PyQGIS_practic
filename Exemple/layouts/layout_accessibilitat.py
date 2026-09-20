"""
Composició accessibilitat
=========================

Funcions per generar la composició d'anàlisi
d'accessibilitat del projecte.

La composició inclou:

- mapa principal
- títol
- llegenda
- escala gràfica
- fletxa del nord
- exportació a PDF

Organització
------------

- afegir_mapa()
- exportar_layout()
- composicio_general()
"""

from qgis.core import (
    QgsLayoutExporter,
    QgsLayoutItemMap,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsRectangle,
    QgsUnitTypes,
)
from qgis.PyQt.QtGui import QColor

import os

import config
import layouts.layout_common as layout_common

def composicio_accessibilitat(capes, capa_extent):
    """
    Genera la composició cartogràfica d'accessibilitat als nuclis
    comercials.

    La funció coordina totes les operacions necessàries per crear el
    layout principal del projecte:
        - crea la composició,
        - afegeix el mapa principal,
        - incorpora el títol,
        - incorpora la llegenda,
        - incorpora l'escala gràfica,
        - incorpora la fletxa del nord,
        - i exporta el resultat a PDF.
    
    Paràmetres
    ----------
    capes: list[QgsMapLayer]
        Llista ordenada de capes que es mostraran a la composició.
    capa_extent: QgsVectorLayer
        Capa utilitzada per a calcular l'extensió inicial del mapa.

    Retorna
    -------
    None
        La composició s'exporta directament en local.
    """
    cfg_layout = config.LAYOUTS["ACCESSIBILITAT"]
    cfg_estructura = config.LAYOUTS["ESTRUCTURA_ACCESS"]

    layout = layout_common.generar_layout(nom_layout="Accessibilitat industrial Barcelona")

    # ------------------------------------------------------------------
    # MAPA
    # ------------------------------------------------------------------

    mapa = layout_common.afegir_mapa(
        layout=layout,
        capes=capes,
        capa_extent=capa_extent,
        **cfg_layout["Mapa"],
        **cfg_estructura["Mapa"]
    )

    # ------------------------------------------------------------------
    # TÍTOLS
    # ------------------------------------------------------------------

    layout_common.afegir_titol(
        layout=layout,
        **cfg_layout["Titol"],
        **cfg_estructura["Titol"]
    )

    layout_common.afegir_subtitol(
        layout=layout,
        **cfg_layout["Subtitol"],
        **cfg_estructura["Subtitol"]
    )

    # ------------------------------------------------------------------
    # LLEGENDA
    # ------------------------------------------------------------------

    layout_common.afegir_llegenda(
        layout=layout,
        mapa=mapa,
        capes=[capes[1]],
        **cfg_layout["Llegenda"],
        **cfg_estructura["Llegenda"]
    )

    # ------------------------------------------------------------------
    # ESCALA I NORD
    # ------------------------------------------------------------------
    
    layout_common.afegir_escala(
        layout=layout,
        mapa=mapa,
        **cfg_layout["Escala"],
        **cfg_estructura["Escala"]
    )

    layout_common.afegir_nord(
        layout=layout,
        mapa=mapa,
        **cfg_layout["Nord"],
        **cfg_estructura["Nord"]
    )

    # ------------------------------------------------------------------
    # PEU DE PÀGINA
    # ------------------------------------------------------------------

    layout_common.afegir_text(
        layout=layout,
        **cfg_layout["Peu"],
        **cfg_estructura["Peu"]
    )

    # ------------------------------------------------------------------
    # EXPORTACIÓ
    # ------------------------------------------------------------------
    
    layout_common.exportar_layout(
        layout=layout,
        **cfg_layout["Exportacio"]
    )
