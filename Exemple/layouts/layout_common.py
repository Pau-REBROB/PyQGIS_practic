"""
Layouts
=======

Funcions comunes per a la construcció de composicions d'impressió.
"""

from qgis.core import (
    Qgis,
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
    QgsUnitTypes,
    QgsFillSymbol
)

from qgis.PyQt.QtCore import Qt

from qgis.PyQt.QtGui import (
    QFont,
    QColor
)

from math import radians, sin, cos

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


def transformar_offset(offset_x, offset_y, rotacio):
    """
    Transforma un desplaçament visual (en pantalla) a un desplaçament
    en coordenades del mapa.

    Quan el mapa està rotat, un desplaçament horitzontal o vertical sobre
    el paper no coincideix amb els eixos del sistema de coordenades. Aquesta
    funció aplica la transformació trigonomètrica necessària per a convertir
    un desplaçament visual en un desplaçament real sobre l'extensió del mapa.

    Paràmetres
    ----------
    offset_x: float
        Desplaçament visual horitzontal.
        Negatiu implica esquerra, positiu implica dreta.
    offset_y: float
        Desplaçament visual vertical.
        Negatiu implica amunt, positiu implica avall.
    rotacio: float
        Rotació del mapa, en graus.

    Retorna
    -------
    tuple[float,float]
        Desplaçament X i Y en coordenades del projecte.
    """

    angle = radians(rotacio)

    dx = offset_x * cos(angle) - offset_y * sin(angle)
    dy = offset_x * sin (angle) + offset_y * cos(angle)

    return dx, dy


