# Selecció i filtre d'elements vectorials
## Fent ús de la GUI
Tota selecció o filtratge d'elements de capes vectorials s'ha de realitzar sobre la capa activa del projecte en el supòsit que es treballi des de la GUI de QGIS.

Si les capes del projecte necessàries estan en el llenç i es desitja observar les seleccions i els filtres sobre la interfície gràfica, s'ha de fer ús de *iface* per treballar amb una capa que serà la capa activa del projecte.

Per a determinar la capa activa del projecte, s'utilitza el mètode `.activeLayer()`.\
`iface.activeLayer()`

Per a establir una capa com la capa activa del projecte, en canvi, s'utilitza el mètode `.setActiveLayer()`.\
`iface.setActiveLayer(layer)`

A nivell estètic, per a modificar el color de la selecció en el canvas s'utilitza el mètode `.setSelectionColor()`. Aquest canvi només serà visible mentre es mantingui el projecte obert, ja que no és un canvi permanent.\
`iface.mapCanvas().setSelectionColor(QColor("color"))`

Si es treballa amb scripts de PyQGIS, en canvi, no és necessari establir una capa com a capa activa per a realitzar una selecció o un filtratge.

## Fent ús d'scripts
Utilitzant PyQGIS es poden realitzar seleccions i filtres vectorials sobre qualsevol capa del projecte; els canvis, però, no seran visibles al llenç fins que no s'exportin explícitament com a noves capes del projecte.

### Selecció d'elements
El mètode `.selectAll()` permet seleccionar tots els elements d'una capa vectorial.\
`vlayer.selectAll()`

Com que normalment no es desitjarà seleccionar tots els elements, sinó aquells que compleixin amb alguna condició, es pot utilitzar el mètode `.selectByExpression()` per a seleccionar elements en funció dels seus atributs.
`layer.selectByExpression('expression', behaviour)`

El primer paràmetre és l'expressió de selecció, entre **comes simples**.

El segon paràmetre és el comportament de la selecció. El comportament és un valor de la classe `QgsVectorLayer.SelectionBehavior` que determina com afecta la selecció respecte els elements ja seleccionats:
- QgsVectorLayer.SetSelection (per defecte)
- QgsVectorLayer.AddToSelection
- QgsVectorLayer.RemoveFromSelection
- QgsVectorLayer.IntersectSelection








# La manera habitual de treballar és guardant l'expressió en una variable independent
expr = '"FIELD" < 1000'
## L'expressió es troba escrita entre comes simples (''), però el nom dels camps de la capa entre comes dobles ("")
## Quan es vol utilitzar un atribut de tipus textual, aquest ha d'estar entre comes simples, també, pel que cal fer ús de la barra d'escapament
expr = '"FIELD" = \'Male\''
# Es poden encadenar tantes condicions com es consideri fent ús dels operadors booleans
expr = '"FIELD1" = \'Male\' and "FIELD2" < 100'

# Guardada l'expressió de selecció, es fa ús de la classe `QgsFeatureRequest()` per a crear una petició (*request*) de selecció
request = QgsFeatureRequest().setFilterExpression(expr)
# Amb el mètode `.getFeatures()` s'obtenen els elements d'una capa que compleixen amb la petició
layer.getFeatures(request)

# El *request* és una manera eficient d'accedir a les dades, sense necessitat de seleccionar-les gràficament al canvas i sense alterar la selecció actual 
## Es pot entendre com un filtre de dades
# Un cop obtingudes (que NO seleccionades) les dades que compleixen amb les condicions, es pot treballar amb elles
## Per a treballar amb els elements d'una capa vectorial sempre s'ha de treballar amb els *features*
for feature in layer.getFeatures(request):
  geom = feature.geometry()
  area = geom.area()
  # etc.

# Per a deseleccionar tots els elements, s'utilitza el mètode `.removeSelection()` 
layer.removeSelection()


"""Càlculs sobre seleccions"""

# És habitual voler realitzar càlculs que involucren un o més camps d'una capa sobre un conjunt concret d'elements d'aquesta - o sobre tots
# Realitzat el filtratge d'elements amb un request de `QgsFeatureRequest()`, es poden seguir utilitzant expressions per a avaluar els diferents elements
# Amb la classe `QgsExpression()` es poden crear expressions d'avaluació seguint la mateixa lògica que els *requests*
expr = QgsExpression('"FIELD" > 500')

# Perquè les expressions funcionin necessiten d'un context d'avaluació, que es crea amb un objecte de la classe `QgsExpressionContext()`
# El context global - variables globals, variables del projecte, variables de la capa, SRC, etc. - es carrega al context
context = QgsExpressionContext()
context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))

# Amb l'expressió i el context, es poden avaluar els elements d'una capa vectorial
for feature in layer.getFeatures():
    context.setFeature(feature)
    if expr.evaluate(context):
        # Operacions sobre els features

# Les diferències entre utilitzar una `QgsExpression()` i un request `QgsFeatureRequest().setFilterExpression()` son diverses
## `QgsExpression` fa una avaluació manual feature a feature, client-side - agafa totes les dades del servidor i, en local, retorna les que compleixen les condicions
## `QgsFeatureRequest().setFilterExpression()` fa un filtrat server-side - filtra les dades del servidor i retorna les que compleixen les condicions
# La manera més eficient de treballar és amb un patró híbrid: primer filtrar i després avaluar
request = QgsFeatureRequest().setFilterExpression('"population" > 5000')
expr = QgsExpression('"area" / "population")
for feat in layer.getFeatures(request):
    context.setFeature(feat)
    val = expr.evaluate(context)
    #print(feat.id(), val)


# En el supòsit que no es treballi a la consola Python de QGIS
from qgis.core import (
    QgsVectorLayer,
    QgsFeatureRequest,
    QgsExpression,
    QgsExpressionContext,
    QgsExpressionContextUtils
)

