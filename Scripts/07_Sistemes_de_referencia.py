# En el supòsit que no es treballi a la consola Python de QGIS
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
)


"""Creació de sistemes de referència de coordenades"""

# Els sistemes de referència de coordenades es troben inscrits dins la classe `QgsCoordinateReferenceSystem`

# Existeixen diferents maneres de generar instàncies d'aquesta classe
## Especificant el SRC amb codi EPSG
crs = QgsCoordinateReferenceSystem('EPSG:25831')

## Especificant el SRC en format WKT
wkt = 'PROJCS["ETRS89 / UTM zone 31N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6258"]], \
PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],PROJECTION["Transverse_Mercator"], \
PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",3],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]], \
AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","25831"]]'
crs =  QgsCoordinateReferenceSystem(wkt)

## Creant un CRS buit, que després és especificat amb el mètode `.createFromX()`
crs = QgsCoordinateReferenceSystem()
crs.createFromProj('')
crs.createFromWkt('')
crs.createFromParameters('')

# Sigui quin sigui el mètode, és bona pràctica comprobar la correcta creació de SRC
print(crs.isValid())


"""Informació dels sistemes de referència de coordenades"""

# Existeixen un seguit de mètodes per a extreure informació sobre una instància de SRC
crs.authid()    # 'EPSG:25831'
crs.description()    # 'ETRS89 / UTM zone 31N'
crs.isGeographic()    # False
crs.toWkt()    # 'PROJCS["ETRS89 / UTM zone 31N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",3],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","25831"]]'
QgsUnitTypes.toString(crs.mapUnits())    # metres

# Per conèixer el sistema de referència associat a una capa s'utilitza el mètode `.crs()`
layer.crs()    # <QgsCoordinateReferenceSystem: EPSG:25831>
# Per obtenir-lo en un format més llegible es pot utilitzar el mètode `.authid()`
layer.crs().authid()    # 'EPSG:25831'


"""Transformacions entre sistemes de referència"""

# Per a transformar una capa en un altre sistema de referència cal, primer, crear una instància del SRC d'origen i de destí
crs_origen = QgsCoordinateReferenceSystem('EPSG:25831')
crs_desti = QgsCoordinateReferenceSystem('EPSG:4326')

# A partir d'aquí, caldrà fer ús de la classe `QgsCoordinateTransform` i el mètode `.transform()`, però es pot procedir de dues maneres
## Amb el mètode més robust, es crea un context de transformació de manera explícita
transform_context = project.transformContext()
xform = QgsCoordinateTransform(crs_origen, crs_desti, transform_context)
geom = xform.transform(old_geom) / geom = old_geom.transform(xform)

## Amb el mètode més ràpid, s'utilitza la instància del projecte per a proporcionar el context de transformació
transform = QgsCoordinateTransform(crs_origen, crs_desti, project)
geom.transform(transform)
