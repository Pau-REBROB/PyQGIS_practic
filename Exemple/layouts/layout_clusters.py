"""
Composició de les agrupacions espacials
=======================================

Generació de la composició cartogràfica del mapa d'agrupacions espacials.

La composició inclou:

- mapa principal
- títol
- llegenda
- escala gràfica
- fletxa del nord
- gràfics estadístics
- exportació a PDF

Organització
------------
- afegir la composició
- exportar la composició
"""

import config
import layouts.layout_common as layout_common
import layouts.layout_general as layout_general

def composicio_clusters(capes, capa_extent):
    """
    Genera la composició del mapa d'agrupacions espacials.

    La composició inclou:
        - mapa principal
        - títol
        - llegenda
        - escala numèrica
        - fletxa del nord
        - gràfic del nombre d'agrupacions per ús
        - gràfic de la mida mitjana de les agrupacions

    Paràmetres
    ----------
    capes: list[QgsMapLayer]
        Llista ordenada de capes que es mostraran al mapa.
    capa_extent: QgsVectorLayer
        Capa utilitzada per a definir l'extensió inicial del mapa.

    Retorna
    -------
    None
    """

    cfg_layout_clusters = config.LAYOUTS["CLUSTERS"]

    layout = layout_common.generar_layout(
        nom_layout="Agrupacions espacials dels usos dels edificis a Barcelona"
    )

    mapa = layout_general.afegir_mapa(
        layout=layout,
        capes=capes,
        capa_extent=capa_extent
    )

    layout_common.afegir_titol(
        layout=layout,
        **cfg_layout_clusters["Titol"]
    )

    layout_common.afegir_llegenda(
        layout=layout,
        mapa=mapa,
        capes=capes,
        **cfg_layout_clusters["Llegenda"]
    )

    layout_common.afegir_escala(
        layout=layout,
        mapa=mapa,
        **cfg_layout_clusters["Escala"]
    )

    layout_common.afegir_nord(
        layout=layout,
        mapa=mapa,
        **cfg_layout_clusters["Nord"]
    )

    layout_common.afegir_grafic(
        layout=layout,
        **cfg_layout_clusters["Grafic_clusters"]
    )

    layout_common.afegir_grafic(
        layout=layout,
        **cfg_layout_clusters["Grafic_mida"]
    )

    layout_general.exportar_layout(
        layout=layout,
        **cfg_layout_clusters["Exportacio"]
    )
