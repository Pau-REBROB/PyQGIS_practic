"""
Composició de l'anàlisi dels usos
=================================

Generació de la composició cartogràfica de l'anàlisi dels usos dels edificis.

Organització
------------
- funció principal de composició
"""

import config
import layouts.layout_common as layout_common
import layouts.layout_general as layout_general

def composicio_analisi(capes, capa_extent):
    """
    Genera la composició cartogràfica de l'anàlisi dels usos dels edificis.

    La composició inclou:
        - mapa principal
        - títol
        - llegenda
        - escala gràfica
        - fletxa del nord
        - gràfics de l'anàlisi
        - exportació a PDF

    Paràmetres
    ----------
    capes: list[QgsMapLayer]
        Llista de capes que es representaran al mapa.
    capa_extent: QgsVectorLayer
        Capa utilitzada per definir l'extensió inicial del mapa.

    Retorna
    -------
    None
    """

    cfg_layout = config.LAYOUTS["ANALISI"]
    cfg_estructura = config.LAYOUTS["ESTRUCTURA"]

    layout = layout_common.generar_layout(
        nom_layout="Anàlisi dels usos dels edificis a Barcelona"
    )

    mapa = layout_general.afegir_mapa(
        layout=layout,
        capes=capes,
        capa_extent=capa_extent,
        **cfg_estructura["Mapa"]
    )

    layout_common.afegir_titol(
        layout=layout,
        **cfg_layout["Titol"],
        **cfg_estructura["Titol"]
    )

    layout_common.afegir_llegenda(
        layout=layout,
        mapa=mapa,
        capes=capes,
        **cfg_layout["Llegenda"],
        **cfg_estructura["Llegenda"]
    )

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

    layout_common.afegir_grafic(
        layout=layout,
        **cfg_layout["Grafic_total"]
    )

    layout_common.afegir_grafic(
        layout=layout,
        **cfg_layout["Grafic_percentatge"]
    )

    layout_general.exportar_layout(
        layout=layout,
        **cfg_layout["Exportacio"]
    )
    