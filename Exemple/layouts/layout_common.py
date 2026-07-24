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
    QgsLayoutItemShape,
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


def afegir_fons(layout, size, position, color):
    """
    Afegeix un rectangle de fons a la composició.

    Paràmetres
    ----------
    layout: QgsPrintLayout
        Composició on s'afegeix el fons.
    size: tuple[int,int]
         Amplada i alçada de la imatge, en mil·límetres.
    position: tuple[int,int]
        Coordenada X i Y de la imatge - cantonada superior esquerra - en mil·límetres.
    color: tuple[int,int,int,int]
        Color del fons, en format (RGBA).
    """

    rectangle = QgsLayoutItemShape(layout)

    layout.addLayoutItem(rectangle)

    rectangle.setShapeType(QgsLayoutItemShape.Rectangle)

    rectangle.attemptMove(QgsLayoutPoint(*position, QgsUnitTypes.LayoutMillimeters))
    rectangle.attemptResize(QgsLayoutSize(*size, QgsUnitTypes.LayoutMillimeters))

    rectangle.setBackgroundColor(QColor(*color))

    rectangle.setFrameEnabled(False)

    return rectangle


def afegir_titol(layout, titol, font, font_size, font_color, size, position, alineacio, backg_color, frame_color):
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
    font_size: float
        Mida del text, en punts.
    font_color: tuple[int,int,int,int]
        Color del text, en format (RGBA).
    size: tuple[int,int]
        Amplada i alçada de la imatge, en mil·límetres.
    position: tuple[int,int]
        Coordenada X i Y de la imatge - cantonada superior esquerra - en mil·límetres.
    alineacio: str
        Alineació del text respecte el full.    
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
    text_format.setSize(font_size)
    text_format.setSizeUnit(QgsUnitTypes.RenderPoints)
    text_format.setColor(QColor(*font_color))
    title.setTextFormat(text_format)
    
    # Definició de posició i mida
    title.attemptMove(QgsLayoutPoint(*position, QgsUnitTypes.LayoutMillimeters))
    title.attemptResize(QgsLayoutSize(*size, QgsUnitTypes.LayoutMillimeters))

    # Definició de l'alineació
    title.setMarginX(5)
    title.setMarginY(1)
    alineacions = {
        "left": Qt.AlignLeft,
        "right": Qt.AlignRight,
        "center": Qt.AlignCenter
    }
    title.setHAlign(alineacions[alineacio])

    # Definició del fons i el marc
    title.setBackgroundEnabled(True)
    title.setBackgroundColor(QColor(*backg_color))
    title.setFrameEnabled(True)
    title.setFrameStrokeColor(QColor(*frame_color))
    title.setFrameStrokeWidth(QgsLayoutMeasurement(0.75, QgsUnitTypes.LayoutMillimeters))

    return title


def afegir_subtitol(layout, subtitol, font, font_size, font_color, size, position, alineacio, backg_color, frame_color):
    """
    Afegeix un subtítol a la composició.

    La funció crea una etiqueta de text, configura el seu contingut,
    el format tipogràfic, la posició, la mida i l'estil del marc,
    i l'afegeix a la composició indicada.

    Paràmetres
    ----------
    layout: QgsPrintLayout
        Composició on s'insereix el títol.
    subtitol: str
        Text que es mostrarà com a subtítol.
    font: str
        Nom de la família tipogràfica.
    font_size: float
        Mida del text, en punts.
    font_color: tuple[int,int,int,int]
        Color del text, en format (RGBA).
    size: tuple[int,int]
        Amplada i alçada de la imatge, en mil·límetres.
    position: tuple[int,int]
        Coordenada X i Y de la imatge - cantonada superior esquerra - en mil·límetres.
    alineacio: str
        Alineació del text respecte el full.    
    backg_color: tuple[int,int,int,int]
        Color del fons, en format (RGBA).
    frame_color: tuple[int,int,int,int]
        Color del marc, en format (RGBA).

    Retorna
    -------
    QgsLayoutItemLabel
        Element de tipus etiqueta.
    """

    subtitle = QgsLayoutItemLabel(layout)
    
    layout.addLayoutItem(subtitle)

    # Definició del text i el seu format
    subtitle.setText(subtitol)
    text_format = QgsTextFormat()
    text_format.setFont(QFont(font))
    text_format.setSize(font_size)
    text_format.setSizeUnit(QgsUnitTypes.RenderPoints)
    text_format.setColor(QColor(*font_color))
    subtitle.setTextFormat(text_format)
    
    # Definició de posició i mida
    subtitle.attemptMove(QgsLayoutPoint(*position, QgsUnitTypes.LayoutMillimeters))
    subtitle.attemptResize(QgsLayoutSize(*size, QgsUnitTypes.LayoutMillimeters))

    # Definició de l'alineació
    subtitle.setMarginX(5)
    subtitle.setMarginY(1)
    alineacions = {
        "left": Qt.AlignLeft,
        "right": Qt.AlignRight,
        "center": Qt.AlignCenter
    }
    subtitle.setHAlign(alineacions[alineacio])

    # Definició del fons i el marc
    subtitle.setBackgroundEnabled(True)
    subtitle.setBackgroundColor(QColor(*backg_color))
    subtitle.setFrameEnabled(True)
    subtitle.setFrameStrokeColor(QColor(*frame_color))
    subtitle.setFrameStrokeWidth(QgsLayoutMeasurement(0.75, QgsUnitTypes.LayoutMillimeters))

    return subtitle


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


def afegir_escala(layout, mapa, position, font, font_color):
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
    position: tuple[int,int]
        Coordenada X i Y de la imatge - cantonada superior esquerra - en mil·límetres.
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
    scale.attemptMove(QgsLayoutPoint(*position, QgsUnitTypes.LayoutMillimeters))

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


def afegir_nord(layout, mapa, image_path, size, position):
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
    size: tuple[int,int]
        Amplada i alçada de la imatge, en mil·límetres.
    position: tuple[int,int]
        Coordenada X i Y de la imatge - cantonada superior esquerra - en mil·límetres.
    
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
    north.attemptResize(QgsLayoutSize(*size, QgsUnitTypes.LayoutMillimeters))
    north.attemptMove(QgsLayoutPoint(*position, QgsUnitTypes.LayoutMillimeters))

    return north


def afegir_grafic(layout, path, size, position):
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
    size: tuple[int,int]
        Amplada i alçada de la imatge, en mil·límetres.
    position: tuple[int,int]
        Coordenada X i Y de la imatge - cantonada superior esquerra - en mil·límetres.
    
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
    image.attemptResize(QgsLayoutSize(*size, QgsUnitTypes.LayoutMillimeters))
    image.attemptMove(QgsLayoutPoint(*position, QgsUnitTypes.LayoutMillimeters))

    return image