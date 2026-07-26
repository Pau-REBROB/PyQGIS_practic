from qgis.core import (
    QgsLayoutExporter,
    QgsLayoutItemLegend,
    QgsLayoutItemMap,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsLegendStyle,
    QgsTextFormat,
    QgsUnitTypes,
)

from qgis.PyQt.QtGui import (
    QFont,
    QColor
)

import os

import layouts.layout_common as layout_common
import config

def afegir_mapa(layout, capes, capa_extent, factor_escala, size, position):
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
    factor_escala: float
        Factor escala per apropar o allunyar el mapa.
    size: tuple[int,int]
        Amplada i alçada de la imatge, en mil·límetres.
    position: tuple[int,int]
        Coordenada X i Y de la imatge - cantonada superior esquerra - en mil·límetres.

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

    layout_map.attemptResize(QgsLayoutSize(*size, QgsUnitTypes.LayoutMillimeters))
    layout_map.attemptMove(QgsLayoutPoint(*position, QgsUnitTypes.LayoutMillimeters))

    #layout_map.setMapRotation(45)

    extent = capa_extent.extent()
    # Apropa la vista abans d'aplicar els desplaçaments manuals
    extent.scale(factor_escala)
    # Ajust manual del centre del mapa
    # per compensar l'espai ocupat per la llegenda
    # i aconseguir una millor composició visual 
    extent.setXMinimum(extent.xMinimum() + 500)
    extent.setXMaximum(extent.xMaximum() + 500)
    extent.setYMinimum(extent.yMinimum() + 250)
    extent.setYMaximum(extent.yMaximum() + 250)
    layout_map.zoomToExtent(extent)
    
    return layout_map


def afegir_llegenda_bivariant(layout, cell, gap, position, colors):
    """
    """

    matriu = [
        ["Baixa_Alta",   "Mitjana_Alta",   "Alta_Alta"],
        ["Baixa_Mitjana","Mitjana_Mitjana","Alta_Mitjana"],
        ["Baixa_Baixa",  "Mitjana_Baixa",  "Alta_Baixa"]
    ]

    x0, y0 = position

    for fila in range(3):
        for columna in range(3):

            classe = matriu[fila][columna]

            layout_common.afegir_fons(
                layout=layout,
                size=(cell,cell),
                position=(x0 + columna*(cell+gap), y0 + fila*(cell+gap)),
                color=colors[classe]
            )


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


def composicio_bivariant_barris(capes, capa_extent):
    """
    Genera la composició cartogràfica d'anàlisi bivariant del projecte.

    La funció coordina totes les operacions necessàries per crear el
    layout:
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

    cfg_layout = config.LAYOUTS["BIVARIANT"]
    cfg_estructura = config.LAYOUTS["ESTRUCTURA_BIVARIANT"]

    layout = layout_common.generar_layout(nom_layout="Anàlisi bivariant per barris")

    layout_common.afegir_fons(
            layout=layout,
            **cfg_layout["Fons"],
            **cfg_estructura["Fons"]
        )
    
    mapa = afegir_mapa(
        layout=layout,
        capes=capes,
        capa_extent=capa_extent,
        **cfg_estructura["Mapa"]
    )

    layout_common.afegir_titol(
        layout=layout,
        **cfg_layout["Titol"],
        **cfg_estructura["Titol"]
    )

    afegir_llegenda_bivariant(
        layout=layout,
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

    exportar_layout(
        layout=layout,
        **cfg_layout["Exportacio"]
    )
