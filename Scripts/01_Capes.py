"""Capes vectorials"""

# En el supòsit que no es treballi a la consola Python de QGIS
import os
from qgis.core import QgsVectorLayer

# Per importar i afegir al projecte una capa vectorial cal crear una instància de la classe `QgsVectorLayer`
# Cal especificar:
## Ruta on es troba la capa (*source*)
## Nom que es desitja donar (*layer name*) com a identificador en el panell de capes
## Proveïdor de dades vectorials
vlayer = QgsVectorLayer("Filepath_capa", "Nom_capa", "Proveïdor")

# El proveïdor "ogr" de la llibreria GDAL suporta gran varietat de formats, incloent els Shapefile, GeoJSON, GeoPackage i DXF d'AutoCAD
# En el cas dels geopackage, cal especificar la capa que es vol importar
vlayer = QgsVectorLayer("Projecte/Dades/dades.gpkg|layername=Aeroports", "Aeroports", "ogr")

