"""COMPOSICIONS - LAYOUTS"""

# Composició en atles

from qgis.core import (
    QgsProject,
    QgsPrintLayout,
    QgsLayoutItemMap,
    QgsLayoutSize,
    QgsLayoutMeasurement,
    QgsLayoutPoint,
    QgsUnitTypes,
    QgsPointXY,
    QgsLayoutItemLabel,
    QgsTextFormat,
    QgsLayoutItemLegend,
    QgsLayerTree,
    QgsLegendStyle,
    QgsLayoutItemScaleBar,
    QgsBasicNumericFormat,
    QgsLayoutItemPicture,
    QgsLayoutExporter)

from qgis.PyQt.QtGui import (
    QFont,
    QColor
)

from qgis.PyQt.QtCore import Qt

import os


def generar_layout(nom_layout):
    """
    Funció que 
        Inicialitza la composició
        Estableix uns paràmetres incials per defecte
        Estableix un nom 
        Desa la composició al gestor de composicions 
    """
    
    # Creació del gestor de composicions
    manager = QgsProject.instance().layoutManager()

    # Comprovació d'existència prèvia del layout
    for layout in manager.printLayouts():
        if layout.name() == nom_layout:
            manager.removeLayout(layout)
    
    # Creació del layout
    layout = QgsPrintLayout(QgsProject.instance())

    # Inicialització
    layout.initializeDefaults()
    
    # Assignació d'un nom
    layout.setName(nom_layout)

    # Addició del layout al gestor
    manager.addLayout(layout)

    return layout


def afegir_mapa(layout, capes, capa_extent):
    """
    Funció que 
        Afegeix un element mapa a la composició
        Estableix les capes que es mostraran
        Estableix una extensió
        Estableix unes mides predefinides segons la composició general
    """

    # Creació del mapa
    layout_map = QgsLayoutItemMap(layout)
    
    # Addició del mapa a la composició
    layout.addLayoutItem(layout_map)

    # Addició de les capes
    layout_map.setLayers(capes)
    layout_map.setKeepLayerSet(True)

    # Definició de posició i mida
    layout_map.attemptResize(QgsLayoutSize(270, 190, QgsUnitTypes.LayoutMillimeters))    #DIN A4 apaisat 297x210mm
    layout_map.attemptMove(QgsLayoutPoint(10, 10, QgsUnitTypes.LayoutMillimeters))

    # Rotació del mapa
    layout_map.setMapRotation(45)

    # Definició de l'extensió i vista
    extent = capa_extent.extent() 
    extent.scale(0.5)
    #extent.setXMinimum(extent.xMinimum() + 500)
    #extent.setXMaximum(extent.xMaximum() + 500)
    #extent.setYMinimum(extent.yMinimum() + 250)
    #extent.setYMaximum(extent.yMaximum() + 250)
    layout_map.zoomToExtent(extent)
    
    return layout_map


def afegir_titol(layout, titol, font, size, font_color, backg_color, frame_color):
    """
    Funció que
        Afegeix un element títol a la composició
        Estableix el text a mostrar
        Estableix el format, alineació, la posició i mida del text
        Estableix un fons
    """

    # Creació del títol
    title = QgsLayoutItemLabel(layout)
    
    # Addició del títol a la composició
    layout.addLayoutItem(title)

    # Definició del text i el seu format
    title.setText(titol)
    title_format = QgsTextFormat()
    title_format.setFont(QFont(font))
    title_format.setSize(size)
    title_format.setSizeUnit(QgsUnitTypes.RenderPoints)
    title_format.setColor(QColor(*font_color))
    title.setTextFormat(title_format)
    
    # Definició de posició i mida
    title.attemptMove(QgsLayoutPoint(10, 5, QgsUnitTypes.LayoutMillimeters))
    title.attemptResize(QgsLayoutSize(270, 10, QgsUnitTypes.LayoutMillimeters))

    # Definició de l'alineació
    title.setMarginX(5)  # marge horitzontal en mm
    title.setMarginY(1)  # marge vertical en mm
    title.setHAlign(Qt.AlignCenter)

    # Definició del fons i el marc
    title.setBackgroundEnabled(True)
    title.setBackgroundColor(QColor(*backg_color))
    title.setFrameEnabled(True)
    title.setFrameStrokeColor(QColor(*frame_color))
    title.setFrameStrokeWidth(QgsLayoutMeasurement(0.75, QgsUnitTypes.LayoutMillimeters))

    return title


