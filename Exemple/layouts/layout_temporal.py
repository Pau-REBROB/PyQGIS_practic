"""
"""

import layouts.layout_common as layout_common

import config

def composicio_antiguitat_parc_edificis(capes, capa_extent, capa_terme, capes_llegenda):
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
        capes=[capa_terme] + list(capes.values()),
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
        capes=[capes_llegenda["Industrial"]],
        **cfg_layout["Llegenda_industria"],
        **cfg_estructura["Llegenda_industria"]
    )

    layout_common.afegir_llegenda(
        layout=layout,
        mapa=mapa,
        capes=[capes_llegenda["No_industrial"]],
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


def composicio_antiguitat_relativa(capes, capa_extent):
    """
    """
    cfg_layout = config.LAYOUTS["TEMPORAL"]["RELATIVA"]["Barris"]
    cfg_estructura = config.LAYOUTS["ESTRUCTURA_TEMPORAL"]["RELATIVA"]["Barris"]

    # ------------------------------------------------------------------
    # LAYOUT
    # ------------------------------------------------------------------

    layout = layout_common.generar_layout(
        nom_layout="Antiguitat parc edificis Barcelona",
        orientacio="horitzontal")

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
        capes=list(capes.values()),
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
    # EXPORTACIÓ
    # ------------------------------------------------------------------

    layout_common.exportar_layout(
        layout=layout,
        **cfg_layout["Exportacio"]
    )


def composicio_antiguitat_relativa_clusters(capes, capa_barris, extensions, capa_general_barris, capa_terme):
    """
    """
    cfg_layout = config.LAYOUTS["TEMPORAL"]["RELATIVA"]["Clusters"]
    cfg_estructura = config.LAYOUTS["ESTRUCTURA_TEMPORAL"]["RELATIVA"]["Clusters"]

    # ------------------------------------------------------------------
    # LAYOUT
    # ------------------------------------------------------------------

    layout = layout_common.generar_layout(
        nom_layout="Antiguitat clústers industrials Barcelona",
        orientacio="horitzontal")

    # ------------------------------------------------------------------
    # MAPES
    # ------------------------------------------------------------------

    mapa_zonaFranca = layout_common.afegir_mapa(
        layout=layout,
        capes=[capa_barris] + list(capes.values()),
        capa_extent=extensions["Zona Franca"],
        **cfg_estructura["Mapa_zonaFranca"]
    )

    mapa_santMarti = layout_common.afegir_mapa(
        layout=layout,
        capes=[capa_barris] + list(capes.values()),
        capa_extent=extensions["Sant Martí"],
        **cfg_estructura["Mapa_santMarti"]
    )

    mapa_santAndreu = layout_common.afegir_mapa(
        layout=layout,
        capes=[capa_barris] + list(capes.values()),
        capa_extent=extensions["Sant Andreu"],
        **cfg_estructura["Mapa_santAndreu"]
    )

    mapa_general = layout_common.afegir_mapa(
        layout=layout,
        capes=list(capa_general_barris.values()),
        capa_extent=capa_terme,
        **cfg_estructura["Mapa_general"]
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
        mapa=mapa_zonaFranca,
        capes=list(capes.values()),
        **cfg_layout["Llegenda"],
        **cfg_estructura["Llegenda"]
    )

    # # ------------------------------------------------------------------
    # # ESCALA I NORD
    # # ------------------------------------------------------------------

    # layout_common.afegir_escala(
    #     layout=layout,
    #     mapa=mapa_,
    #     **cfg_layout["Escala"],
    #     **cfg_estructura["Escala"]
    # )

    # layout_common.afegir_nord(
    #     layout=layout,
    #     mapa=mapa,
    #     **cfg_layout["Nord"],
    #     **cfg_estructura["Nord"]
    # )

    # ------------------------------------------------------------------
    # EXPORTACIÓ
    # ------------------------------------------------------------------

    layout_common.exportar_layout(
        layout=layout,
        **cfg_layout["Exportacio"]
    )