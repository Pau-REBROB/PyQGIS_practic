# 
from qgis.PyQt.QtCore import QVariant


"""Modificació de capes vectorials"""

# Existeixen diferents metodologies per a modificar els *features* d'una capa vectorial
# Les modificacions d'alt nivell impliquen l'ús del buffer d'edició
# Les modificacions de baix nivell impliquen l'ús del proveïdor de dades


"""Modificacions d'alt nivell"""

# Per crear, actualitzar o suprimir elements en una capa vectorial cal inicialitzar el mode edició de la capa
# La manera més senzilla de fer-ho és amb `with edit()`
with edit(vlayer):
  # create
  # update
  # delete

# Aquest mètode passa pel sistema d'edició de QGIS, de manera que no pot utilitzar-se fora de la GUI
  
# Ja s'ha vist que per llegir els *features* d'una capa cal recórrer a un *for loop* sobre vlayer.getFeatures()

# Per CREAR un nou element, cal crear una instància de la classe `QgsFeature`
# Per donar context a l'element, aquesta instància ha de recopil·lar els camps (*fields*) ja presents a la capa vectorial; La manera més ràpida de fer-ho és amb el mètode `.fields()`
# S'assigna una geometria a l'element amb el mètode `.setGeometry()`
# S'assignen atributs als diferents camps segons convingui
# S'afegeix el *feature* a la capa vectorial amb el mètode `.addFeature()`
with edit(vlayer):
    feat = QgsFeature(vlayer.fields())
    feat.setGeometry(geom)
    feat["FIELD"] = "value" / feat.setAttributes(["FIELD", "value"])
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

# Per ELIMINAR un element existent en una capa vectorial s'utilitza el mètode `.delteFeature()`, especificant el id de l'element desitjat
with edit(vlayer):
    vlayer.deleteFeature(fid)
# Si es desitja eliminar més d'un element, cal passar una llista dels seus identificadors en el mètode `.deleteFeatures()`
with edit(vlayer):
    vlayer.deleteFeatures([fid1, fid2])

# De nou, treballar amb ids pot ser poc pràctic i, de nou, és millor pràctica realitzar una selecció segons atributs dels elements que es volen eliminar
expr = QgsExpression('"codi" = \'12345\'')
request = QgsFeatureRequest(expr)
with edit(vlayer):
  for feat in vlayer.getFeatures(request):
    vlayer.updateFeature(feat.id())

# Si ja hi ha un element seleccionat en el canvas, es pot utilitzar fàcilment el mètode `.deleteSelectedFeatures()`
with edit(vlayer):
    vlayer.deleteSelectedFeatures()

# Per AFEGIR camps s'utilitza el mètode `.addAttributes()`
with edit(vlayer):
  vlayer.addAttributes([QgsField("nou_camp", QVariant.String)])
# Per ELIMINAR camps s'utilitza el mètode `.deleteAttribute()`, especificant el camp a eliminar pel seu índex (només un)
with edit(vlayer):
  vlayer.deleteAttribute(fid)
## Com que pot no ser pràctic conèixer els índex dels diferents camps, és més pràctic treballar amb els seus noms
## Si es crea una llista dels noms dels camps que es volen eliminar, s'utilitza el mètode `.indexFromName()` per trobar-ne l'índex
fields_names_to_delete = ['a', 'b', 'c']
index_to_delete = [vlayer.fields().indexFromName(name) for name in fields_names_to_delete]
## Per aconseguir el contrari, és a dir, voler eliminar tots els camps menys uns en concret, cal generar una llista dels camps a mantenir
## Amb un condicional dins d'una iteració sobre tots els camps de la capa, s'aconsegueix la llista dels índex dels camps a mantenir
fields_names_to_keep = ['d', 'e']
index_to_delete = [
  i for i, field in enumerate(vlayer.fields())
  if field.name() not in fields_names_to_keep
]


# El mètode `with edit()` és realment un *wrapper* del cicle complet del buffer d'edició de QGIS
# El buffer és l'espai temporal on es realitzen les modificacions abans de sobreescriure la font de dades
# Necessita d'explicitar quan s'inicia l'edició de la capa i quan es volen aprovar els canvis com a definitius
vlayer.startEditing()
  # create
  # update
  # delete
vlayer.commitChanges()
# També permet desfer els canvis que s'hagin fet
vlayer.rollBack()

# Amb `with edit()` s'activa el buffer d'edició, s'executen les operacions que hi contingui i fa commit automàtic si tot va bé o rollback si surt un error


"""Modificacions de baix nivell"""

# Les modificacions d'una capa vectorial poden realitzar-se directament sobre la font de dades, sense necessitat de passar pel buffer d'edició de QGIS
# En aquest cas, cal cridar al proveïdor de dades (*data provider*), el connector amb els diferents formats de dades
provider = vlayer.dataProvider()

# El proveïdor de dades permet una edició massiva, directa i més eficient

# Per CREAR nous elements, cal crear una instància de la classe `QgsFeature` i omplir-la de contingut (igual que amb el buffer d'edició)
feat = QgsFeature(vlayer.fields())
feat.setGeometry(geom)
feat["FIELD"] = "value" / feat.setAttributes(["FIELD", "value"])
# Per afegir el nou element a la capa s'utilitza el mètode `.addFeatures()` (en plural, pel que necessita d'una llista de *features*)
provider.addFeatures([feat])

# Per MODIFICAR els atributs dels elements continguts a la capa vectorial es fa ús del mètode `.changeAttributeValues()`
## Aquesta funció necessita d'un diccionari del tipus {FID: {field_index: value}}
## Per cada *feature*, especificat pel seu id (FID), s'indica amb un diccionari quins camps es volen modificar, especificats pel seu índex (field_index), i quin és el nou valor
## La funció, doncs, NO treballa amb noms ni objectes de la classe `QgsFeature`
# Per obtenir l'índex dels camps:
for i, field in enumerate(vlayer.fields()):
    print(i, field.name())
changes = {
  FID1: {idx1: "value", idx2: "value"},
  FID2: {idx1: "value", idx2: "value"}
}
provider.changeAttributeValues(changes)

# Aquesta mateixa metodologia s'utilitza per a modificar les geometries dels elements, no només els seus atributs
# En aquest cas, cal utilitzar el mètode `.changeGeometryValues()`
geom_changes = {
  FID: "new_geom"
}
provider.changeGeometryValues(geom_changes)

# Per ELIMINAR un element existent s'utilitza el mètode `.delteFeatures()`, especificant els ids dels elements desitjats
provider.deleteFeatures([fid])

# Per afegir o eliminar camps, s'utilitzen els mateixos mètodes que amb la metodologia d'alt nivell
# Per AFEGIR camps s'utilitza el mètode `.addAttributes()`
provider.addAttributes([QgsField("nou_camp", QVariant.String)])
vlayer.updateFields()
# Per ELIMINAR camps s'utilitza el mètode `.deleteAttributes()`, especificant el camp a eliminar pel seu índex
provider.deleteAttributes([fid])
vlayer.updateFields()


# És necessari actualitzar manualment l'extensió de la capa vectorial per a visualitzar els canvis que s'hagin fet
vlayer.updateExtents()
vlayer.triggerRepaint()
