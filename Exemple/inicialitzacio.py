"""INICIALITZACIÓ DEL PROJECTE"""

from qgis.core import QgsProject, QgsCoordinateReferenceSystem

def inicialitzar_projecte():
    """
    Funció 
        Defineix una instància del projecte (project) i del panell de capes (root)
        Neteja totes les capes i grups de capes preexistents al projecte
        Estableix el SRC del projecte
    """
    
    # Generar instància del projecte
    project = QgsProject.instance()

    # Generar instància del panell de capes
    root = project.layerTreeRoot()

    # Netejar totes les capes i grups existents al projecte
    project.removeAllMapLayers()
    root.removeAllChildren()

    # Establiment del SRC
    project.setCrs(QgsCoordinateReferenceSystem("EPSG:25831"))

    return project, root


import sys
import importlib

def recarregar_moduls(llista):
    """
    Funció encarregada de recarregar els mòduls propis importats 
    """
    
    for mod in llista:
        if mod in sys.modules:
            importlib.reload(sys.modules[mod])
