"""COMPOSICIONS - LAYOUTS"""

# Mòdul de funcions comunes

from qgis.core import (
    QgsProject,
    QgsPrintLayout,
    QgsLayoutSize,
    QgsLayoutMeasurement,
    QgsLayoutPoint,
    QgsUnitTypes,
    QgsLayoutItemLabel,
    QgsTextFormat,
    QgsLayoutItemLegend,
    QgsLegendStyle,
    QgsLayoutItemScaleBar,
    QgsBasicNumericFormat,
    QgsLayoutItemPicture,
)

from qgis.PyQt.QtGui import (
    QFont,
    QColor
)

from qgis.PyQt.QtCore import Qt


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
    title.attemptResize(QgsLayoutSize(280, 10, QgsUnitTypes.LayoutMillimeters))

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
    legend.attemptMove(QgsLayoutPoint(240, 60, QgsUnitTypes.LayoutMillimeters))
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

    # Vinculació de la imatge amb el mapa
    north.setLinkedMap(mapa)

    # Cerca de la imatge
    north.setPicturePath(path)
    
    # Definició de posició i mida
    north.attemptResize(QgsLayoutSize(10, 10, QgsUnitTypes.LayoutMillimeters))
    north.attemptMove(QgsLayoutPoint(15, 180, QgsUnitTypes.LayoutMillimeters))

    return north


def afegir_grafic(layout, path, x_s, y_s, x_m, y_m):
    """
    Funció que insereix un gràfic en forma d'imatge a la composició
    """

    # Creació de la imatge
    image = QgsLayoutItemPicture(layout)

    # Addició de la imatge a la composició
    layout.addLayoutItem(image)

    # Cerca de la imatge
    image.setPicturePath(path)
    
    # Definició de posició i mida
    image.attemptResize(QgsLayoutSize(x_s, y_s, QgsUnitTypes.LayoutMillimeters))
    image.attemptMove(QgsLayoutPoint(x_m, y_m, QgsUnitTypes.LayoutMillimeters))

    return image