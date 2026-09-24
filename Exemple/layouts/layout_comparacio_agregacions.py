"""
"""

import layouts.layout_common as layout_common
import config

def composicio_agregacio_comparacio_unitat(capes, capa_terme, capa_extent):
    """
    """

    cfg_layout = config.LAYOUTS["AGREGACIO_COMPARACIO"]
    cfg_estructura = config.LAYOUTS["ESTRUCTURA_AGREGACIO_COMPARACIO"]

    # ------------------------------------------------------------------
    # LAYOUT
    # ------------------------------------------------------------------

    layout = layout_common.generar_layout(
        nom_layout="Comparació agregacio edificis_superficie",
        orientacio="horitzontal"
    )

    # ------------------------------------------------------------------
    # MAPES
    # ------------------------------------------------------------------

    mapa_edificis = layout_common.afegir_mapa(
        layout=layout,
        capes=[capa_terme, capes["Edificis"]],
        capa_extent=capa_extent,
        **cfg_estructura["Mapa_edificis"]
    )
    
    mapa_superficie = layout_common.afegir_mapa(
        layout=layout,
        capes=[capa_terme, capes["Superficie"]],
        capa_extent=capa_extent,
        **cfg_estructura["Mapa_superficie"]
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
    
    # layout_common.afegir_subtitol(
    #     layout=layout,
    #     **cfg_layout["Subtitol_2"],
    #     **cfg_estructura["Subtitol_2"]
    # )

    # ------------------------------------------------------------------
    # LLEGENDA
    # ------------------------------------------------------------------

    layout_common.afegir_llegenda(
        layout=layout,
        mapa=mapa_edificis,
        capes=[capes["Edificis"]],
        **cfg_layout["Llegenda_edificis"],
        **cfg_estructura["Llegenda_edificis"]
    )

    layout_common.afegir_llegenda(
        layout=layout,
        mapa=mapa_superficie,
        capes=[capes["Superficie"]],
        **cfg_layout["Llegenda_superficie"],
        **cfg_estructura["Llegenda_superficie"]
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
