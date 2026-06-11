"""COMPOSICIONS - LAYOUTS"""

# Composició general =============================

# LES CAPES QUE ES VOLGUIN MOSTRAR S'ESTABLIRAN DES DEL MAIN O EL CONFIG.

from qgis.core import (
    QgsProject,
    QgsPrintLayout,
    QgsLayoutItemMap,
    QgsLayoutItemLabel,
    QgsTextFormat,
    d,
    QgsLayoutItemScaleBar)

QgsLayoutSize
QgsLayoutPoint
QgsUnitTypes
QFont
QColor


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

    # Definició de l'extensió
    extent = capa_extent.extent() 
    layout_map.zoomToExtent(extent)

    # Definició de posició i mida
    layout_map.attemptResize(QgsLayoutSize(180, 180, QgsUnitTypes.LayoutMillimeters))    #DIN A4 apaisat 297x210mm
    layout_map.attemptMove(QgsLayoutPoint(10, 10, QgsUnitTypes.LayoutMillimeters))

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
    title.attemptMove(QgsLayoutPoint(15, 5, QgsUnitTypes.LayoutMillimeters))
    title.adjustSizeToText() #NO SÉ SI CAL 

    # Definició de l'alineació
    title.setMarginX(5)  # marge horitzontal en mm
    title.setMarginY(1)  # marge vertical en mm

    # Definició del fons i el marc
    title.setBackgroundEnabled(True)
    title.setBackgroundColor(QColor(*backg_color))
    title.setFrameEnabled(True)
    title.setFrameStrokeColor(QColor(*frame_color))
    title.setFrameStrokeWidth(QgsLayoutMeasurement(0.75, QgsUnitTypes.LayoutMillimeters))

    return title


def afegir_llegenda(layout):
    """
    Funció
    """


def afegir_escala(layout, mapa):
    """
    Funció
    """
    scale = QgsLayoutItemScaleBar(layout)
    layout.addLayoutItem(scale)

    scale.setLinkedMap(layout_map)

    #scale.attemptResize(QgsLayoutSize(15,15,QgsUnitTypes.LayoutMillimeters))
    scale.attemptMove(QgsLayoutPoint(270,200,QgsUnitTypes.LayoutMillimeters))

    scale.setStyle("Numeric")
    numeric_format = QgsBasicNumericFormat()
    numeric_format.setShowThousandsSeparator(True)
    numeric_format.setNumberDecimalPlaces(0)
    scale.setNumericFormat(numeric_format)

    scale_format = QgsTextFormat()
    scale_format.setFont(QFont("Arial"))
    scale_format.setSize(16)
    scale_format.setSizeUnit(QgsUnitTypes.RenderPoints)
    scale_format.setColor(QColor(255, 255, 255))
    scale.setTextFormat(scale_format)
    #scale.setFontColor(QColor(255, 255, 255))
