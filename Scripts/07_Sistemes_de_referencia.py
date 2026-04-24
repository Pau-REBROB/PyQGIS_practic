# En el supòsit que no es treballi a la consola Python de QGIS
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
)


"""Sistemes de referència de coordenades"""

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
