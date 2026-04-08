"""Execució implícita quan s'inicialitza la consola Python de QGIS"""
from qgis.core import *
import qgis.utils


# En el supòsit que no es treballi a la consola Python de QGIS
from qgis.core import QgsProject

# Sempre és necessari crear una instància de la classe `QgsProject`
## Al ser una classe *singleton* - és a dir, d'instància única - cal utilitzar el mètode `.instance()`
project = QgsProject.instance()

# Si es vol importar un projecte existent a l'aplicatiu de QGIS en blanc, cal cridar-lo amb el mètode `.read()`
project.read("Filepath_projecte/Nom_projecte.qgs")
# Per desar els canvis en el projecte, s'utilitza el mètode `.write()`
## Si no s'especifica cap ruta, el projecte es guardarà en el mateix directori sota el mateix nom
## Si es fa passar una ruta diferent com a argument, el projecte es guardarà en un nou directori i/o amb un nom diferent  
project.write()
