"""
Layouts
=======

Funcions comunes per a la construcció de composicions d'impressió.
"""

from qgis.core import (
    Qgis,
    QgsBasicNumericFormat,
    QgsLayoutExporter,
    QgsLayoutItemLabel,
    QgsLayoutItemLegend,
    QgsLayoutItemMap,
    QgsLayoutItemPage,
    QgsLayoutItemPicture,
    QgsLayoutItemScaleBar,
    QgsLayoutItemShape,
    QgsLayoutMeasurement,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsLegendRenderer,
    QgsLegendStyle,
    QgsPrintLayout,
    QgsProject,
    QgsRectangle,
    QgsTextFormat,
    QgsUnitTypes,
    QgsFillSymbol
)

from qgis.PyQt.QtCore import Qt

from qgis.PyQt.QtGui import (
    QFont,
    QColor
)

import os
from math import radians, sin, cos

# =============================================================================
# LAYOUT
# =============================================================================

def generar_layout(nom_layout, orientacio="horitzontal"):
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
    orientacio: str
        Orientació de la composició.
        Per defecte "horitzontal", però també pot ser "vertical". 

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

    # Gestor de pàgines
    pc = layout.pageCollection()

    page = pc.page(0)

    if orientacio == "vertical":
        page.setPageSize('A4', QgsLayoutItemPage.Portrait)
    
    layout.setName(nom_layout)

    # Registre del layout al projecte
    manager.addLayout(layout)

    return layout

# =============================================================================
# MAPA
# =============================================================================

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


