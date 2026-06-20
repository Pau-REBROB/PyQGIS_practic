"""COMPOSICIONS - LAYOUTS"""

# Composició en atles

from qgis.core import (
    QgsLayoutItemMap,
    QgsLayoutSize,
    QgsLayoutPoint,
    QgsUnitTypes,
    QgsLayoutExporter
)


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


def generar_atles(layout, capa_cobertura, camp, mapa):
    """
    Funció per generar l'atles
    """

    # Activar l'atlas com a layout
    atlas = layout.atlas()
    atlas.setEnabled(True)

    # Definir la capa de cobertura
    atlas.setCoverageLayer(capa_cobertura)

    # Establir el camp que genera els fulls - el nom de cada full
    atlas.setPageNameExpression(camp) 
    atlas.setFilenameExpression(camp) 

    # Ajustar la composició amb diferents mètodes
    # Fer que el mapa s'ajusti automàticament a cada feature
    mapa.setAtlasDriven(True)
    # Establir zoom automàtic a cada element
    mapa.setAtlasScalingMode(QgsLayoutItemMap.Auto)
    # Establir un marge percentual al voltant del mapa
    mapa.setAtlasMargin(0.1)

    atlas.updateFeatures()

    return atlas


def exportar_atles(atlas, output_path, dpi):
    """
    Funció per exportar la composició com a atles
    """
    
    # Exportar tots els fulls
    #exporter = QgsLayoutExporter(layout)
    
    pdf_settings = QgsLayoutExporter.PdfExportSettings()
    pdf_settings.dpi = dpi
    pdf_settings.forceVectorOutput = True
    pdf_settings.rasterizeWholeImage = False
    
    result, error = QgsLayoutExporter.exportToPdf(
        atlas,
        output_path,
        pdf_settings)
    
    return result
