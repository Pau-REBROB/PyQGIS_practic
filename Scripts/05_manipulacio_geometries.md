# Manipulació de geometries vectorials
Les geometries disponibles a QGIS estan representades com a instàncies de la classe `QgsGeometry`, i totes segueixen els estàndards de l'OGC de *Standard Feature Access*.

## Creació de geometries
Es poden generar geometries de tres maneres diferents:

### Creació de geometries a partir de coordenades
Com que totes les geometries deriven d'elements puntuals, es poden utilitzar les coordenades de cada punt que conforma la geometria.

Els objectes tipus punts son de la classe `QgsPointXY`.
```python
from qgis.core import QgsPointXY

pt = QgsPointXY(1,3)
```

Alternativament, es pot utilitzar la classe `QgsPoint`, que permet declarar una dimensió Z i una dimensió M.
```python
from qgis.core import QgsPoint

pt = QgsPointXY(1,3,5)
```

Declarats els punts, es construeix la geometria amb els diferents mètodes `.from--XY()`, en funció del tipus de geometria.
```python
from qgis.core import (
  QgsPointXY,
  QgsGeometry
)

pt = QgsPointXY(1,3)
geom = QgsGeometry.fromPointXY(pt)  # Punts

line = [QgsPointXY(1,3), QgsPointXY(2,4)]  # LLista de punts
geom = QgsGeometry.fromPolylineXY(line)  # Línies

ring = [[QgsPointXY(1,3), QgsPointXY(2,4), QgsPointXY(1,1)]]  # LLista de llista de punts
geom = QgsGeometry.fromPolygonXY(ring)  # Polígons
```

### Creació de geometries a partir de WKT
En aquest cas, s'utilitza el mètode `.fromWKT()` en tots els tipus de geometries.
```python
from qgis.core import QgsGeometry

geom = QgsGeometry.fromWKT("POINT (1 3)")
geom = QgsGeometry.fromWKT("LINESTRING (1 3, 2 4)")
geom = QgsGeometry.fromWKT("POLYGON ((1 3, 2 4, 1 1, 1 3))")  # En aquest cas, cal tancar explícitament el polígon
```

### Creació de geometries a partir de WKB
.....

## Manipulació de geometries
Com s'ha explicat anteriorment, per a accedir a les geometries dels elements d'una capa vectorial és necessari accedir primer al *feature* corresponent; un cop s'ha accedit a l'element, es pot accedir a la pròpia geometria amb el mètode `.geometry()`.

Per conèixer el tipus de geometria que emmagatzema una variable o un *feature* es poden utilitzar diferents mètodes:

El mètode `.wkbType()` retorna 1 per punts, 2 per línies i 3 per polígons.
```python
geom.wkbType()
# <WkbType.Point: 1>
# <WkbType.LineString: 2>
# <WkbType.Polygon: 3>
```

El mètode `.type()` funciona de manera anàloga a l'anterior, però retorna valors de 0-1-2.
```python
geom.type()
# <GeometryType.Point: 0>
# <GeometryType.Line: 1>
# <GeometryType.Polygon: 2>
```

El mètode `.displayString()`, de la classe `QgsWkbTypes`, retorna una geometria en format WKB en un format llegible per humans.
```python
from qgis.core import QgsWkbTypes

QgsWkbTypes.displayString(geom.wkbType())
# 'Point'
# 'LineString'
# 'Polygon'
```

Per conèixer el valor dels diferents vèrtex d'una geometria s'utilitzen els diferents mètodes `.as--()`, segons el tipus de geometria a analitzar. És necessari, doncs, conèixer el tipus de geometria amb anterioritat.
```python
geom.asPoint()
# <QgsPointXY: POINT(1 3)>

geom.asPolyline()
# [<QgsPointXY: POINT(1 3)>, <QgsPointXY: POINT(2 4)>]

geom.asPolygon()
# [[<QgsPointXY: POINT(1 3)>, <QgsPointXY: POINT(2 4)>, <QgsPointXY: POINT(1 1)>, <QgsPointXY: POINT(1 3)>]]
```

## Geometries multipart
vds




"""Geometries multipart"""

# Per saber si una geometria és de tipus multipart es pot utilitzar el mètode `.isMultipart()`, que retorna True o False
geom.isMultipart()

# Generar una geometria multipart implica l'ús dels mètodes específics per a aquest tipus de geometria
## A partir de coordenades
### Multipunt
pt1 = QgsPointXY(1,3)
pt2 = QgsPointXY(2,6)
geom = QgsGeometry.fromMultiPointXY([pt1, pt2])

