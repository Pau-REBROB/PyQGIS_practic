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
# És necessari actualitzar manualment l'extensió de la capa vectorial per a visualitzar els canvis
provider.addFeatures([feat])
vlayer.updateExtents()

# Per MODIFICAR

# Per ELIMINAR un element existent s'utilitza el mètode `.delteFeatures()`, especificant els ids dels elements desitjats
provider.deleteFeatures([fid])
