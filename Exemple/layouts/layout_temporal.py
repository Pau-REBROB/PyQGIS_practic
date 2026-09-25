"""
"""

import layouts.layout_common as layout_common

import config

def composicio_antiguitat_parc_edificis(capes, capa_extent, capes_llegenda):
    """
    """
    cfg_layout = config.LAYOUTS["TEMPORAL"]["GENERAL"]
    cfg_estructura = config.LAYOUTS["ESTRUCTURA_TEMPORAL"]["GENERAL"]

    # ------------------------------------------------------------------
    # LAYOUT
    # ------------------------------------------------------------------

    layout = layout_common.generar_layout(
        nom_layout="Antiguitat parc edificis Barcelona",
        orientacio="vertical")

    # ------------------------------------------------------------------
    # MAPA
    # ------------------------------------------------------------------

    mapa = layout_common.afegir_mapa(
        layout=layout,
        capes=list(capes.values()),
        capa_extent=capa_extent,
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
        capes=list(capes_llegenda.values()),
        **cfg_layout["Llegenda_industria"],
        **cfg_estructura["Llegenda_industria"]
    )

    layout_common.afegir_llegenda(
        layout=layout,
        mapa=mapa,
        capes=list(capes_llegenda.values()),
        **cfg_layout["Llegenda_no_industria"],
        **cfg_estructura["Llegenda_no_industria"]
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
    # EXPORTACIÓ
    # ------------------------------------------------------------------

    layout_common.exportar_layout(
        layout=layout,
        **cfg_layout["Exportacio"]
    )