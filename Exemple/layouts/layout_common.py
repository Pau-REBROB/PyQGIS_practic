"""
Layouts
=======

Funcions comunes per a la construcció de composicions d'impressió.
"""

from qgis.core import (
    QgsBasicNumericFormat,
    QgsLayoutItemLabel,
    QgsLayoutItemLegend,
    QgsLayoutItemPicture,
    QgsLayoutItemScaleBar,
    QgsLayoutMeasurement,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsLegendStyle,
    QgsPrintLayout,
    QgsProject,
    QgsTextFormat,
    QgsUnitTypes
)

from qgis.PyQt.QtCore import Qt

from qgis.PyQt.QtGui import (
    QFont,
    QColor
)

def generar_layout(nom_layout):
    """
    Crea una nova composició d'impressió del projecte.

    Si ja existeix una composició amb el mateix nom, s'elimina
    abans de crear-ne una de nova.

    La composició s'inicialitza amb els valors per defecte de QGIS,
    rep el nom indicat i s'afegeix al gestor de composicions del 
    projecte.

    Paràmetres
    ----------
    nom_layout: str
        Nom que s'assignarà a la composició.

    Retorna
    -------
    QgsPrintLayout
        Nova composició registrada al gestor de composicions del projecte. 
    """
    
    # Gestor de composicions
    manager = QgsProject.instance().layoutManager()

    # Si hi ha existència prèvia del layout, s'elimina
    for layout in manager.printLayouts():
        if layout.name() == nom_layout:
            manager.removeLayout(layout)
    
    # Creació i inicialització del layout
    layout = QgsPrintLayout(QgsProject.instance())
    layout.initializeDefaults()
    
    layout.setName(nom_layout)

    # Registre del layout al projecte
    manager.addLayout(layout)

    return layout


def afegir_titol(layout, titol, font, size, font_color, backg_color, frame_color):
    """
    Afegeix un títol a la composició.

    La funció crea una etiqueta de text, configura el seu contingut,
    el format tipogràfic, la posició, la mida i l'estil del marc,
    i l'afegeix a la composició indicada.

    Paràmetres
    ----------
    layout: QgsPrintLayout
        Composició on s'insereix el títol.
    titol: str
        Text que es mostrarà com a títol.
    font: str
        Nom de la família tipogràfica.
    size: float
        Mida del text, en punts.
    font_color: tuple[int,int,int,int]
        Color del text, en format (RGBA).
    backg_color: tuple[int,int,int,int]
        Color del fons, en format (RGBA).
    frame_color: tuple[int,int,int,int]
        Color del marc, en format (RGBA).

    Retorna
    -------
    QgsLayoutItemLabel
        Element de tipus etiqueta.
    """

    title = QgsLayoutItemLabel(layout)
    
    layout.addLayoutItem(title)

    # Definició del text i el seu format
    title.setText(titol)
    text_format = QgsTextFormat()
    text_format.setFont(QFont(font))
    text_format.setSize(size)
    text_format.setSizeUnit(QgsUnitTypes.RenderPoints)
    text_format.setColor(QColor(*font_color))
    title.setTextFormat(text_format)
    
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


def afegir_llegenda(layout, mapa, capes, titol, font, size, font_color, backg_color):
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
     size: float
        Mida del text, en punts.
     font_color: tuple[int,int,int,int]
        Color del text, en format (RGBA).
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

    ids_capes = {capa.id() for capa in capes}

    for node in list(root.findLayers()):
        if node.layerId() not in ids_capes:
            root.removeLayer(node.layer())
    
    # Títol
    legend.setTitle(titol)

    # Posició i mida
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
    Afegeix una escala numèrica a una composició.

    La funció crea una escala vinculada al mapa indicat i configura
    la seva posició, mida, el format numèric i l'estil del text.

    Paràmetres
    ----------
    layout: QgsPrintLayout
        Composició on s'insereix l'escala.
    mapa: QgsLayoutItemMap
        Element mapa al qual queda vinculada l'escala.
    font: str
        Nom de la família tipogràfica.
    font_color: tuple[int,int,int,int]
        Color del text, en format (RGBA).

    Retorna
    -------
    QgsLayoutItemScaleBar
        Element escala.
    """
    
    # Creació de l'escala
    scale = QgsLayoutItemScaleBar(layout)
    layout.addLayoutItem(scale)

    # Vinculació amb el mapa
    scale.setLinkedMap(mapa)

    # Definició de mida
    scale.attemptMove(QgsLayoutPoint(15, 190, QgsUnitTypes.LayoutMillimeters))

    # Format numèric
    scale.setStyle("Numeric")
    numeric_format = QgsBasicNumericFormat()
    numeric_format.setShowThousandsSeparator(True)
    numeric_format.setNumberDecimalPlaces(0)
    scale.setNumericFormat(numeric_format)

    # Format de text
    text_format = QgsTextFormat()
    text_format.setFont(QFont(font))
    text_format.setSize(16)
    text_format.setSizeUnit(QgsUnitTypes.RenderPoints)
    text_format.setColor(QColor(*font_color))
    scale.setTextFormat(text_format)

    return scale


def afegir_nord(layout, mapa, image_path):
    """
    Afegeix una fletxa del nord a una composició.

    La funció crea un element d'imatge vinculat al mapa indicat,
    carrega la imatge especificada i en configura la posició i mida.

    Paràmetres
    ----------
    layout: QgsPrintLayout
        Composició on s'insereix la fletxa del nord.
    mapa: QgsLayoutItemMap
        Element mapa al qual queda vinculada la fletxa.
    image_path: str
        Ruta local de la imatge utilitzada com a símbol de la fletxa del nord.
    
    Retorna
    -------
    QgsLayoutItemPicture
        Element gràfic.
    """

    # Creació de la fletxa del nord
    north = QgsLayoutItemPicture(layout)
    layout.addLayoutItem(north)

    # Vinculació amb el mapa
    north.setLinkedMap(mapa)

    # Imatge
    north.setPicturePath(image_path)
    
    # Posició i mida
    north.attemptResize(QgsLayoutSize(10, 10, QgsUnitTypes.LayoutMillimeters))
    north.attemptMove(QgsLayoutPoint(15, 180, QgsUnitTypes.LayoutMillimeters))

    return north


def afegir_grafic(layout, path, width, height, x, y):
    """
    Afegeix una imatge a una composició.

    La funció crea un element d'imatge, carrega el fitxer indicat,
    i en configura la posició i mida dins la composició.

    Paràmetres
    ----------
    layout: QgsPrintLayout
        Composició on s'insereix la imatge.
    path: str
        Ruta de la imatge.
    width: float
        Amplada de la imatge, en mil·límetres.
    height: float
        Alçada de la imatge, en mil·límetres.
    x: float
        Coordenada X de la imatge - cantonada superior esquerra - en mil·límetres.
    y: float
        Coordenada Y de la imatge - cantonada superior esquerra - en mil·límetres.

    Retorna
    -------
    QgsLayoutItemPicture
        Element gràfic. 
    """

    # Creació de la imatge
    image = QgsLayoutItemPicture(layout)
    layout.addLayoutItem(image)

    # Imatge
    image.setPicturePath(path)
    
    # Definició de posició i mida
    image.attemptResize(QgsLayoutSize(width, height, QgsUnitTypes.LayoutMillimeters))
    image.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))

    return image