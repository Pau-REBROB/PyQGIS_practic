"""Elements de capes vectorials"""

# En el supòsit que no es treballi a la consola Python de QGIS
import os
from qgis.core import QgsVectorLayer

# Les capes vectorials son una instància de la classe `QgsVectorLayer`
# Per a la seva importació, cal especificar:
## Ruta on es troba la capa (*source*)
## Nom que es desitja donar (*layer name*) com a identificador en el panell de capes
## Proveïdor de dades vectorials
vlayer = QgsVectorLayer("Filepath_capa", "Nom_capa", "Proveïdor")

# Les capes vectorials estan formades per un conjunt de *FEATURES*, que representen elements individuals dins la capa (les geometries vectorials)
# S'accedeix al conjunt de *features* d'una capa vectorial a través del mètode `.getFeatures()`, que retorna els elements en format llista 
features = vlayer.getFeatures()
# El resultat del mètode és un objecte de classe `QgsFeatureIterator` 
# Aquest fet fa que SEMPRE s'hagi d'iterar sobre el conjunt d'elements d'una capa vectorial per tal de treuer'n informació - no es poden aplicar els mètodes sobre *features*
for feature in features:
  print("Feature ID: ", feature.id())
  geom = feature.geometry()  
  # etcètera

# Cada *feature* conté la informació estructurada en *FIELDS* - en camps, equivalent a les columnes d'una taula de dades
# Es pot conèixer el conjunt de camps d'un element amb el mètode `.fields()`
feature.fields().names()
# El mètode `.typeName()` permet conèixer el tipus de dada que emmagatzema un camp
## El tipus de camp és heredat de la font de dades, de manera que no estan estandarditzats dins de QGIS
# La millor manera de conèixer els camps presents a cada capa és utilitzant els mètodes anteriors en un loop
for field in vlayer.fields():
  print(field.name(), field.typeName())
  
# Quan s'importa una capa vectorial, QGIS escull un dels seus camps com a camp de visualització (*display field*)
## El mètode `.displayField()` permet conèixer aquest camp
vlayer.displayField()
## El mètode `.setDisplayExpression()` permet establir un camp o una expressió nova com a camp de visualització
## Al ser una expressió, ha d'estar escrit entre cometes simples
vlayer.setDisplayField('"FIELD"')

# El valor concret d'un camp (*field*) específic per a un element (*feature*) particular és el seu *ATTRIBUTE*
## Si els features son els registres (files) i els fields son els camps (columnes) d'una taula de dades, els atributs es corresponen amb les cel·les
# Es pot accedir a la informació dels atributs d'un element i un camp concrets a través del nom del camp
feature['nom']
# Alternativament, s'hi pot accedir a través de l'índex del camp
feature[i]
# Per accedir al llistat d'atributs d'un element s'utilitza el mètode `.attributes()`
feature.attributes()
# Totes les maneres per a accedir als atributs d'un element es realitzen en els propis features, NO sobre la capa vectorial

# És molt important remarcar l'ús de la iteració sobre els elements (*features*) de les capes vectorials per tal d'accedir i manipular les dades


"""Accés a geometries vectorials"""

# Iterant sobre els elements d'una capa vectorial es pot accedir a les geometries d'aquests elements amb el mètode `.geometry()`
# Amb les geometries disponibles, es poden aplicar predicats - intersects, within, equals, etc. - i operacions espacials - unió, envolvent, àrea, buffer, etc. - sobre elles
features = vlayer.getFeatures()
for feature in features:
  geom = feature.geometry()
  area = geom.area()
  perim = geom.length()
  print(f"Àrea de l'element: {area}; Perímetre de l'element: {perim}")


"""Índex espacials"""

# És sabuda la importància dels índex espacials en els processos d'anàlisi i manipulació de geometries
# Existeixen dues maneres de generar índex espacials
## Es poden guardar en memòria en un objecte manipulable, que haurà de ser cridat en les operacions espacials en el lloc de la pròpia capa vectorial
index = QgsSpatialIndex(vlayer.getFeatures())
## Es poden modificar les dades originals generant-hi un índex espacial, que és persistent
vlayer.dataProvider().createSpatialIndex()


"""Modificació de capes vectorials"""

# Es poden conèixer les possibilitats de manipulació d'una capa vectorial amb el mètode `.capabilitiesString()`
vlayer.dataProvider().capabilitiesString()
## 'Afegeix objectes
## Suprimeix objectes
## Canvia els valors dels atributs
## Afegeix atributs
## Suprimeix els atributs
## Canvia els noms dels atributs
## Fast Access to Features at ID
## Canvia geometries'

# Ja s'ha vist que per llegir els *features* d'una capa cal recórrer a un *for loop* sobre vlayer.getFeatures()

# Per crear, actualitzar o suprimir elements en una capa vectorial cal inicialitzar el mode edició de la capa
with edit(vlayer):
  # create
  # update
  # delete

# Per CREAR un nou element, cal crear una instància de la classe `QgsFeature`
# Per donar context a l'element, aquesta instància ha de recopil·lar els camps (*fields*) ja presents a la capa vectorial; La manera més ràpida de fer-ho és amb el mètode `.fields()`
# S'assigna una geometria a l'element amb el mètode `.setGeometry()`
# S'assignen atributs als diferents camps segons convingui
# S'afegeix el *feature* a la capa vectorial amb el mètode `.addFeature()`
with edit(vlayer):
    feat = QgsFeature(vlayer.fields())
    feat.setGeometry(geom)
    feat["FIELD"] = "value"
    vlayer.addFeature(feat)

# Per MODIFICAR un element existent d'una capa vectorial primer cal llegir-ne els seus elements amb un *for loop*
# Es busca l'element d'interès a partir del seu id - o de qualsevol atribut identificatiu únic - afegint un condicional
# Trobat l'element, es modifica l'atribut desitjat del camp desitjat
# Finalment, es fan permanents els canvis amb el mètode `.updateFeature()`
with edit(vlayer):
    for feat in vlayer.getFeatures():
        if feat.id() == "value":
            feat["FIELD"] = "other value"
            vlayer.updateFeature(feat)

# Una manera més eficient de buscar l'element que es vol modificar és realitzant una selecció vectorial - que es veurà més endavant
# D'aquesta manera, s'evita recórrer tots els *features* de la capa
expr = QgsExpression('"codi" = \'12345\'')
request = QgsFeatureRequest(expr)
with edit(vlayer):
  for feat in vlayer.getFeatures(request):
    feat["FIELD"] = "other value"
    vlayer.updateFeature(feat)

#ELIMINAR
with edit(layer):
    layer.deleteFeature(10)
