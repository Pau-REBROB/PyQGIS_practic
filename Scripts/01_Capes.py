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

# Altres proveïdors disponibles permeten carregar arxius CSV ("delimitedtext"), establir connexions WFS ("WFS") o carregar capes des d'un servidor PostgreSQL ("postgres")


"""Capes ràster"""



"""Addició de capes al llenç"""

# Per a afegir una capa ja importada al llenç cal afegir-la a la instància del projecte utilitzant el mètode `.addMapLayer()`
project.addMapLayer(vlayer)

# Aquest mètode, declarant la capa amb una instància QgsVectorLayer/QgsRasterLayer + utilitzant la instància del projecte, és el mètode més indicat per a importar capes
# De manera més ràpida i alternativa, es pot fer ús del mètode `addVectorLayer()` o `addRasterLayer()` de la classe `QgsInterface` per a carregar i visualitzar una capa
vlayer = iface.addVectorLayer()
# Igual que amb la classe QgsVectorLayer o QgsRasterLayer, cal especificar 
## Ruta on es troba la capa (*source*)
## Nom que es desitja donar (*layer name*) com a identificador en el panell de capes
## Proveïdor de dades vectorials
# `iface` - o QgsInterface - és una instància proporcionada per QGIS que enllaça la GUI amb el codi Python que, internament, utilitza el mètode indicat anterior (és un *wrapper*) 
# Per tant, ÚNICAMENT es pot fer servir quan es treballa a la GUI, és a dir, a la consola Python de QGIS 
