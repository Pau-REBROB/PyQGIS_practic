"""
Inicialització del projecte
===========================

Conté les funcions necessàries per preparar l'entorn de treball de QGIS.

El mòdul defineix les funcions encarregades de crear l'entorn inicial
del projecte abans d'executar la resta del flux de treball.
"""

from qgis.core import (
    QgsProject,
    QgsCoordinateReferenceSystem
)

def inicialitzar_projecte():
    """
    Inicialitza el projecte de QGIS.

    La funció:
        - obté la instància del projecte,
        - estableix el títol del projecte,
        - estableix el sistema de referència de coordenades del projecte.


    Retorna
    -------
    tupla
        (QgsProject, QgsLayerTree)
        
        on:
            - QgsProject correspon a la instància del projecte,
            - QgsLayerTree correspon a l'arrel del panell de capes del projecte.
    """
    
    project = QgsProject.instance()
    root = project.layerTreeRoot()

    # Nom del projecte
    project.setTitle("Anàlisi geoespacial de la distribució funcional i l'accessibilitat comercial a Barcelona")

    # Definició del SRC del projecte
    project.setCrs(QgsCoordinateReferenceSystem("EPSG:25831"))

    return project, root
