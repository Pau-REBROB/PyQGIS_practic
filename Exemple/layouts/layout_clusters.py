"""COMPOSICIÓ GENERAL"""

import config
import layout_common
import layout_general


def composicio_clusters(capes, capa_extent):
    """
    Funció d'alt nivell per generar la composició del mapa general amb les agrupacions espacials per usos 
    i l'anàlisi estadístic
    """

    cfg_layout_clusters = config.LAYOUT["CLUSTERS"]

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
