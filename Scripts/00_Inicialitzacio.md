# Inicialització d'un projecte
Un *script* de PyQGIS és un *script* en codi Python que pot ser interpretat per QGIS.
QGIS disposa d'una consola Python per importar o executar codi PyQGIS de manera interactiva, però els scripts poden també executar-se fora de l'entorn de QGIS. 

## Importació de mòduls
El mòdul principal per treballar amb PyQGIS és ***core***. Aquest mòdul proporciona les classes fonamentals per crear i treballar amb les dades espacials, gestionar capes i projectes i executar operacions d'anàlisi geoespacial.

`from qgis.core import *`

El mòdul ***utils*** proporciona variables i funcions auxiliars essencialment per treballar amb el canvas de QGIS.

`import qgis.utils`

Si el projecte s'inicia des de la consola Python de QGIS aquestes importacions no seran necessàries, ja que s'executen a l'arrencar el projecte.
```
from qgis.core import *
import qgis.utils
```

## Projectes
### Creació
En el cas que no es treballi directament a la consola Python de QGIS serà sempre necessari importar la classe `QgsProject` per poder gestionar el projecte actiu.

`from qgis.core import QgsProject`

Per manipular el projecte és necessari crear una instància de la classe `QgsProject`. Al ser una classe *singleton* - d'instància única - cal utilitzar el mètode `.instance()`

`project = QgsProject.instance()`

A partir d'ara, s'assumirà que la classe *QgsProject* ha estat sempre cridada i s'ha creat una instància del projecte amb el nom ***project***.

### Manipulació
Per importar un projecte existent de QGIS cal cridar-lo amb el mètode `.read()`.

`project.read("project_filepath/project_name.qgs")`

Per desar els canvis en el projecte, s'utilitza el mètode `.write()`, especificant el directori on es vol guardar el projecte i el seu nom. Si no s'especifica cap ruta, el projecte es guardarà en el mateix directori sota el mateix nom. 

## Flags
Les banderes (*flags*) permeten evitar carregar tot un projecte sencer de QGIS, evitant possibles errors i accelerant el rendiment.

Es declaren amb el mètode `ProjectReadFlags()`.

`readflags = Qgis.ProjectReadFlags()`

Cada flag s'ha de declarar de manera individual amb l'operador `|=`. Alguns exemples son:
- `DontResolveLayers` evita carregar i validar les capes del projecte, útil quan l'interès son les propietats del projecte o els layouts.
- `DontLoadLayouts`evita carregar les composicions del projecte, útil quan aquests son nombrosos o molt pesats.
- `DontLoad3DViews` evita carregar configuracions 3D generades en el projecte, estalviant temps i recursos.
- `DontLoadProjectStyles` evita carregar estils de capes guardats en el projecte, útil quan es vol consultar les capes sense necessitat de la seva estètica.
- `ForceReadOnlyLayers` imposa carregar les capes del projecte únicament en mode lectura, el que evita poder modificar les capes.

Les banderes han de declarar-se amb anterioritat al projecte. Quan aquest s'importa, s'afegeix el paràmetre *readflags* després de la ruta i nom d'importació.
```
readflags |= Qgis.ProjectReadFlag.DontResolveLayers
readflags |= Qgis.ProjectReadFlag.DontLoadLayouts
readflags |= Qgis.ProjectReadFlag.DontLoad3DViews
readflags |= Qgis.ProjectReadFlag.DontLoadProjectStyles
readflags |= Qgis.ProjectReadFlag.ForceReadOnlyLayers

project.read("project_filepath/project_name.qgs, readflags")
```

Les banderes son útils per accelerar i simplificar la visualització d'un projecte, de manera que únicament tenen sentit quan es desitja importar un projecte ja existent, i no quan es crea un projecte de zero.
