"""Caixa d'eines de QGIS"""

# Totes les funcions i algoritmes presents a la caixa d'eines de QGIS son accessibles des de PyQGIS a través del mòdul `processing`
from qgis import processing

# Per utilitzar alguna de les funcions de la caixa d'eines, cal cridar el mètode `.run()` sobre *processing*
processing.run("native:algorithm_name", {dict_of_parameters})
## El primer argument és el nom ORIGINAL de la funció
### Les funcions pròpies de QGIS comencen totes amb "native:"
## El segon argument és un diccionari de paràmetres, propis de la funció que es vol utilitzar
### Els paràmetres concrets d'una funció específica poden no ser coneguts a priori. El mètode `.algorithmHelp()` retorna informació sobre la funció, incloent els paràmetres
processing.algorithmHelp("native:algorithm_name")

## Els paràmetres que segur que existiran en totes les funcions son 'INPUT' i 'OUTPUT'
### 'INPUT' fa referència a la capa - o elements d'una capa - sobre la que vol aplicar-se la funció
### 'OUTPUT' fa referència a el resultat de la funció, que serà "memory:" si es desitja que sigui un arxiu temporal, o la ruta completa de l'arxiu si es desitja guardar en local

# La manera habitual de treballar és guardar el resultat de la funció en una variable, i utilitzar el seu 'OUTPUT' per a afegir-la al canvas de QGIS
result = processing.run("algorith_id", {params})
project.addMapLayer(result['OUTPUT'])
# Això implica que el resultat de *processing* és sempre un diccionari



"""Noves eines de processament"""

#
