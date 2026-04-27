"""Elements de capes vectorials"""

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
# El resultat del mètode és un objecte de classe `QgsFeatureIterator` 
# Aquest fet fa que SEMPRE s'hagi d'iterar sobre el conjunt d'elements d'una capa vectorial per tal de treuer'n informació - no es poden aplicar els mètodes sobre *features*
for feature in features:
  print("Feature ID: ", feature.id())
  geom = feature.geometry()  
  # etcètera

# Cada *feature* conté la informació estructurada en *FIELDS* - en camps, equivalent a les columnes d'una taula de dades
# Es pot conèixer el conjunt de camps d'un element amb el mètode `.fields()`
feature.fields().names()
# El mètode `.typeName()` permet conèixer el tipus de dada que emmagatzema un camp
## El tipus de camp és heredat de la font de dades, de manera que no estan estandarditzats dins de QGIS
# La millor manera de conèixer els camps presents a cada capa és utilitzant els mètodes anteriors en un loop
for field in vlayer.fields():
  print(field.name(), field.typeName())
  
# Quan s'importa una capa vectorial, QGIS escull un dels seus camps com a camp de visualització (*display field*)
## El mètode `.displayField()` permet conèixer aquest camp
vlayer.displayField()
## El mètode `.setDisplayExpression()` permet establir un camp o una expressió nova com a camp de visualització
## Al ser una expressió, ha d'estar escrit entre cometes simples
vlayer.setDisplayField('"FIELD"')

# El valor concret d'un camp (*field*) específic per a un element (*feature*) particular és el seu *ATTRIBUTE*
## Si els features son els registres (files) i els fields son els camps (columnes) d'una taula de dades, els atributs es corresponen amb les cel·les
# Es pot accedir a la informació dels atributs d'un element i un camp concrets a través del nom del camp
feature['nom']
# Alternativament, s'hi pot accedir a través de l'índex del camp
feature[i]
# Per accedir al llistat d'atributs d'un element s'utilitza el mètode `.attributes()`
feature.attributes()
# Totes les maneres per a accedir als atributs d'un element es realitzen en els propis features, NO sobre la capa vectorial

# És molt important remarcar l'ús de la iteració sobre els elements (*features*) de les capes vectorials per tal d'accedir i manipular les dades


"""Accés a geometries vectorials"""

# Iterant sobre els elements d'una capa vectorial es pot accedir a les geometries d'aquests elements amb el mètode `.geometry()`
# Amb les geometries disponibles, es poden aplicar predicats - intersects, within, equals, etc. - i operacions espacials - unió, envolvent, àrea, buffer, etc. - sobre elles
features = vlayer.getFeatures()
for feature in features:
  geom = feature.geometry()
  area = geom.area()
  perim = geom.length()
  print(f"Àrea de l'element: {area}; Perímetre de l'element: {perim}")


"""Índex espacials"""

# És sabuda la importància dels índex espacials en els processos d'anàlisi i manipulació de geometries
# Existeixen dues maneres de generar índex espacials
## Es poden guardar en memòria en un objecte manipulable, que haurà de ser cridat en les operacions espacials en el lloc de la pròpia capa vectorial
index = QgsSpatialIndex(vlayer.getFeatures())
## Es poden modificar les dades originals generant-hi un índex espacial, que és persistent
vlayer.dataProvider().createSpatialIndex()


"""Creació de capes vectorials"""

# La manera de crear una capa vectorial més habitual és utilitzant, de nou, una instància de `QgsVectorLayer`
vlayer = QgsVectorLayer("Geometry_type?crs&field1&field2&index", "layer_name", "memory")

# El provider *memory* és l'únic que permet crear capes vectorials des de zero
# La resta de proveïdors necessiten que les dades estiguin físicament guardades en algun lloc

# La definició de la capa ha d'incorporar, en un URI
## Tipus de geometria: "Point","LineString","Polygon","MultiPoint","MultiLineString","MultiPolygon" o "None"
## SRC definit de qualsevol de les maneres acceptades per QgsCoordinateReferenceSystem.createFromString(): crs=epsg:25831
## Camps, que han de tenir un nom i, opcionalment, el tipus de dada que suporta - string, integer, double - amb la seva longitud i precisió: field=id:integer(10)
## Índex, per especificar si es crearan índex espacials: index=yes
vlayer = QgsVectorLayer("Polygon?crs=epsg:25831&field=id:integer(10)&field=barri:string(50)&index=yes", "temporary_polygons", "memory")


"""Modificació de capes vectorials"""

# Tot i que es poden crear capes vectorials des de zero amb tots els camps desitjats amb el proveïdor de memòria, la pràctica habitual és crear una capa amb la informació mínima
vlayer = QgsVectorLayer("Polygon?crs=epsg:25831", "layer_name", "memory")

# Un cop creada, és més flexible modificar la capa i afegir els camps i les geometries fent ús del *provider*
provider = vlayer.dataProvider()

# Es poden conèixer les possibilitats de manipulació d'una capa vectorial amb el mètode `.capabilitiesString()`
vlayer.dataProvider().capabilitiesString()
## 'Afegeix objectes
## Suprimeix objectes
## Canvia els valors dels atributs
## Afegeix atributs
## Suprimeix els atributs
## Canvia els noms dels atributs
## Fast Access to Features at ID
## Canvia geometries'
## etc.

# Un cop creada o importada una capa vectorial, existeixen diferents maneres de modificar els *features*, que es veuran en un altre script
