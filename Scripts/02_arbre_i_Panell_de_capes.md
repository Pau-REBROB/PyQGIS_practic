# Arbre de capes i Panell de capes
Encara que puguin semblar el mateix, l'arbre de capes i el panell de capes d'un projecte de QGIS no son el mateix element.

## Arbre de capes
L'arbre de capes - *layer tree* - és una estructura basada en nodes que recull totes les capes d'un projecte.

S'hi pot accedir a través del mètode `.layerTreeRoot()` de la classe `QgsProject`. ***`root`*** és com es sol anomenar a aquesta estructura.\
`root = project.layerTreeRoot()`

### Contingut de l'arbre de capes
Per accedir als seus nodes - als seus fills, *children* - s'utilitza el mètode `.children()`.\
`root.children()`

El resultat és un llistat de tots els elements que pengen de l'arbre de capes pel seu nom, que son capes o grups de capes.\
`[<QgsLayerTreeLayer: layer_name>, <QgsLayerTreeLayer: layer_name>, ...]`

Es pot realitzar una iteració sobre cada node de l'arbre de capes per a obtenir informació de cada un d'ells.
```
for node in root.children():
  print(node.name())
  # etcètera
```

A través de la seva posició dins l'arbre de capes es pot accedir a un node concret.\
`root.children()[i]`

També s'hi pot accedir a través de l'identificador únic de la capa utilitzant el mètode `.findLayer()`. En aquest cas, com que els identificadors son cadenes de caràcters complicades, s'utilitza el mètode `.findLayerIds()` per generar una llista de tots els identificadors únics de totes les capes del projecte i així poder extreure la posició (o el nom directament) de l'identificador d'interès.
```
ids = root.findLayerIds()
root.findLayer(ids[i])  # o directament l'string identificador
```

Encara que els dos mètodes son equivalents, utilitzar la funció *.children()* és més segura ja que permet accedir a una capa a través del seu nom.

### Addició de capes a l'arbre
L'arbre de capes no només és consultable, sinó que també permet afegir noves capes.

En aquest cas, existeixen dos mètodes diferents:

El mètode `.addLayer()` afegeix la capa a la posició més baixa dins l'arbre (la posició -1).\
`root.addLayer(layer)`

El mètode `.insertLayer()`, en canvi, permet inserir una capa a la posició desitjada dins l'arbre de capes.\
`root.insertLayer(i, layer)`

L'addició de capes a través de l'arbre de capes també afegeix les capes al llenç de QGIS. Ara bé, les capes afegides NO formen part de la instància del projecte i no seran accessibles a través dels seus mètodes com *project.mapLayers()*.

### Grups de capes
A través de l'arbre de capes es poden crear grups de capes.\
`group = root.addGroup("group_name")`

Creat el grup, es poden afegir o inserir capes en el seu interior amb els mateixos dos mètodes d'addició de capes a l'arbre de capes.
```
group.addLayer(layer)
group.insertLayer(i, layer)
```
Si s'utilitza el mètode *.addLayer()*, a diferència de amb l'arbre de capes, la capa afegida al grup es situa a la posició més alta, PER SOBRE de les capes ja existents.

El mètode `.findGroup()` permet cercar un grup de capes per nom a l'arbre de capes.\
`root.findGroup("group_name")`

## Panell de capes
Existeix una relació directa entre l'arbre de capes d'un projecte (*layer tree*) i el panell de capes de la GUI (*table of contents*, TOC).

Totes les capes que s'afegeixen a un projecte a través de la seva instància - `project.addMapLayer()` - son afegides a l'arbre de capes i al panell de capes. Ara bé, tal i com es deia, si s'especifica el segon paràmetre com a *False*, la capa quedarà inclosa a l'arbre de capes, però NO quedarà reflectida en el panell de capes. Aquesta manera de treballar permet manipular les capes i seguir treballant amb el resultat d'una anàlisi aplicada a un conjunt de capes sense necessitat d'estar presents al canvas i, per tant, sense que la renderització afecti al rendiment del projecte. 

A diferència de l'arbre de capes, en el panell de capes cada nova capa que s'afegeix al projecte queda PER SOBRE de les capes ja presents, és a dir, cada nova capa agafa l'índex 0.
