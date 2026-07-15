"""
Layouts
=======

Funcions comunes per a la construcció de composicions d'impressió.
"""

from qgis.core import (
    QgsLayoutExporter,
    QgsLayoutItemMap,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsUnitTypes,
)

import os

import config
import layouts.layout_common as layout_common

def afegir_mapa(layout, capes, capa_extent):
    """
    Afegeix l'element mapa principal a una composició.

    La funció crea un element `QgsLayoutItemMap`, hi assocïa les capes
    indicades, defineix la seva extensió, i n'estableix la seva
    posició, mida i rotació dins de la composició.

    Paràmetres
    ----------
    layout: QgsPrintLayout
        Composició sobre la qual s'afegeix el mapa.
    capes: list[QgsMapLayer]
        Capes que es mostraran al mapa, en ordre de representació.
    capa_extent: QgsVectorLayer
        Capa utilitzada per a definir l'extensió inicial del mapa.

    Retorna
    -------
    QgsLayoutItemMap
        Element mapa.
    """

    layout_map = QgsLayoutItemMap(layout)
    
    layout.addLayoutItem(layout_map)

    layout_map.setLayers(capes)

    # Mantenir el conjunt de capes fix perquè el layout no canvïi
    layout_map.setKeepLayerSet(True)

    layout_map.attemptResize(QgsLayoutSize(270, 190, QgsUnitTypes.LayoutMillimeters))
    layout_map.attemptMove(QgsLayoutPoint(10, 10, QgsUnitTypes.LayoutMillimeters))

    layout_map.setMapRotation(45)

    extent = capa_extent.extent()
    # Apropa la vista abans d'aplicar els desplaçaments manuals.
    extent.scale(0.5)
    # Ajust manual del centre del mapa
    # per compensar l'espai ocupat per la llegenda
    # i aconseguir una millor composició visual 
    extent.setXMinimum(extent.xMinimum() + 500)
    extent.setXMaximum(extent.xMaximum() + 500)
    extent.setYMinimum(extent.yMinimum() + 250)
    extent.setYMaximum(extent.yMaximum() + 250)
    layout_map.zoomToExtent(extent)
    
    return layout_map


def exportar_layout(layout, output_path, dpi):
    """
    Exporta una composició QGIS en format PDF.

    Si ja existeix un fitxer amb el mateix nom, s'elimina abans
    de generar la nova exportació.

    Paràmetres
    ----------
    layout: QgsPrintLayout
        Composició que es vol exportar.
    output_path: str
        Ruta completa de l'arxiu PDF de sortida.
    dpi: int
        Resolució de l'exportació.

    Retorna
    -------
    None
    """
   
    # Si ja existeix una composició amb el mateix nom, s'elimina
    if os.path.exists(output_path):
        os.remove(output_path)  

    exporter = QgsLayoutExporter(layout)
    
    # Configurar els paràmetres d'exportació
    pdf_settings = QgsLayoutExporter.PdfExportSettings()
    pdf_settings.dpi = dpi
    pdf_settings.forceVectorOutput = True
    pdf_settings.rasterizeWholeImage = False
    
    resultat = exporter.exportToPdf(output_path, pdf_settings)

    if resultat != QgsLayoutExporter.Success:
        raise RuntimeError(f"No s'ha pogut exportar el layout a '{output_path}'")


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

    cfg_layout_general = config.LAYOUTS["GENERAL"]

    layout = layout_common.generar_layout(nom_layout="Ús dels edificis a Barcelona")

    mapa = afegir_mapa(
        layout=layout,
        capes=capes,
        capa_extent=capa_extent
    )

    layout_common.afegir_titol(
        layout=layout,
        **cfg_layout_general["Titol"]
    )

    layout_common.afegir_llegenda(
        layout=layout,
        mapa=mapa,
        capes=capes,
        **cfg_layout_general["Llegenda"]
    )

    layout_common.afegir_escala(
        layout=layout,
        mapa=mapa,
        **cfg_layout_general["Escala"]
    )

    layout_common.afegir_nord(
        layout=layout,
        mapa=mapa,
        **cfg_layout_general["Nord"]
    )

    exportar_layout(
        layout=layout,
        **cfg_layout_general["Exportacio"]
    )