### Multilínia
pts1 = [QgsPointXY(1,3), QgsPointXY(2,4)]
pts2 = [QgsPointXY(0,1), QgsPointXY(2,2)]
geom = QgsGeometry.fromMultiPolylineXY([pts1, pts2])

### Multipolígon
ring1 = [[QgsPointXY(1,3), QgsPointXY(2,4), QgsPointXY(1,1)]]
ring2 = [[QgsPointXY(0,1), QgsPointXY(2,2), QgsPointXY(5,4)]]
geom = QgsGeometry.fromMultiPolygonXY([ring1, ring2])

## A partir de WKT
geom = QgsGeometry.fromWKT("MULTIPOINT (1 3, 2 4)")
geom = QgsGeometry.fromWKT("MULTILINESTRING ((1 3, 2 4), (0 1, 2 2))")
geom = QgsGeometry.fromWKT("MULTIPOLYGON (((1 3, 2 4, 1 1, 1 3)), ((0 1, 2 2, 5 4, 0 1)))")  # En aquest cas, cal tancar explícitament el polígon


# El mètode `.wkbType()` retorna 4 per multi-punts, 5 per multi-línies i 6 per multi-polígons
geom.wkbType()
# <WkbType.MultiPoint: 4>
# <WkbType.MultiLineString: 5>
# <WkbType.MultiPolygon: 6>

# El mètode `.type()`, en canvi, retorna el mateix resultat que per a les geometries simples: point, line, polygon

## El mètode `.displayString` de la classe `QgsWkbTypes` retorna una geometria en format llegible per humans
QgsWkbTypes.displayString(geom.wkbType())
# 'MultiPoint'
# 'MultiLineString'
# 'MultiPolygon'

# També existeixen els mètodes `.asX()` per conèixer el valor dels diferents vèrtex d'una geometria multipart
geom.asMultiPoint()
# [<QgsPointXY: POINT(1 3)>, <QgsPointXY: POINT(2 4)>]
geom.asMultiPolyline()
# [[<QgsPointXY: POINT(1 3)>, <QgsPointXY: POINT(2 4)>], [<QgsPointXY: POINT(0 1)>, <QgsPointXY: POINT(2 2)>]]
geom.asMultiPolygon()
# [[[<QgsPointXY: POINT(1 3)>, <QgsPointXY: POINT(2 4)>, <QgsPointXY: POINT(1 1)>, <QgsPointXY: POINT(1 3)>]], [[<QgsPointXY: POINT(0 1)>, <QgsPointXY: POINT(2 2)>, <QgsPointXY: POINT(5 4)>, <QgsPointXY: POINT(0 1)>]]]


"""Col·leccions de geometries"""

# Una col·lecció de geometries - o *geometry collection* - és un objecte on es barregen dos o més tipus de geometries bàsiques o multipart
# A QGIS existeix la classe `QgsGeometryCollection`, que permet afegir geometries amb el mètode `.addGeometry()`
## El mètode treballa amb geometries de baix nivell, de manera que s'han de declarar objectes de classe `QgsPoint`, `QgsLineString` o `QgsPolygon`
collection = QgsGeometryCollection()
collection.addGeometry(QgsPointXY(1,3))
collection.addGeometry(QgsLineString([QgsPointXY(0,1), QgsPointXY(2,2)]))
### Amb polígons cal definir l'anell exterior com a *linestring*
ring = QgsLineString([QgsPointXY(2,3), QgsPointXY(2,6), QgsPointXY(3,1), QgsPointXY(2,3)])
polygon = QgsPolygon()
polygon.setExteriorRing(ring)
collection.addGeometry(polygon)
geom = QgsGeometry(collection)

# La forma més senzilla i directa de generar una col·lecció és declarant-la com a WKT i utilitzar la classe `QgsGeometry`
wkt = "GEOMETRYCOLLECTION(POINT(1 3), LINESTRING(0 1, 2 2), POLYGON((2 3, 2 6, 3 1, 2 3)))"
geom = QgsGeometry.fromWkt(wkt)
# QGIS reconeix internament que es tracte d'una col·lecció de geometries encara que no s'utilitzi la seva classe
# <QgsGeometry: GeometryCollection (Point (1 1),LineString (0 0, 2 2),Polygon ((2 3, 2 6, 3 1, 2 3)))>



# En el supòsit que no es treballi a la consola Python de QGIS
from qgis.core import (
  QgsVectorLayer  
  QgsGeometry,
  QgsGeometryCollection,
  QgsPoint,
  QgsPointXY,
  QgsLineString,
  QgsWkbTypes,
  QgsUnitTypes,
)