def afegir_fons(layout, size, position, color, outline_color=None, outline_width=0.26):
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
    outline_color: tuple[int,int,int,int]
        ###
    outline_width: float
        ###
    """

    rectangle = QgsLayoutItemShape(layout)
    layout.addLayoutItem(rectangle)

    rectangle.setShapeType(QgsLayoutItemShape.Rectangle)

    params = {
        "color": f"{color[0]},{color[1]},{color[2]},{color[3]}"
    }
    if outline_color is None:
        params["outline_style"] = "no"
    else:
        params["outline_color"] = f"{outline_color[0]},{outline_color[1]},{outline_color[2]},{outline_color[3]}"
        params["outline_width"]= str(outline_width)

    symbol = QgsFillSymbol.createSimple(
        params
    )

    rectangle.setSymbol(symbol)

    rectangle.attemptMove(QgsLayoutPoint(*position, QgsUnitTypes.LayoutMillimeters))
    rectangle.attemptResize(QgsLayoutSize(*size, QgsUnitTypes.LayoutMillimeters))

    return rectangle


def afegir_text(layout, text, font, font_size, font_color, size, position, marge_X=0, marge_Y=0, alineacio="left", rotacio=0,
                backg_enabled=False, backg_color=None, frame_enabled=False, frame_color=None):
    """
    Afegeix un text a la composició.

    La funció crea una etiqueta de text, configura el seu contingut,
    el format tipogràfic, la posició, la mida i l'estil del marc,
    i l'afegeix a la composició indicada.

    Paràmetres
    ----------
    layout: QgsPrintLayout
        Composició on s'insereix el títol.
    text: str
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
    marge_X: float
        ###
    marge_Y: float
        ###
    alineacio: str
        Alineació del text respecte el full.
    rotacio: float
        Rotació del text respecte el full.
    backg_enabled: bool
        Activació del fons.    
    backg_color: tuple[int,int,int,int]
        Color del fons, en format (RGBA).
    frame_enabled: bool
        Activació del marc.
    frame_color: tuple[int,int,int,int]
        Color del marc, en format (RGBA).

    Retorna
    -------
    QgsLayoutItemLabel
        Element de tipus etiqueta.
    """

    layout_text = QgsLayoutItemLabel(layout)
    
    layout.addLayoutItem(layout_text)

    # Definició del text i el seu format
    layout_text.setText(text)
    text_format = QgsTextFormat()
    text_format.setFont(QFont(font))
    text_format.setSize(font_size)
    text_format.setSizeUnit(QgsUnitTypes.RenderPoints)
    text_format.setColor(QColor(*font_color))
    layout_text.setTextFormat(text_format)

    # Definició de posició i mida
    layout_text.attemptMove(QgsLayoutPoint(*position, QgsUnitTypes.LayoutMillimeters))
    layout_text.setItemRotation(rotacio)
    # IMPORTANT:
    # A QGIS 3.44 la rotació s'ha d'aplicar abans de attemptMove().
    # En cas contrari la posició final del label és incorrecta.
    layout_text.attemptResize(QgsLayoutSize(*size, QgsUnitTypes.LayoutMillimeters))

    # Definició de l'alineació
    layout_text.setMarginX(marge_X)
    layout_text.setMarginY(marge_Y)
    alineacions = {
        "left": Qt.AlignLeft,
        "right": Qt.AlignRight,
        "center": Qt.AlignCenter
    }
    layout_text.setHAlign(alineacions[alineacio])

    # Definició del fons i el marc
    layout_text.setBackgroundEnabled(backg_enabled)
    if backg_color is not None:
        layout_text.setBackgroundColor(QColor(*backg_color))
    layout_text.setFrameEnabled(frame_enabled)
    if frame_color is not None:
        layout_text.setFrameStrokeColor(QColor(*frame_color))
        layout_text.setFrameStrokeWidth(QgsLayoutMeasurement(0.75, QgsUnitTypes.LayoutMillimeters))

    return layout_text


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

    return afegir_text(
        layout=layout,
        text=titol,
        font=font,
        font_size=font_size,
        font_color=font_color,
        size=size,
        position=position,
        marge_X=5,
        marge_Y=2,
        alineacio=alineacio,
        rotacio=0,
        backg_enabled=True,
        backg_color=backg_color,
        frame_enabled=True,
        frame_color=frame_color
    )


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

    return afegir_text(
        layout=layout,
        text=subtitol,
        font=font,
        font_size=font_size,
        font_color=font_color,
        size=size,
        position=position,
        marge_X=5,
        marge_Y=2,
        alineacio=alineacio,
        rotacio=0,
        backg_enabled=True,
        backg_color=backg_color,
        frame_enabled=True,
        frame_color=frame_color
    )


def afegir_capçalera(layout, backg_size, backg_position, color, outline_color, outline_width,
                     text, font, font_size, font_color, text_size, text_position):
    """
    """

    afegir_fons(
        layout=layout,
        size=backg_size,
        position=backg_position,
        color=color,
        outline_color=outline_color,
        outline_width=outline_width
    )

    afegir_text(
        layout=layout,
        text=text,
        font=font,
        font_size=font_size,
        font_color=font_color,
        size=text_size,
        position=text_position
    )


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


def afegir_escala(layout, mapa, position, tipus, font, font_size, font_color):
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
    tipus: str
        Format d'escala.
    font: str
        Nom de la família tipogràfica.
    font_size: int
        ##
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

    # Unitats
    scale.setUnits(Qgis.DistanceUnit.Meters)
    scale.setUnitLabel("m")

    # Definició de mida
    scale.attemptMove(QgsLayoutPoint(*position, QgsUnitTypes.LayoutMillimeters))

    # Format de text
    text_format = QgsTextFormat()
    text_format.setFont(QFont(font))
    text_format.setSize(font_size)
    text_format.setSizeUnit(QgsUnitTypes.RenderPoints)
    text_format.setColor(QColor(*font_color))
    scale.setTextFormat(text_format)

    # Format numèric
    if tipus == "numeric":
        scale.setStyle("Numeric")

        # Format numèric
        numeric_format = QgsBasicNumericFormat()
        numeric_format.setShowThousandsSeparator(True)
        numeric_format.setNumberDecimalPlaces(0)
        scale.setNumericFormat(numeric_format)

    # Format gràfic
    elif tipus == "Single Box":
        scale.setStyle("Single Box")

        # Format de barra
        scale.setNumberOfSegments(2)
        scale.setNumberOfSegmentsLeft(0)
        scale.setUnitsPerSegment(500)
        scale.setHeight(2.5)


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