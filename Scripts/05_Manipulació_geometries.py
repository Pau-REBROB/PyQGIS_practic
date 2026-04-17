"""Geometries vectorials"""

#ff
import

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
