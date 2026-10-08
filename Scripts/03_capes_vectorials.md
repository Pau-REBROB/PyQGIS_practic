# Capes vectorials a PyQGIS
Les capes vectorials son una instància de la classe `QgsVectorLayer`.

## Estructura de les capes vectorials: *features*, *fields* i *attributes*
Les capes vectorials estan formades per un conjunt de ***features*** (elements), que son les geometries vectorials individuals continguts a la capa.

Amb el mètode `.getFeatures()` s'accedeix al conjunt d'elements de la capa vectorial.\
`features = vlayer.getFeatures()`

El mètode retorna un llistat de tots els *features* presents, que és un objecte de la classe `QgsFeatureIterator`. Aquest fet condiciona la manera de treballar amb les capes vectorials: sempre s'ha d'iterar sobre el conjunt de features per extreure'n informació o manipular-los; els mètodes no poden aplicar-se mai directament sobre un element, ja que no son accessibles de manera directa.
```
features = vlayer.getFeatures()

for feat in features:
  print("Feature ID: ", feat.id())
  geom = feat.geometry()
  buffer = geom.buffer()
  # etcètera
```

La iteració sobre tots els elements és condició necessària per treballar amb capes vectorials, però un cop començada es pot aïllar el *feature* o *features* d'interès identificant-los pel seu *id* o amb una condició lògica i treballar únicament sobre aquests.
```
features = vlayer.getFeatures()

for feat in features:
  # Determinació de l'àrea de cada element
  area = feat.geometry().area()

  # Filtre d'àrea per valor mínim
  if area > 50:
    buffer = area.buffer()
    # etcètera
```

Cada *feature* conté la informació estructurada en ***fields*** (en camps), que es corresponen amb les columnes de la seva taula d'atributs.

Es pot conèixer el conjunt de camps d'una capa o d'un element amb el mètode `.fields()`; aquest mètode ha d'anar acompanyat del mètode `.names()` per visualitzar els noms dels camps.\
```
vlayer.fields().names()  # camps d'una capa
feature.fields().names()  # camps d'un element
```

El mètode `.typeName()` permet conèixer el tipus de dada que emmagatzema un camp; El tipus de camp és heredat de la font de dades, de manera que no estan estandarditzats dins de QGIS.

La millor manera de conèixer els camps presents a cada capa és utilitzant els mètodes anteriors en un loop.
```
for field in vlayer.fields():
  print(field.name(), field.typeName())
```

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





"""Elements de capes vectorials"""

# En el supòsit que no es treballi a la consola Python de QGIS
import os
from qgis.core import (
  QgsVectorLayer,
  QgsVectorFileWriter
)

# Per a la seva importació, cal especificar:
## Ruta on es troba la capa (*source*)
## Nom que es desitja donar (*layer name*) com a identificador en el panell de capes
## Proveïdor de dades vectorials
vlayer = QgsVectorLayer("Filepath_capa", "Nom_capa", "Proveïdor")


 
# Quan s'importa una capa vectorial, QGIS escull un dels seus camps com a camp de visualització (*display field*)
## El mètode `.displayField()` permet conèixer aquest camp
vlayer.displayField()
## El mètode `.setDisplayExpression()` permet establir un camp o una expressió nova com a camp de visualització
## Al ser una expressió, ha d'estar escrit entre cometes simples
vlayer.setDisplayField('"FIELD"')


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

# El provider *memory*, que emmagatzema la capa temporalment a la RAM, és l'únic que permet crear capes vectorials des de zero
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

# Un cop creada, és més flexible modificar la capa i afegir els camps i les geometries fent ús del *provider* o amb el mode edició de la capa, tal i com es veurà en un altre script

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


"""Exportació de capes vectorials"""

# La classe `QgsVectorFileWriter` permet escriure arxius vectorials en el disc fent ús de `.writeAsVectorFormatV3()`
# La classe suporta tots els formats vectorials que suporta GDAL
# El mètode necessita d'un context de transformació i unes opcions de guardat
QgsVectorFileWriter.writeAsVectorFormatV3(vlayer, "file_path/file_name", transform_context, save_options)

# El context de transformació es pot extreure directament del projecte
transform_context = project.transformContext()
# Amb el context, QGIS aplica automàticament l'encoding, les geometries o el SRC
# Si es necessita d'un control més extens de les opcions de guardat, es poden definir totes les que es necessiti
save_options = QgsVectorFileWriter.SaveVectorOptions()
## Per exemple
save_options.driverName = "ESRI Shapefile"
save_options.fileEncoding = "UTF-8"
save_options.layerName = 'my_new_layer_name'
save_options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer

# Amb l'extensió de sortida de l'arxiu, QGIS inferiex el driver que ha d'utilitzar
