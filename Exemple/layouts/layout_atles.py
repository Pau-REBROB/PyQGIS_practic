"""
Composició tipus atles
======================

Funcions per generar una composició en format atles.

Cada entitat de la capa de cobertura genera una pàgina
independent de l'atles.

La composició inclou:

- mapa principal
- mapa localitzador
- títol
- llegenda
- escala gràfica
- fletxa del nord
- configuració de l'atles
- exportació a PDF

Organització
------------

- afegir_mapa()
- afegir_mapa_localitzador()
- generar_atles()
- exportar_atles()
- composicio_atles()
"""

from qgis.core import (
    QgsLayoutItemMap,
    QgsLayoutSize,
    QgsLayoutPoint,
    QgsRectangle,
    QgsUnitTypes,
    QgsLayoutMeasurement,
    QgsLayoutExporter
)

from qgis.PyQt.QtGui import QColor

import config
import layouts.layout_common as layout_common

def afegir_mapa(layout, capes, capa_extent, factor_escala, size, position, rotacio, offset_x, offset_y, color_fons=(0,0,0,0)):
    """
    Afegeix el mapa principal a la composició.

    La funció crea un element de mapa, configura les capes visibles,
    estableix la seva posició, mida, rotació i extensió inicial.

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
        ###
    offset_x: int
        ##
    offset_y: int
        ##
    color_fons: tuple[int,int,int,int], optional
        ###
        
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

    layout_map.zoomToExtent(capa_extent.extent())
    layout_map.setMapRotation(rotacio)
    layout_map.setScale(layout_map.scale() * factor_escala)

    # Desplaçament manual del centre del mapa
    extent = layout_map.extent()
    dx, dy = layout_common.transformar_offset(
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


def afegir_mapa_localitzador(layout, capa_localitzador, capa_extensio, mapa, size, position):
    """
    Afegeix un mapa localitzador a la composició de l'atles.

    El mapa localitzador mostra una vista general del municipi i 
    ressalta, mitjançant un "overview", l'extensió que representa 
    el mapa principal de cada pàgina de l'atles.

    Paràmetres
    ----------
    layout: QgsPrintLayout
        Composició sobre la qual s'afegeix el mapa localitzador.
    capa_localitzador: QgsVectorLayer
        Capa utilitzada per a representar el mapa localitzador.
    capa_extensio: QgsVectorLayer
        Capa utilitzada per a definir l'extensió fixa del mapa localitzador.
    mapa: QgsLayoutItemMap
        Mapa principal de la composició, que servirà de referència per a
        generar l'overview.
    size: tuple[int,int]
        Amplada i alçada de la imatge, en mil·límetres.
    position: tuple[int,int]
        Coordenada X i Y de la imatge - cantonada superior esquerra - en mil·límetres.

    Retorna
    -------
    QgsLayoutItemMap
        Element de mapa corresponent al localitzador.
    """

    # Crear del mapa
    locator = QgsLayoutItemMap(layout)
    layout.addLayoutItem(locator)

    # Afegir la capa que farà de localitzador
    locator.setLayers([capa_localitzador])
    locator.setKeepLayerSet(True)

    locator.attemptResize(QgsLayoutSize(*size, QgsUnitTypes.LayoutMillimeters))
    locator.attemptMove(QgsLayoutPoint(*position, QgsUnitTypes.LayoutMillimeters))

    # Extensió fixa del mapa localitzador
    locator.zoomToExtent(capa_extensio.extent())

    # L'overview representa sobre el mapa localitzador
    # l'extensió visible del mapa principal
    overview = locator.overview()
    overview.setLinkedMap(mapa)
    overview.setEnabled(True)
    
    # Afegir un marc per diferenciar visualment el mapa localitzador
    locator.setFrameEnabled(True)
    locator.setFrameStrokeWidth(QgsLayoutMeasurement(0.5, QgsUnitTypes.LayoutMillimeters))

    return locator


def generar_atles(layout, capa_cobertura, camp, mapa):
    """
    Configura l'atles d'una composició.

    La funció activa el mode Atles del layout, defineix la capa de
    cobertura i el camp que identifica cada pàgina, i configura
    el mapa principal perquè s'ajusti automàticament a cada entitat
    de la capa de cobertura.

    Paràmetres
    ----------
    layout: QgsPrintLayout
        Composició sobre la qual es configura l'atles.
    capa_cobertura: QgsVectorLayer
        Capa utilitzada per a generar les diferents pàgines de
        l'atles.
    camp: str
        Camp utilitzat tant per al nom de les pàgines com per al
        nom dels fitxers exportats.
    mapa: QgsLayoutItemMap
        Element mapa que es controlarà automàticament
        durant la generació de l'atles.

    Retorna
    -------
    QgsLayoutAtlas
        Objecte atles preparat i configurat per a exportar.
    """

    # Obtenir el gestor de l'atlas de la composició
    atlas = layout.atlas()
    atlas.setEnabled(True)

    # Definir la capa de cobertura
    # Cada entitat d'aquesta capa generarà una pàgina de l'atles
    atlas.setCoverageLayer(capa_cobertura)

    # El valor del camp s'utilitzarà com a nom de la pàgina i com
    # a nom de fitxer exportat
    atlas.setPageNameExpression(camp) 
    atlas.setFilenameExpression(camp) 

    # El mapa principal passa a ser controlat per l'atles
    mapa.setAtlasDriven(True)

    # Cada pàgina ajustarà automàticament el nivell de zoom a la 
    # geometria de l'entitat corresponent
    mapa.setAtlasScalingMode(QgsLayoutItemMap.Auto)
    
    # S'estableix un marge del 5% al voltant de cada entitat
    mapa.setAtlasMargin(0.05)

    # Actualitzar la llista d'entitats que formaran l'Atlas
    atlas.updateFeatures()

    return atlas


def exportar_atles(atlas, output_path, dpi):
    """
    Exporta un atles a un únic document PDF.

    Paràmetres
    ----------
    atlas: QgsLayoutAtlas
        Atles prèviament configurat.
    output_path: str
        Ruta del fitxer PDF de sortida.
    dpi: int
        Resolució d'exportació.
    
    Retorna
    -------
    None
    """

    # Configuració dels paràmetres d'exportació    
    pdf_settings = QgsLayoutExporter.PdfExportSettings()
    pdf_settings.dpi = dpi
    pdf_settings.forceVectorOutput = True
    pdf_settings.rasterizeWholeImage = False
    
    result, missatge_error = QgsLayoutExporter.exportToPdf(
        atlas,
        output_path,
        pdf_settings)
    
    if result != QgsLayoutExporter.Success:
        raise RuntimeError(f"No s'ha pogut exportar l'atles.\n{missatge_error}")
    

def composicio_atles(capes, capa_extent, capa_cobertura):
    """
    Genera la composició tipus atles del projecte.

    La funció crea una composició en format atles, incorpora
    els diferents elements cartogràfics, configura l'atles i 
    l'exporta a un document PDF.

    Paràmetres
    ----------
    capes: list[QgsMapLayer]
        Capes que es mostraran al mapa principal.
    capa_extent: QgsVectorLayer
        Capa utilitzada per a definir l'extensió general del mapa
        principal i l'extensió fixa del mapa localitzador.
    capa_cobertura: QgsVectorLayer
        Capa de cobertura de l'atles.
        Cada entitat genera una pàgina independent.

    Retorna
    -------
    None
    """

    cfg_layout = config.LAYOUTS["ATLES"]
    cfg_estructura = config.LAYOUTS["ESTRUCTURA_ATLES"]

    layout = layout_common.generar_layout(nom_layout="Ús dels edificis a Barcelona per districte")

    mapa = afegir_mapa(
        layout=layout,
        capes=capes,
        capa_extent=capa_extent,
        **cfg_estructura["Mapa"]
    )

    afegir_mapa_localitzador(
        layout=layout,
        capa_localitzador=capa_cobertura,
        capa_extensio=capa_extent,
        mapa=mapa,
        **cfg_estructura["Localitzador"]
    )

    layout_common.afegir_capçalera(
        layout=layout,
        **cfg_layout["Capçalera"],
        **cfg_estructura["Capçalera"]
    )

    layout_common.afegir_llegenda(
        layout=layout,
        mapa=mapa,
        capes=capes,
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

    atles = generar_atles(
        layout=layout,
        capa_cobertura=capa_cobertura,
        mapa=mapa,
        **cfg_layout["Generacio"]
    )

    exportar_atles(
        atlas=atles,
        **cfg_layout["Exportacio"]
    )
