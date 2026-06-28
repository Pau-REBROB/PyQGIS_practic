"""COMPOSICIÓ GENERAL"""

import layout_common
import layout_atles

def crear_composicio_analisi():
    """
    Funció d'alt nivell per a crear la composició completa d'anàlisi
    """

    # Crida de totes les funcions pròpies creades

    layout = layout_common.generar_layout(nom_layout="Composició d'anàlisi")

    layout_atles.afegir_mapa(layout=layout)

    layout_atles.afegir_mapa_localitzador()

    layout_common.afegir_titol()

    layout_common.afegir_llegenda()

    layout_common.afegir_escala()

    layout_common.afegir_nord()

    layout_common.afegir_grafic()