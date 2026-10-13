# Sistemes de referència de coordenades a PyQGIS
## Creació i assignació d'un SRC
Els sistemes de referència de coordenades es troben inscrits dins la classe `QgsCoordinateReferenceSystem`.

Existeixen diferents maneres de generar una instància d'aquesta classe:

La més senzilla és utilitzant el codi EPSG.
```python
from qgis.core import QgsCoordinateReferenceSystem

crs = QgsCoordinateReferenceSystem('EPSG:25831')
```

També es pot utilitzar un format WKT.
```python
from qgis.core import QgsCoordinateReferenceSystem

wkt = 'PROJCS["ETRS89 / UTM zone 31N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6258"]], \
PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],PROJECTION["Transverse_Mercator"], \
PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",3],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]], \
AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","25831"]]'

crs =  QgsCoordinateReferenceSystem(wkt)
```

Si no es coneix quin sistema de referència han de tenir les dades, es pot crear un SRC buit i després omplir-se amb un dels mètodes `.createFrom--()`.
```python
from qgis.core import QgsCoordinateReferenceSystem

crs = QgsCoordinateReferenceSystem()

# Diferent alternatives
crs.createFromProj('')
crs.createFromWkt('')
crs.createFromParameters('')
```

Sigui quin sigui el mètode de creació, és bona pràctica comprovar la correcta creació de SRC abans de seguir amb l'anàlisi espacial.\
`print(crs.isValid())`

Per assignar un sistema de referència a una capa s'utilitza el mètode `.setCrs()`.
`layer.setCrs(crs)`

## Informació del SRC
Per conèixer el sistema de referència associat a una capa s'utilitza el mètode `.crs()`.\
`layer.crs()    # <QgsCoordinateReferenceSystem: EPSG:25831>`

Per obtenir-lo en un format més llegible, es pot afegir el mètode `.authid()`.\
`layer.crs().authid()    # 'EPSG:25831'`

Existeixen un seguit de mètodes per a extreure informació sobre una instància de SRC.
```python
crs.authid()    # 'EPSG:25831'

crs.description()    # 'ETRS89 / UTM zone 31N'

crs.isGeographic()    # False

crs.toWkt()    # 'PROJCS["ETRS89 / UTM zone 31N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",3],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","25831"]]'

from qgis.core import QgsUnitTypes
QgsUnitTypes.toString(crs.mapUnits())    # metres
```

## Transformació entre SRC
Per a transformar una geometria en un altre sistema de referència cal, primer, crear una instància del SRC d'origen i de destí.
```python
crs_origen = QgsCoordinateReferenceSystem('EPSG:25831')
crs_desti = QgsCoordinateReferenceSystem('EPSG:4326')
```

Un cop creades, caldrà fer ús de la classe `QgsCoordinateTransform` i el mètode `.transform()` per aconseguir la transformació. Es pot procedir, però, de dues maneres diferents.

Amb el mètode més robust, es crea un context de transformació de manera explícita.
```python
from qgis.core import QgsCoordinateTransform

transform_context = project.transformContext()
xform = QgsCoordinateTransform(crs_origen, crs_desti, transform_context)

geom = xform.transform(old_geom) / geom = old_geom.transform(xform)
```

Amb el mètode més ràpid, s'utilitza la instància del projecte per a proporcionar el context de transformació.
```python
from qgis.core import QgsCoordinateTransform

transform = QgsCoordinateTransform(crs_origen, crs_desti, project)

geom = old_geom.transform(transform)
```

Aquests dos procediments son vàlids per a transformar coordenades. Les variables *geom* especificades no son objectes de classe *QgsGeometry*, sinó coordenades de la forma *QgsPointXY*.
```python
from qgis.core import QgsCoordinateTransform

crs_origen = QgsCoordinateReferenceSystem('EPSG:25831')
crs_desti = QgsCoordinateReferenceSystem('EPSG:4326')

coords_25831 = QgsPointXY(429482.6,4584386.8)

transform_context = project.transformContext()
xform = QgsCoordinateTransform(crs_origen, crs_desti, transform_context)

coords_4326 = xform.transform(coords_25831)
# <QgsPointXY: POINT(2.15630120301015449 41.40793551458637012)>
```

Per poder transformar les geometries d'una capa sencera cal recórrer els seus *features* individuals. A més, cal guardar els canvis de geometria a la pròpia capa, pel que cal inicialitzar el mode edició.
```python
from qgis.core import QgsCoordinateTransform

# Definició del SRC d'origen i destí
crs_origen = QgsCoordinateReferenceSystem('EPSG:25831')
crs_desti = QgsCoordinateReferenceSystem('EPSG:4326')

# Definició del context de transformació utilitzant el projecte
transform = QgsCoordinateTransform(crs_origen, crs_desti, project)

# Transformació de les geometries
layer.startEditing()

for feature in layer.getFeatures():
    geom = feature.geometry()
    geom.transform(transform)
    layer.changeGeometry(feature.id(), geom)

layer.commitChanges()

# És necessari reassignar el sistema de coordenades a la capa transformada
layer.setCrs(crs_desti)
```

L'alternativa més ràpida i optimitzada és utilitzar el mètode de reprojecció propi de QGIS - *native:reprojectlayer* - fent ús de *processing*.
```python
import processing

result= processing.run("native:reprojectlayer", {
    'INPUT': layer,
    'TARGET_CRS': crs_desti,
    'OUTPUT': 'memory:'
})

reprojected = result['OUTPUT']

project.addMapLayer(reprojected)
```
