# Importació, gestió i tipus de capes
Les capes d'un projecte - tant capes vectorials com capes ràster - poden ser importades des d'una font externa, i en molts formats diferents. En qualsevol cas, serà necessari primer crear una instància del tipus de capa perquè sigui reconeguda per QGIS.

## Importació de capes
Per a declarar una capa vectorial s'utilitza la classe `QgsVectorLayer`, i per una capa ràster s'utilitza la classe `QgsRasterLayer`.

En ambdos casos caldrà especificar:
- La ruta de l'arxiu que conté les dades (*source*).
- El nom que es desitja donar a la capa (*layer name*), com a nom identificatiu en el panell de capes.
- Proveïdor de les dades (*provider*).

```
from qgis.core import (QgsVectorLayer, QgsRasterLayer)

vlayer = QgsVectorLayer("layer_filepath", "layer_name", "provider")
rlayer = QgsRasterLayer("layer_filepath", "layer_name", "provider")
```

En el cas de capes vectorials, el proveïdor principal és ***"ogr"*** de la llibreria GDAL, que suporta gran varietat de formats incloent els Shapefile, GeoJSON, GeoPackage i DXF d'AutoCAD.

En el cas de voler importar un geopackage, cal especificar a la ruta de les dades la capa que es vol importar.\
`vlayer = QgsVectorLayer("Projecte/Dades/dades.gpkg|layername=Aeroports", "Aeroports", "ogr")`

Altres proveïdors disponibles permeten carregar arxius CSV (*"delimitedtext"*), establir connexions WFS (*"WFS"*) o carregar capes des d'un servidor PostgreSQL (*"postgres"*).

En el cas de capes ràster, GDAL és, de nou, el proveïdor que suporta la majoria de formats.\
`rlayer = QgsRasterLayer("GPKG:Projecte/Dades/dades.gpkg:dem", "DEM", "gdal")`

Altres proveïdors disponibles permeten establir connexions WMS (*"wms"*) o carregar capes des d'un servidor PostgreSQL (*"postgresraster"*).

Encara que no estigui estrictament relacionat amb QGIS, si les dades es troben allotjades en local pot ser necessària la importació de la llibreria ***os*** per a la manipulació d'arxius i directoris.\
`import os`

## Addició de capes
La importació d'una capa i la seva declaració en una instància de la classe *QgsVectorLayer* o *QgsRasterLayer* no implica la seva addició al llenç de la interfície de QGIS.

La capa importada - o creada, tot i que la creació in-situ en el mateix script o la mateixa consola Python de QGIS és un procediment que es tractarà més endavant - forma part del projecte, però no del canvas. Per afegir una capa ja importada al llenç cal afegir-la a la instància del projecte utilitzant el mètode `.addMapLayer()`.
```
project.addMapLayer(vlayer)
project.addMapLayer(rlayer)
```

Aquest mètode - declaració de la capa amb una instància QgsVectorLayer/QgsRasterLayer + utilitzar la instància del projecte - és el mètode més indicat per a importar capes a un projecte i afegir-les al llenç.

De manera més ràpida i alternativa, es pot fer ús del mètode `.addVectorLayer()` o `.addRasterLayer()` de la classe `QgsInterface` per a carregar i visualitzar una capa de manera directa.
```
vlayer = iface.addVectorLayer()
rlayer = iface.addRasterLayer()
```

A l'igual que amb el mètode anterior, cal especificar la ruta on es troba la capa (*source*), el nom que es desitja donar (*layer name*) com a identificador en el panell de capes i el proveïdor de dades vectorials o ràster.

Com que *iface* - o QgsInterface - és una instància proporcionada per QGIS que enllaça la GUI amb el codi Python, aquest segon mètode únicament es pot fer servir quan es treballa a la GUI, és a dir, a la consola Python de QGIS.

## Manipulació de capes existents
Què passa quan s'obra un projecte que ja conté totes les capes necessàries carregades? En aquest cas, no es pot accedir a l'objecte que representa cada capa perquè no ha estat declarat pròpiament.

En aquests casos, convé crear un objecte per cada capa continguda en el projecte per tal de poder manipular-la segons convingui.

El mètode `.mapLayers()` retorna un diccionari de les capes presents al projecte. Les claus (*keys*) d'aquest diccionari son els identificadors únics de les capes `.layer.id()`, mentre que els valors (*values*) son els objectes vectorials o ràster (la pròpia capa), que es mostren com a informació referent a la capa: classe, nom i proveïdor - <QgsVectorLayer: 'name' (ogr)>
```
project.mapLayers()  # diccionari de capes
project.mapLayers().keys()  # identificadors de les capes
project.mapLayers().values()  # capes vectorials/ràster
```

Així doncs, per crear un objecte per cada capa present al projecte es pot utilitzar el seu identificador únic (*layer.id()*) o el nom amb què ha estat declarada i que apareix al panell de capes.

L'identificador *id* no és un element que permet relacionar fàcilment amb quina capa s'està tractant, de manera que l'element més indicat és el nom de la capa. Per accedir al nom s'utilitza el mètode `.name()` sobre els valors del diccionari de capes.  
```
for layer in project.mapLayers().values():
  print(layer.name())
```

Modificant aquesta iteració es pot generar un diccionari de capes amb la clau sent el nom de la capa i el valor sent la pròpia capa de classe QgsVectorLayer o QgsRasterLayer.
```
layers = project.mapLayers().values()
layers_dict = {layer.name(): layer for layer in layers}
```

Amb aquest nou diccionari, accedir a una capa és equivalent a accedir a un element d'un diccionari `layers_dict["layer_name"]`. D'aquesta manera, es millora la comprensió i la legibilitat del projecte i l'accés a les capes.

Una altra manera de generar un objecte d'una capa ja present és utilitzant directament el nom que hi figura al panell de capes amb el mètode `.mapLayersByName()`.\
`layer = project.mapLayersByName('layer_name')[0]`

L'índex *[0]* especifica la selecció del primer element que tingui aquest nom.





"""Addició de capes al llenç"""

# Es pot parlar d'un tercer mètode per afegir capes a un projecte
# Si al mètode `.addMapLayer()` s'afegeix el paràmetre *False* en segona posició - corresponent a l'argument *addToLegend* -, la capa s'afegeix al projecte, però no al llenç del mapa
project.addMapLayer(vlayer, False)
# La capa segueix activa dins del projecte, tal i com reflectirà l'arbre de capes (*layer tree*)


"""Manipulació de capes"""

# Les capes que s'importen a un projecte son declarades com a variables utilitzant la classe `QgsVectorLayer` o `QgsRasterLayer`
# A l'existir com a variables, es poden aplicar sobre el nom de la variable els mètodes propis de les classes vectorials i ràster
layer.name()
layer.id()
layer.source()  # etcètera