def afegir_llegenda(layout, mapa, titol, font, size, font_color, backg_color):
    """
     Funció que
        Afegeix una llegenda a la composició
        Estableix el seu títol
        Estableix el format del text contingut
        Estableix un fons
    """

    # Creació de la llegenda
    legend = QgsLayoutItemLegend(layout)
    
    # Addició de la llegenda a la composició
    layout.addLayoutItem(legend)

    # Vinculació de la llegenda amb el mapa
    legend.setLinkedMap(mapa)
    
    # Construcció de la llegenda
    # Actualització automàtica de la llegenda
    legend.setAutoUpdateModel(True)
    #root = QgsLayerTree()

    #for layer in mapa.layers():
    #    root.addLayer(layer)

    #legend.model().setRootGroup(root) 


    # Definició d'un títol
    legend.setTitle(titol)

    # Definició de posició i mida
    legend.attemptMove(QgsLayoutPoint(250, 120, QgsUnitTypes.LayoutMillimeters))
    legend.adjustBoxSize()

    # Definició del format de text - tot igual
    text_format = QgsTextFormat()
    text_format.setFont(QFont(font))
    text_format.setSize(size)
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


def afegir_escala(layout, mapa, font, font_color):
    """
    Funció que defineix l'escala
    """
    
    # Creació de l'escala
    scale = QgsLayoutItemScaleBar(layout)
    
    # Addició de l'escala a la composició
    layout.addLayoutItem(scale)

    # Vinculació de l'escala amb el mapa
    scale.setLinkedMap(mapa)

    # Definició de mida
    #scale.attemptResize(QgsLayoutSize(15,15,QgsUnitTypes.LayoutMillimeters))
    scale.attemptMove(QgsLayoutPoint(15, 190, QgsUnitTypes.LayoutMillimeters))

    # Definició del tipus numèric
    scale.setStyle("Numeric")
    numeric_format = QgsBasicNumericFormat()
    numeric_format.setShowThousandsSeparator(True)
    numeric_format.setNumberDecimalPlaces(0)
    scale.setNumericFormat(numeric_format)

    # Definició del format de text
    scale_format = QgsTextFormat()
    scale_format.setFont(QFont(font))
    scale_format.setSize(16)
    scale_format.setSizeUnit(QgsUnitTypes.RenderPoints)
    scale_format.setColor(QColor(*font_color))
    scale.setTextFormat(scale_format)

    return scale


def afegir_nord(layout, mapa, path):
    """
    Funció que defineix la fletxa del nord a partir d'una imatge guardada en local
    """

    # Creació de la fletxa del nord
    north = QgsLayoutItemPicture(layout)

    # Addició del nord a la composició
    layout.addLayoutItem(north)

    # Vinculació de l'escala amb el mapa
    north.setLinkedMap(mapa)

    # Cerca de la imatge
    north.setPicturePath(path)  #"C:/projectes_git/Dades/nord2.png"
    
    # Definició de posició i mida
    north.attemptResize(QgsLayoutSize(10, 10, QgsUnitTypes.LayoutMillimeters))
    north.attemptMove(QgsLayoutPoint(15, 180, QgsUnitTypes.LayoutMillimeters))

    return north


def exportar_atles(layout, capa_cobertura, camp, output_path, dpi):
    """
    Funció per exportar la composició com a atles
    """

    # Activar l'atlas com a layout
    atlas = layout.atlas()
    atlas.setEnabled(True)

    # Definir la capa de cobertura
    atlas.setCoverageLayer(capa_cobertura) #dict_layers["Districtes"]

    # Establir el camp que genera els fulls - el nom de cada full
    atlas.setPageNameExpression(camp) #'"NOM"'
    atlas.setFilenameExpression(camp) #'"NOM"'

    # Ajustar la composició amb diferents mètodes
    # Fer que el mapa s'ajusti automàticament a cada feature
    layout.setAtlasDriven(True)
    # Establir zoom automàtic a cada element
    layout.setAtlasScalingMode(QgsLayoutItemMap.Auto)
    # Establir un marge percentual al voltant del mapa
    layout.setAtlasMargin(0.1)

    atlas.updateFeatures()
    
    atlas.beginRender()

    # Exportar tots els fulls
    exporter = QgsLayoutExporter(layout)
    pdf_settings = QgsLayoutExporter.PdfExportSettings()
    pdf_settings.dpi = dpi
    pdf_settings.forceVectorOutput = True
    pdf_settings.rasterizeWholeImage = False
    exporter.exportToPdf(
        atlas,
        output_path, #"C:/projectes_git/PyQGIS_practic/Resultats/"
        ".pdf",          
        pdf_settings
    )

    atlas.endRender()

