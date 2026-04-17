"""Creació de geometries vectorials"""

#ff
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

# Generar una geometria multipart implica l'ús dels mètodes específics per a aquest tipus de geometria
## Multipunt
pt1 = QgsPointXY(1,3)
pt2 = QgsPointXY(2,6)
geom = QgsGeometry.fromMultiPointXY(pt)

## Multilínia
pts1 = [QgsPointXY(1,3), QgsPointXY(2,6)]
pts2 = [QgsPointXY(0,1), QgsPointXY(2,2)]
geom = QgsGeometry.fromMultiPolylineXY([pts1, pts2])

## Multipolígon
ring1 = [[QgsPointXY(1,3), QgsPointXY(2,4), QgsPointXY(1,1)]]
ring2 = [[QgsPointXY(1,3), QgsPointXY(2,4), QgsPointXY(1,1)]]
geom = QgsGeometry.fromMultiPolygonXY(ring)
