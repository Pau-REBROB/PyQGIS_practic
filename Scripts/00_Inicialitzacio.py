"""Execució implícita quan s'inicialitza la consola Python de QGIS"""
from qgis.core import *
import qgis.utils


# En el supòsit que no es treballi a la consola Python de QGIS
from qgis.core import QgsProject

# Sempre és necessari crear una instància de la classe `QgsProject`
## Al ser una classe *singleton* - és a dir, d'instància única - cal utilitzar el mètode `.instance()`
project = QgsProject.instance()

# Si es vol importar un projecte existent a l'aplicatiu de QGIS en blanc, cal cridar-lo amb el mètode `.read()`
project.read("Filepath_projecte/Nom_projecte.qgs")
# Per desar els canvis en el projecte, s'utilitza el mètode `.write()`
## Si no s'especifica cap ruta, el projecte es guardarà en el mateix directori sota el mateix nom
## Si es fa passar una ruta diferent com a argument, el projecte es guardarà en un nou directori i/o amb un nom diferent  
project.write()


# Les banderes (*flags*) permeten evitar carregar tot un projecte sencer de QGIS, evitant errors i accelerant el rendiment
# Es declaren amb el mètode `ProjectReadFlags()`
readflags = Qgis.ProjectReadFlags()
# Cada flag que es vol afegir ha de ser amb l'operador `|=`
## `DontResolveLayers` evita carregar i validar les capes del projecte, útil quan l'interès son les propietats del projecte o els layouts
readflags |= Qgis.ProjectReadFlag.DontResolveLayers
## `DontLoadLayouts`evita carregar les composicions del projecte, útil quan aquests son nombrosos o molt pesants
readflags |= Qgis.ProjectReadFlag.DontLoadLayouts
## `DontLoad3DViews` evita carregar configuracions 3D generades en el projecte, estalviant temps i recursos
readflags |= Qgis.ProjectReadFlag.DontLoad3DViews
## `DontLoadProjectStyles` evita carregar estils de capes guardats en el projecte, útil quan es vol consultar les capes sense necessitat de la seva estètica
readflags |= Qgis.ProjectReadFlag.DontLoadProjectStyles
## `ForceReadOnlyLayers` imposa carregar les capes del projecte únicament en mode lectura, el que evita poder modificar les capes
readflags |= Qgis.ProjectReadFlag.ForceReadOnlyLayers

# Les banderes han de declarar-se amb anterioritat al projecte
# Només tenen sentit quan es desitja importar un projecte ja existent, i no quan es crea un projecte de zero
project.read("Filepath_projecte/Nom_projecte.qgs", readflags)
