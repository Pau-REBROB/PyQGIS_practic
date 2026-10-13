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
Per conèixer si una geometria és de tipus multipart es pot utilitzar el mètode `.isMultipart()`, que retorna *True* o *False*.

Generar una geometria multipart té un procediment anàleg al de les geometries simples, i implica l'ús de mètodes específics per a aquests tipus de geometries.

### Creació de geometries multipart a partir de coordenades
De nou, cal declarar tots els punts que formen part de les geometries a partir de les classes `QgsPoint` o `QgsPointXY`.
```python
from qgis.core import (
  QgsPointXY,
  QgsGeometry
)

# Multipunt
pt1 = QgsPointXY(1,3)
pt2 = QgsPointXY(2,6)
geom = QgsGeometry.fromMultiPointXY([pt1, pt2])

# Multilínia
line1 = [QgsPointXY(1,3), QgsPointXY(2,4)]
line2 = [QgsPointXY(0,1), QgsPointXY(2,2)]
geom = QgsGeometry.fromMultiPolylineXY([line1, line2])

# Multipolígon
ring1 = [[QgsPointXY(1,3), QgsPointXY(2,4), QgsPointXY(1,1)]]
ring2 = [[QgsPointXY(0,1), QgsPointXY(2,2), QgsPointXY(5,4)]]
geom = QgsGeometry.fromMultiPolygonXY([ring1, ring2])
```

## Creació de geometries multipart a partir de WKT
En aquest cas, s'utilitza el mateix mètode `.fromWKT()` per a totes les geometries.
```python
geom = QgsGeometry.fromWKT("MULTIPOINT (1 3, 2 4)")
geom = QgsGeometry.fromWKT("MULTILINESTRING ((1 3, 2 4), (0 1, 2 2))")
geom = QgsGeometry.fromWKT("MULTIPOLYGON (((1 3, 2 4, 1 1, 1 3)), ((0 1, 2 2, 5 4, 0 1)))")  # En aquest cas, cal tancar explícitament el polígon
```

### Manipulació de geometries multipart
Els mètodes de manipulació i consulta son els mateixos que els de les geometries simples.

El mètode `.wkbType()` retorna 4 per multi-punts, 5 per multi-línies i 6 per multi-polígons.
```python
geom.wkbType()
# <WkbType.MultiPoint: 4>
# <WkbType.MultiLineString: 5>
# <WkbType.MultiPolygon: 6>
```

El mètode `.type()`, en canvi, retorna el mateix resultat que per a les geometries simples: point, line, polygon.

El mètode `.displayString` de la classe `QgsWkbTypes` retorna les geometries en forma d'*string* llegible per humans.
```python
from qgis.core import QgsWkbTypes

QgsWkbTypes.displayString(geom.wkbType())
# 'MultiPoint'
# 'MultiLineString'
# 'MultiPolygon'
```

També es poden utilitzar els mètodes `.as--()` per conèixer el valor dels diferents vèrtex d'una geometria multipart.
```python
geom.asMultiPoint()
# [<QgsPointXY: POINT(1 3)>, <QgsPointXY: POINT(2 4)>]
geom.asMultiPolyline()
# [[<QgsPointXY: POINT(1 3)>, <QgsPointXY: POINT(2 4)>], [<QgsPointXY: POINT(0 1)>, <QgsPointXY: POINT(2 2)>]]
geom.asMultiPolygon()
# [[[<QgsPointXY: POINT(1 3)>, <QgsPointXY: POINT(2 4)>, <QgsPointXY: POINT(1 1)>, <QgsPointXY: POINT(1 3)>]], [[<QgsPointXY: POINT(0 1)>, <QgsPointXY: POINT(2 2)>, <QgsPointXY: POINT(5 4)>, <QgsPointXY: POINT(0 1)>]]]
```

## Col·leccions de geometries
Una col·lecció de geometries - *geometry collection* - és un objecte de classe `QgsGeometryCollection` on es barregen dos o més tipus de geometries bàsiques o multipart.

El procediment per generar una col·lecció és primer crear un objecte buit i posteriorment afegir les geometries desitjades amb el mètode `.addGeometry()`; aquest mètode treballa amb geometries de baix nivell que s'han de declarar com objectes de classe `QgsPoint`, `QgsLineString` o `QgsPolygon`.
```python
from qgis.core import (
  QgsGeometryCollection,
  QgsPoint,
  QgsPointXY,
  QgsLineString,
  QgsPolygon
)

collection = QgsGeometryCollection()
collection.addGeometry(QgsPointXY(1,3))
collection.addGeometry(QgsLineString([QgsPointXY(0,1), QgsPointXY(2,2)]))

# En el cas de polígons cal definir l'anell exterior com a linestring
ring = QgsLineString([QgsPointXY(2,3), QgsPointXY(2,6), QgsPointXY(3,1), QgsPointXY(2,3)])
polygon = QgsPolygon()
polygon.setExteriorRing(ring)
collection.addGeometry(polygon)
```

Creada la col·lecció, cal especificar que la nova geometria és el conjunt de totes les geometries individuals.\
`geom = QgsGeometry(collection)`

La forma més senzilla i directa de generar una col·lecció, però, és declarant-la com a WKT i utilitzar la classe `QgsGeometry`.
```python
from qgis.core import QgsGeometry

wkt = "GEOMETRYCOLLECTION(POINT(1 3), LINESTRING(0 1, 2 2), POLYGON((2 3, 2 6, 3 1, 2 3)))"
geom = QgsGeometry.fromWkt(wkt)
# <QgsGeometry: GeometryCollection (Point (1 1),LineString (0 0, 2 2),Polygon ((2 3, 2 6, 3 1, 2 3)))>
```

Amb aquest procediment, QGIS reconeix internament que es tracte d'una col·lecció de geometries encara que no s'utilitzi la seva classe.