def afegir_mapa(layout, capes, capa_extent, factor_escala, size, position, rotacio, offset_x, offset_y, color_fons=(0,0,0,0)):
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
    rotacio: int
        Rotació del mapa, en graus.
    offset_x: float
        Desplaçament horitzontal del centre del mapa, en metres.
    offset_y: float
        Desplaçament vertical del centre del mapa, en metres.
    color_fons: tuple[int,int,int,int], optional
        Color de fons del mapa, en format (RGBA).
        Per defecte, transparent.
    
    Retorna
    -------
    QgsLayoutItemMap
        Element mapa.
    """

    # Configuració inicial del mapa
    layout_map = QgsLayoutItemMap(layout)
    
    layout.addLayoutItem(layout_map)

    layout_map.setLayers(capes)

    layout_map.setKeepLayerSet(True)

    # Ajust d'escala i rotació
    layout_map.attemptMove(QgsLayoutPoint(*position, QgsUnitTypes.LayoutMillimeters))
    layout_map.attemptResize(QgsLayoutSize(*size, QgsUnitTypes.LayoutMillimeters))

    # Ajust d'extensió
    if isinstance(capa_extent, QgsRectangle):
        extent = capa_extent
    else:
        extent = capa_extent.extent()

    layout_map.zoomToExtent(extent)
    layout_map.setMapRotation(rotacio)
    layout_map.setScale(layout_map.scale() * factor_escala)

    # Desplaçament manual del centre del mapa
    extent = layout_map.extent()
    dx, dy = transformar_offset(
        offset_x=offset_x,
        offset_y=offset_y,
        rotacio=rotacio
    )
    extent = QgsRectangle(
        extent.xMinimum() + dx,
        extent.yMinimum() + dy,
        extent.xMaximum() + dx,
        extent.yMaximum() + dy
    )
    layout_map.setExtent(extent)

    layout_map.setBackgroundEnabled(True)
    layout_map.setBackgroundColor(QColor(*color_fons))
        
    return layout_map


def calcular_extent_ampliat(geometria, marge_percentual=0.3):
    """
    Calcula un extent ampliat al voltant d'una geometria, afegint-hi
    un marge proporcional a la seva mida, per deixar context visual
    al voltant en un mapa retallat.

    Paràmetres
    ----------
    geometria: QgsGeometry
        Geometria de referència (p. ex. l'envolupant d'un clúster).
    marge_percentual: float
        Marge a afegir a cada costat, com a fracció de l'amplada/alçada
        de la geometria (0.3 = 30% de marge a cada banda).

    Retorna
    -------
    dict
        Diccionari { nom: QgsRectangle }, amb tots els extents ajustats
        a la mateixa mida (la del clúster més gran) perquè els mapes
        siguin comparables a la mateixa escala.
    """
    bbox = geometria.boundingBox()

    marge_x = bbox.width() * marge_percentual
    marge_y = bbox.height() * marge_percentual

    return QgsRectangle(
        bbox.xMinimum() - marge_x,
        bbox.yMinimum() - marge_y,
        bbox.xMaximum() + marge_x,
        bbox.yMaximum() + marge_y
    )


def calcular_extents_per_cluster(zones, dict_clusters, marge_percentual=0.3):
    """
    Calcula un extent ampliat i uniforme per a cadascun dels clústers
    indicats, a partir de la capa d'envolupants.

    Paràmetres
    ----------
    zones: QgsVectorLayer
        Capa d'envolupants de clústers, amb el camp CLUSTER_ID.
    dict_clusters: dict
        Diccionari { cluster_id: nom }, identificant els clústers
        a incloure.
    marge_percentual: float
        Marge de context a cada costat del bounding box del clúster.

    Retorna
    -------
    dict
        Diccionari { nom: QgsRectangle }, amb tots els extents ajustats
        a la mateixa mida (la del clúster més gran) perquè els mapes
        siguin comparables a la mateixa escala.
    """
    extents_bruts = {}
    
    for feat in zones.getFeatures():
        cluster_id = feat["CLUSTER_ID"]
        if cluster_id in dict_clusters:
            nom = dict_clusters[cluster_id]
            extents_bruts[nom] = calcular_extent_ampliat(
                geometria=feat.geometry()
            )

    print(zones.featureCount())
    ids_unics = {feat["CLUSTER_ID"] for feat in zones.getFeatures()}
    print("CLUSTER_ID únics:", ids_unics)

    costat_maxim = max(max(e.width(), e.height()) for e in extents_bruts.values())

    extents_finals = {}

    for nom, extent in extents_bruts.items():
        cx, cy = extent.center().x(), extent.center().y()
        meitat = costat_maxim / 2
        extents_finals[nom] = QgsRectangle(cx - meitat, cy - meitat, cx + meitat, cy + meitat)

    return extents_finals


def extents_manuals_a_dict(coordenades):
    """
    Converteix un diccionari de coordenades manuals en un diccionari
    d'extents (QgsRectangle), per a casos on els requadres de cada
    zona s'han determinat manualment en comptes de calcular-se a
    partir de la geometria d'un clúster.

    Paràmetres
    ----------
    coordenades: dict
        Diccionari { nom: (xmin, ymin, xmax, ymax) }, amb les
        coordenades de cada requadre en el CRS del projecte.

    Retorna
    -------
    dict
        Diccionari { nom: QgsRectangle }.
    """
    return {
        nom: QgsRectangle(xmin, ymin, xmax, ymax)
        for nom, (xmin, ymin, xmax, ymax) in coordenades.items()
    }


def uniformitzar_extents(extents_dict):
    """
    (docstring igual, ajustant la descripció del paràmetre a dict)
    """
    costat_maxim = max(max(e.width(), e.height()) for e in extents_dict.values())

    extents_uniformes = {}
    for nom, e in extents_dict.items():
        cx, cy = e.center().x(), e.center().y()
        meitat = costat_maxim / 2
        extents_uniformes[nom] = QgsRectangle(cx - meitat, cy - meitat, cx + meitat, cy + meitat)

    return extents_uniformes


# =============================================================================
# TÍTOLS
# =============================================================================

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

# =============================================================================
# LLEGENDA
# =============================================================================

def afegir_llegenda(layout, mapa, capes, titol, font, font_size, font_color, position, backg_color, size=None):
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
    legend.updateLegend()
    
    root = legend.model().rootGroup()

    ids_capes = {capa.id() for capa in capes}

    for node in list(root.findLayers()):
        if node.layerId() not in ids_capes:
            node.parent().removeChildNode(node)

        else:
            QgsLegendRenderer.setNodeLegendStyle(
                node,
                QgsLegendStyle.Hidden
            )

    root.removeChildrenGroupWithoutLayers()
    legend.updateLegend()   
    
    # Títol
    legend.setTitle(titol)

    # Posició i mida
    legend.attemptMove(QgsLayoutPoint(*position, QgsUnitTypes.LayoutMillimeters))
    if size is not None:
        legend.setResizeToContents(False)
        legend.setSplitLayer(True)
        legend.setColumnCount(3)
        legend.attemptResize(QgsLayoutSize(*size, QgsUnitTypes.LayoutMillimeters))
    else:
        legend.setResizeToContents(True)
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

# =============================================================================
# ESCALA
# =============================================================================

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

# =============================================================================
# NORD
# =============================================================================

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

# =============================================================================
# GRÀFICS
# =============================================================================

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

# =============================================================================
# EXPORTACIÓ
# =============================================================================

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
    RuntimeError
        Si no s'ha pogut exportar el layout.
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
