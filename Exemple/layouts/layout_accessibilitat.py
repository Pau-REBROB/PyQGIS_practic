"""
Composició accessibilitat
=========================

Funcions per generar la composició d'anàlisi
d'accessibilitat del projecte.

La composició inclou:

- mapa principal
- títol
- llegenda
- escala gràfica
- fletxa del nord
- exportació a PDF

Organització
------------

- afegir_mapa()
- exportar_layout()
- composicio_general()
"""

from qgis.core import (
    QgsLayoutExporter,
    QgsLayoutItemMap,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsRectangle,
    QgsUnitTypes,
)
from qgis.PyQt.QtGui import QColor

import os

import config
import layouts.layout_common as layout_common

def afegir_mapa(layout, capes, capa_extent, factor_escala, size, position, rotacio, offset_x, offset_y, color_fons=(0,0,0,0)):
    """
    Afegeix l'element mapa principal a una composició.

    La funció crea un element `QgsLayoutItemMap`, hi assocïa les capes
    indicades, ajusta l'extensió inicial a partir de la capa de 
    referència i configura la seva posició, mida i rotació.

    L'ordre de les operacions:
        1. Definir la mida i posició del mapa,
        2. Ajustar l'extensió al conjunt de dades,
        3. Aplicar la rotació,
        4. Modificar l'escala,
        5. Aplicar un desplaçament manual del centre,
    evita modificacions inesperades de l'escala o l'extensió quan el
    mapa està rotat.

    Observacions
    ------------
    Els desplaçaments `offset_x` i `offset_y` s'apliquen després
    de la rotació mitjançant una funció auxiliar `transformar_offset()`
    per mantenir la direcció visual del desplaçament de manera
    independent a l'orientació del mapa.

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
    color_fons: tuple[int,int,int,int]
        Color de fons del mapa.

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


def composicio_accessibilitat(capes, capa_extent):
    """
    Genera la composició cartogràfica general del projecte.

    La funció coordina totes les operacions necessàries per crear el
    layout principal del projecte:
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

    cfg_layout = config.LAYOUTS["ACCESSIBILITAT"]
    cfg_estructura = config.LAYOUTS["ESTRUCTURA_ACCESS"]

    layout = layout_common.generar_layout(nom_layout="Accessibilitat comerços Barcelona")

    mapa = afegir_mapa(
        layout=layout,
        capes=capes,
        capa_extent=capa_extent,
        **cfg_layout["Mapa"],
        **cfg_estructura["Mapa"]
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

    exportar_layout(
        layout=layout,
        **cfg_layout["Exportacio"]
    )
