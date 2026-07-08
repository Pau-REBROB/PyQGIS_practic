"""COMPOSICIÓ GENERAL"""

import config
import layouts.layout_common as layout_common
import layouts.layout_general as layout_general


def composicio_analisi(capes, capa_extent):
    """
    Funció d'alt nivell per generar la composició del mapa general amb l'anàlisi dels diferents usos
    """

    cfg_layout_analisi = config.LAYOUTS["ANALISI"]

    layout = layout_common.generar_layout(
        nom_layout="Anàlisi dels usos dels edificis a Barcelona"
    )

    mapa = layout_general.afegir_mapa(
        layout=layout,
        capes=capes,
        capa_extent=capa_extent
    )

    layout_common.afegir_titol(
        layout=layout,
        **cfg_layout_analisi["Titol"]
    )

    layout_common.afegir_llegenda(
        layout=layout,
        mapa=mapa,
        capes=capes,
        **cfg_layout_analisi["Llegenda"]
    )

    layout_common.afegir_escala(
        layout=layout,
        mapa=mapa,
        **cfg_layout_analisi["Escala"]
    )

    layout_common.afegir_nord(
        layout=layout,
        mapa=mapa,
        **cfg_layout_analisi["Nord"]
    )

    layout_common.afegir_grafic(
        layout=layout,
        **cfg_layout_analisi["Grafic_total"]
    )

    layout_common.afegir_grafic(
        layout=layout,
        **cfg_layout_analisi["Grafic_percentatge"]
    )

    layout_general.exportar_layout(
        layout=layout,
        **cfg_layout_analisi["Exportacio"]
    )
    