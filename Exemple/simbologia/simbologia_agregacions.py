"""
"""

from qgis.core import QgsClassificationJenks

import config
import simbologia.simbologies as simbologies

def calcular_breaks_compartits(diccionari_valors, n_classes):
    """
    Calcula els llindars de classificació per a una distribució amb una
    proporció alta de zeros (p. ex. densitat industrial per hexàgon).

    El valor 0 es tracta com una classe pròpia explícita ("sense indústria"),
    i el mètode de Jenks (natural breaks) s'aplica només sobre els valors
    positius per repartir les n_classes - 1 classes restants.

    Paràmetres
    ----------
    diccionari_valors : dict
        Diccionari { id_zona: valor }, típicament el resultat més fi
        (densitat industrial per hexàgon).
    n_classes : int
        Nombre de classes totals de la simbologia (incloent la classe "0").

    Retorna
    -------
    list[float]
        Llista de n_classes + 1 llindars ordenats. El primer interval
        correspon sempre a la classe "0".
    """
    valors_positius = [
        valor 
        for valor in diccionari_valors.values()
        if valor is not None and valor > 0
    ]

    metode = QgsClassificationJenks()
    rangs = metode.classes(valors_positius, n_classes - 1)

    breaks = [0.0, 0.0] + [rang.upperBound() for rang in rangs]

    return breaks


def simbologia_densitat_industrial(capa_zones, breaks, tipus_zona):
    """
    Aplica la simbologia graduada de densitat industrial a una capa de
    zones (districtes, barris o hexàgons), amb els breaks compartits
    definits a config.BREAKS_DENSITAT_INDUSTRIAL.

    La primera classe (0-0) es reetiqueta explícitament com "Sense
    indústria" per distingir-la clarament de les classes amb valors
    positius a la llegenda.

    Paràmetres
    ----------
    capa_zones : QgsVectorLayer
        Capa de zones amb el camp de densitat industrial ja calculat.
    breaks : list[float]
        Llindars de classificació compartits entre totes les escales.
    tipus_zona : str
        Clau de config.SIMBOLOGIA["Densitat_industrial"] ("Districtes",
        "Barris" o "Hexagons").

    Retorna
    -------
    QgsVectorLayer
        Còpia en memòria de la capa amb la simbologia graduada aplicada.
    """
    layer = simbologies.simbologia_graduada_manual(
        layer=capa_zones,
        intervals=breaks,
        **config.SIMBOLOGIA["Densitat_industrial"][tipus_zona]
    )

    # Reetiqueta només la primera classe (0-0) com a "Sense indústria"
    renderer = layer.renderer()
    renderer.updateRangeLabel(0, "Sense indústria")

    layer.setName(f"Densitat industrial {tipus_zona}")

    return layer
