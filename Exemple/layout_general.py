"""COMPOSICIONS - LAYOUTS"""

# Composició general =============================

from qgis.core import (
    QgsLayoutItemMap,
    QgsLayoutSize,
    QgsLayoutPoint,
    QgsUnitTypes,
    QgsLayoutExporter
)

import os


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
    extent.setXMinimum(extent.xMinimum() + 500)
    extent.setXMaximum(extent.xMaximum() + 500)
    extent.setYMinimum(extent.yMinimum() + 250)
    extent.setYMaximum(extent.yMaximum() + 250)
    layout_map.zoomToExtent(extent)
    

    return layout_map


def exportar_layout(layout, output_path, dpi):
    """
    Funció per exportar la composició
    """

    #output_path = "C:/projectes_git/PyQGIS_practic/Resultats/Proximitat_retail.png"
    
    # Comprovació de composicions existents
    if os.path.exists(output_path):
        os.remove(output_path)  

    # Definició de l'exportador
    exporter = QgsLayoutExporter(layout)
    
    # Definició de paràmetres de configuració
    pdf_settings = QgsLayoutExporter.PdfExportSettings()
    pdf_settings.dpi = dpi
    pdf_settings.forceVectorOutput = True
    pdf_settings.rasterizeWholeImage = False
    
    # Exportació a PDF
    exporter.exportToPdf(output_path, pdf_settings)
    