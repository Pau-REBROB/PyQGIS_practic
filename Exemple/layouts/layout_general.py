"""
Composició general
==================

Funcions per generar la composició principal del projecte.

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

import config
import layouts.layout_common as layout_common

def composicio_general(capes, capa_extent):
    """
    Genera la composició cartogràfica general del projecte.

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

    cfg_layout = config.LAYOUTS["GENERAL"]
    cfg_estructura = config.LAYOUTS["ESTRUCTURA"]

    layout = layout_common.generar_layout(nom_layout="Ús dels edificis a Barcelona")

    mapa = layout_common.afegir_mapa(
        layout=layout,
        capes=capes,
        capa_extent=capa_extent,
        **cfg_estructura["Mapa"]
    )

    layout_common.afegir_capçalera(
        layout=layout,
        **cfg_layout["Capçalera"],
        **cfg_estructura["Capçalera"],
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

    layout_common.exportar_layout(
        layout=layout,
        **cfg_layout["Exportacio"]
    )
