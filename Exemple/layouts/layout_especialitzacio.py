"""
Composició de les especialitzacions funcionals dels edificis
============================================================

####TODO
Generació de la composició cartogràfica del mapa d'agrupacions espacials.

La composició inclou:

- mapa principal
- títol
- llegenda
- escala gràfica
- fletxa del nord
- gràfics estadístics
- exportació a PDF

Organització
------------
- afegir la composició
- exportar la composició
"""

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

import config
import layouts.layout_common as layout_common

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


def afegir_llegenda(layout, mapa, capes, titol, font, font_size, font_color, position, backg_color):
    """
    Afegeix una llegenda a una composició.

    La funció crea una llegenda vinculada al mapa indicat,
    elimina les capes que no s'han de representar, configura
    el format del text, i aplica el fons corresponent.

    Paràmetres
    ----------
    layout: QgsPrintLayout
        Composició on s'insereix la llegenda.
    mapa: QgsLayoutItemMap
        Element mapa al qual queda vinculada la llegenda.
    capes: list[QgsMapLayer]
        Llistat de capes que ha de mostrar la llegenda.
    titol: str
        Títol de la llegenda.
    font: str
        Nom de la família tipogràfica.
    font_size: float
        Mida del text, en punts.
    font_color: tuple[int,int,int,int]
        Color del text, en format (RGBA).
    position: tuple[int,int]
        Coordenada X i Y de la imatge - cantonada superior esquerra - en mil·límetres.
    backg_color: tuple[int,int,int,int]
        Color del fons, en format (RGBA).

    Retorna
    -------
    QgsLayoutItemLegend
        Element llegenda.
    """

    # Creació de la llegenda
    legend = QgsLayoutItemLegend(layout)
    layout.addLayoutItem(legend)

    # Vinculació amb el mapa
    legend.setLinkedMap(mapa)
    
    # Construcció manual del contingut
    legend.setAutoUpdateModel(False)
    
    root = legend.model().rootGroup()

    for layer_node in root.findLayers():
        layer_node.setName("")     

    ids_capes = {capa.id() for capa in capes}

    for node in list(root.findLayers()):
        if node.layerId() not in ids_capes:
            root.removeLayer(node.layer())
    
    # Títol
    legend.setTitle(titol)

    # Posició i mida
    legend.attemptMove(QgsLayoutPoint(*position, QgsUnitTypes.LayoutMillimeters))
    legend.adjustBoxSize()

    # Definició del format de text - tot igual
    text_format = QgsTextFormat()
    text_format.setFont(QFont(font))
    text_format.setSize(font_size)
    text_format.setSizeUnit(QgsUnitTypes.RenderPoints)
    text_format.setColor(QColor(*font_color))
    # Títol
    legend.rstyle(QgsLegendStyle.Title).setTextFormat(text_format)
    # Grups
    legend.rstyle(QgsLegendStyle.Group).setTextFormat(text_format)
    # Subgrups
    legend.rstyle(QgsLegendStyle.Subgroup).setTextFormat(text_format)
    # Elements individuals
    legend.rstyle(QgsLegendStyle.SymbolLabel).setTextFormat(text_format)

    # Definició del fons i el marc
    legend.setBackgroundEnabled(True)
    legend.setBackgroundColor(QColor(*backg_color))
    legend.setFrameEnabled(False)

    return legend


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


def composicio_especialitzacio(capes, capa_extent):
    """
    Genera la composició cartogràfica d'especialització del projecte.

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

    cfg_layout = config.LAYOUTS["ESPECIALITZACIO"]
    cfg_estructura = config.LAYOUTS["ESTRUCTURA_ESPECIALITZACIO"]

    layout = layout_common.generar_layout(nom_layout="Especialitzacio funcional per districtes")

    layout_common.afegir_fons(
            layout=layout,
            **cfg_layout["Fons"],
            **cfg_estructura["Fons"]
        )
    
    mapa_us = afegir_mapa(
        layout=layout,
        capes=[capes["us_predominant"]],
        capa_extent=capa_extent,
        **cfg_estructura["Mapa_us"]
    )

    mapa_dominancia = afegir_mapa(
        layout=layout,
        capes=[capes["dominancia"]],
        capa_extent=capa_extent,
        **cfg_estructura["Mapa_dominancia"]
    )

    mapa_shannon = afegir_mapa(
        layout=layout,
        capes=[capes["index_shannon"]],
        capa_extent=capa_extent,
        **cfg_estructura["Mapa_shannon"]
    )

    layout_common.afegir_titol(
        layout=layout,
        **cfg_layout["Titol"],
        **cfg_estructura["Titol"]
    )

    layout_common.afegir_titol(
        layout=layout,
        **cfg_layout["Titol_us"],
        **cfg_estructura["Titol_us"]
    )

    layout_common.afegir_subtitol(
        layout=layout,
        **cfg_layout["Subtitol_us"],
        **cfg_estructura["Subtitol_us"]
    )

    layout_common.afegir_titol(
        layout=layout,
        **cfg_layout["Titol_dominancia"],
        **cfg_estructura["Titol_dominancia"]
    )

    layout_common.afegir_subtitol(
        layout=layout,
        **cfg_layout["Subtitol_dominancia"],
        **cfg_estructura["Subtitol_dominancia"]
    )

    layout_common.afegir_titol(
        layout=layout,
        **cfg_layout["Titol_shannon"],
        **cfg_estructura["Titol_shannon"]
    )

    layout_common.afegir_subtitol(
        layout=layout,
        **cfg_layout["Subtitol_shannon"],
        **cfg_estructura["Subtitol_shannon"]
    )

    afegir_llegenda(
        layout=layout,
        mapa=mapa_us,
        capes=[capes["us_predominant"]],
        **cfg_layout["Llegenda"],
        **cfg_estructura["Llegenda_us"]
    )

    afegir_llegenda(
        layout=layout,
        mapa=mapa_dominancia,
        capes=[capes["dominancia"]],
        **cfg_layout["Llegenda"],
        **cfg_estructura["Llegenda_dominancia"]
    )

    afegir_llegenda(
        layout=layout,
        mapa=mapa_shannon,
        capes=[capes["index_shannon"]],
        **cfg_layout["Llegenda"],
        **cfg_estructura["Llegenda_shannon"]
    )

    exportar_layout(
        layout=layout,
        **cfg_layout["Exportacio"]
    )
