"""
"""

import layouts.layout_common as layout_common
import config

def composicio_maup_densitat_industrial(capes, capa_terme, capa_extent):
    """
    """

    cfg_layout = config.LAYOUTS["MAUP"]
    cfg_estructura = config.LAYOUTS["ESTRUCTURA_MAUP"]

    # ------------------------------------------------------------------
    # LAYOUT
    # ------------------------------------------------------------------

    layout = layout_common.generar_layout(
        nom_layout="Densitat industrial de Barcelona",
        orientacio="horitzontal"
    )

    # ------------------------------------------------------------------
    # MAPES
    # ------------------------------------------------------------------

    mapa_hexagons = layout_common.afegir_mapa(
        layout=layout,
        capes=[capa_terme, capes["Hexagons"]],
        capa_extent=capa_extent,
        **cfg_estructura["Mapa_hexagons"]
    )
    
    mapa_barris = layout_common.afegir_mapa(
        layout=layout,
        capes=[capa_terme, capes["Barris"]],
        capa_extent=capa_extent,
        **cfg_estructura["Mapa_barris"]
    )

    mapa_districtes = layout_common.afegir_mapa(
        layout=layout,
        capes=[capa_terme, capes["Districtes"]],
        capa_extent=capa_extent,
        **cfg_estructura["Mapa_districtes"]
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
        **cfg_layout["Subtitol_1"],
        **cfg_estructura["Subtitol_1"]
    )
    
    layout_common.afegir_subtitol(
        layout=layout,
        **cfg_layout["Subtitol_2"],
        **cfg_estructura["Subtitol_2"]
    )

    # ------------------------------------------------------------------
    # LLEGENDA
    # ------------------------------------------------------------------

    layout_common.afegir_llegenda(
        layout=layout,
        mapa=mapa_hexagons,
        capes=[capes["Hexagons"]],
        **cfg_layout["Llegenda"],
        **cfg_estructura["Llegenda"]
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
