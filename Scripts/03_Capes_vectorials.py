"""Manipulació de capes vectorials"""

# En el supòsit que no es treballi a la consola Python de QGIS
import os
from qgis.core import QgsVectorLayer

# Les capes vectorials son una instància de la classe `QgsVectorLayer`
# Per a la seva importació, cal especificar:
## Ruta on es troba la capa (*source*)
## Nom que es desitja donar (*layer name*) com a identificador en el panell de capes
## Proveïdor de dades vectorials
vlayer = QgsVectorLayer("Filepath_capa", "Nom_capa", "Proveïdor")

# Les capes vectorials estan formades per un conjunt de *FEATURES*, que representen elements individuals dins la capa (les geometries vectorials)
# S'accedeix al conjunt de *features* d'una capa vectorial a través del mètode `.getFeatures()`, que retorna els elements en format llista 
features = vlayer.getFeatures()
# Aquest fet fa que SEMPRE s'hagi d'iterar sobre el conjunt d'elements d'una capa vectorial per tal de treuer'n informació
for feature in features:
  print("Feature ID: ", feature.id())
  geom = feature.geometry()  
  # etcètera

# Cada *feature* conté la informació estructurada en *ATTRIBUTES* - en camps, equivalent a les columnes d'una taula de dades
# Es pot conèixer el conjunt d'atributs d'un element amb el mètode `.attributes()`
feature.attributes()
# Es pot accedir a la informació continguda en els atributs d'un element a través del nom de l'atribut
feature['nom']
# Alternativament, s'hi pot accedir a través del seu índex
feature[i]

# És molt important remarcar l'ús de la iteració sobre els elements (*features*) de les capes vectorials per tal d'accedir i manipular les dades


"""Geometries vectorials"""

# Iterant sobre els elements d'una capa vectorial es pot accedir a les geometries d'aquests elements
features = vlayer.getFeatures()
for feature in features:
  geom = feature.geometry()  

# 


"""Modificació de capes vectorials"""

#
