# Arbre de capes i Panell de capes
Encara que puguin semblar el mateix, l'arbre de capes i el panell de capes d'un projecte de QGIS no son el mateix element.

## Arbre de capes
L'arbre de capes - *layer tree* - és una estructura basada en nodes que recull totes les capes d'un projecte.

S'hi pot accedir a través del mètode `.layerTreeRoot()` de la classe `QgsProject`. ***`root`*** és com es sol anomenar a aquesta estructura.\
`root = project.layerTreeRoot()`

Per accedir als seus nodes - als seus fills, *children* - s'utilitza el mètode `.children()`.\
`root.children()`

El resultat és un llistat de tots els elements que pengen de l'arbre de capes pel seu nom, que son capes o grups de capes.\
`[<QgsLayerTreeLayer: layer_name>, <QgsLayerTreeLayer: layer_name>, ...]`

Es pot accedir a un node concret de l'arbre de capes a través de la seva posició dins l'arbre.\
`root.children()[i]`

També s'hi pot accedir a través de l'identificador únic de la capa utilitzant el mètode `.findLayer()`. En aquest cas, com que els identificadors son cadenes de caràcters complicades, s'utilitza el mètode `.findLayerIds()` per generar una llista de tots els identificadors únics de totes les capes del projecte i així poder extreure la posició (o el nom directament) de l'identificador d'interès.
```
ids = root.findLayerIds()
root.findLayer(ids[i])  # o directament l'string identificador
```

Encara que els dos mètodes son equivalents, utilitzar la funció *.children()* és més segura ja que permet accedir a una capa a través del seu nom.




"""Arbre de capes"""

# Cada nova capa que s'afegeix al projecte queda PER SOBRE de les capes ja presents, és a dir, cada nova capa agafa l'índex 0
# També a través del seu identificador únic
ids = root.findLayerIds()  # Llistat dels ids de totes les capes presents 
root.findLayer(ids[i])

# Es pot iterar sobre cada node de l'arbre de capes per a obtenir informació de cada un d'ells
for node in root.children():
  print(node.name())
  print(node.id())

# L'arbre de capes també permet afegir noves capes
# En aquest cas, existeixen dos mètodes diferents
## El mètode `.addLayer()` afegeix la capa a la posició més baixa dins l'arbre (la posició -1)
root.addLayer(layer)
## El mètode `.insertLayer()`, en canvi, permet inserir una capa a la posició desitjada dins l'arbre de capes
root.insertLayer(i, layer)
# L'addició de capes a través de l'arbre de capes afegeix les capes al llenç de QGIS
# Les capes afegides, però, NO formen part de la instància del projecte
project.mapLayers()  # El mètode NO reconeix les capes afegides a través de `root`


"""Grups de capes"""

# A través de l'arbre de capes es poden crear grups de capes
group = root.addGroup("Nom_grup")

# Creat un grup, es poden afegir o inserir capes en el seu interior
group.addLayer(layer)
# En aquest cas, la capa afegida grup es situa a la posició més alta, PER SOBRE de les capes ja existents
group.insertLayer(i, layer)

# El mètode `findGroup` permet cercar un grup de capes per nom a l'arbre de capes
root.findGroup("Nom_grup")


"""Panell de capes"""

# Existeix una relació directa entre l'arbre de capes d'un projecte (*layer tree*) i el panell de capes de la GUI (*table of contents*, TOC)
# Totes les capes que s'afegeixen a un projecte a través de la seva instància - `project.addMapLayer()` - son afegides a l'arbre de capes i al panell de capes
## Si s'especifica el segon paràmetre com a *False*, la capa està inclosa a l'arbre de capes, però NO queda reflectida en el panell de capes
# Quan una capa s'afegeix al projecte directament des de `root`, la capa queda afegida al panell de capes però NO consta a l'arbre de capes com una capa del projecte
