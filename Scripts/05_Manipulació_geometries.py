"""Creació de geometries vectorials"""

# En el supòsit que no es treballi a la consola Python de QGIS
from qgis.core import (
  QgsVectorLayer  
  QgsGeometry,
  QgsGeometryCollection,
  QgsPoint,
  QgsPointXY,
  QgsWkbTypes,
  QgsUnitTypes,
)

# Les geometries disponibles a QGIS estan representades per la classe `QgsGeometry`
# Totes segueixen els estàndards de l'OGC de Standard Feature Access

# Es poden generar geometries de 3 maneres diferents
## A partir de coordenades
### Totes les geometries es construeixen a partir d'objectes tipus punt, de la classe QgsPointXY
pt = QgsPointXY(1,3)
### Alternativament, es pot utilitzar la classe QgsPoint, que permet declarar una dimensió Z i M
pt = QgsPoint(1,3,5)
### Declarats els punts, es construeix la geometria amb els mètodes `.from--XY()`
#### Punts
pt = QgsPointXY(1,3)
geom = QgsGeometry.fromPointXY(pt)
#### Línies
pts = [QgsPointXY(1,3), QgsPointXY(2,4)]  # LLista de punts
geom = QgsGeometry.fromPolylineXY(pts)
#### Polígons
ring = [[QgsPointXY(1,3), QgsPointXY(2,4), QgsPointXY(1,1)]]  # LLista de llista de punts
geom = QgsGeometry.fromPolygonXY(ring)

### Quan els punts es declaren amb més coordenades que X-Y, els mètodes de creació de geometries han d'obviar el XY final

## A partir de WKT
### S'utilitza el mètode `.fromWKT()` en tots els casos
geom = QgsGeometry.fromWKT("POINT (1 3)")
geom = QgsGeometry.fromWKT("LINESTRING (1 3, 2 4)")
geom = QgsGeometry.fromWKT("POLYGON ((1 3, 2 4, 1 1, 1 3))")  # En aquest cas, cal tancar explícitament el polígon

## A partir de WKB


"""Accés a les geometries"""

# Per accedir a una geometria ja s'ha vist que cal iterar sobre els elements (*features*) de la capa vectorial
# Per cada element, es pot accedir a la seva geometria amb el mètode `.geometry()`

# Per conèixer el tipus de geometria que engloba una variable es poden utilitzar diferents mètodes
## El mètode `.wkbType()` retorna 1 per punts, 2 per línies i 3 per polígons
geom.wkbType()
# <WkbType.Point: 1>
# <WkbType.LineString: 2>
# <WkbType.Polygon: 3>

## El mètode `.type()` funciona de manera anàloga a l'anterior, però retorna valors de 0-1-2
geom.type()
# <GeometryType.Point: 0>
# <GeometryType.Line: 1>
# <GeometryType.Polygon: 2>

## El mètode `.displayString`, de la classe `QgsWkbTypes`, retorna una geometria en format llegible per humans
QgsWkbTypes.displayString(geom.wkbType())
# 'Point'
# 'LineString'
# 'Polygon'

# Per conèixer el valor dels diferents vèrtex d'una geometria s'utilitzen els mètodes `.asX()`
# És necessari, llavors, conèixer el tipus de geometria amb anterioritat
geom.asPoint()
# <QgsPointXY: POINT(1 3)>
geom.asPolyline()
# [<QgsPointXY: POINT(1 3)>, <QgsPointXY: POINT(2 4)>]
geom.asPolygon()
# [[<QgsPointXY: POINT(1 3)>, <QgsPointXY: POINT(2 4)>, <QgsPointXY: POINT(1 1)>, <QgsPointXY: POINT(1 3)>]]


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
