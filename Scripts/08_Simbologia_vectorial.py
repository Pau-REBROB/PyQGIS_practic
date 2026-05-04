# import


"""Simbologia de capes vectorials"""

# La representació d'una capa vectorial necessita de la definició de símbols associats a la capa, així com d'un renderitzador (*renderer*) que determini el tipus de simbolització que es vol donar

# Els tipus de simbologia - els tipus de renderers - disponibles son les següents
print(QgsApplication.rendererRegistry().renderersList())
# ['nullSymbol', 'singleSymbol', 'categorizedSymbol', 'graduatedSymbol', 'RuleRenderer',
# 'pointDisplacement', 'pointCluster', 'mergedFeatureRenderer', 'invertedPolygonRenderer', 'heatmapRenderer', '25dRenderer', 'embeddedSymbol']

# Per comprovar el renderer vigent d'entre els anteriors possibles en una capa vectorial s'utilitza el mètode `.type()`
vlayer.renderer().type()
#  Amb el mètode `.dump()` es pot conèixer de manera més extensa el tipus de renderitzat d'una capa
vlayer.renderer().dump()
# 'SINGLE: FILL SYMBOL (1 layers) color 141,90,153,255,rgb:0.55294117647058827,0.35294117647058826,0.59999999999999998,1'

# És bon costum guardar el renderitzador en una variable independent
renderer = vlayer.renderer()

# Totes les capes afegides al projecte, tant si estan al canvas com si no, presenten per defecte una simbologia de símbol únic 'singleSymbol', tal i com passa quan s'utilitza la GUI

# Els símbols tenen diferents classes, segons el tipus de simbologia
# La classe utilitzada, que acostuma a guardar-se en la variable `symbol`, s'ha d'entendre com un contenidor de capes de simbologia que es poden anar afegint per a fer la simbologia més rica

## Utilitzant el renderer es pot extreure la simbologia existent d'una capa
symbol = vlayer.renderer().symbol()


"""Simbologia única"""

# És aquella que no depèn de cap variable

# Es pot utilitzar una classe específica per a cada geometria per a crear un objecte símbol totalment buit
## `QgsMarkerSymbol` per punts
## `QgsLineSymbol` per a línies
## `QgsFillSymbol` per a polígons

# Amb el mètode `.defaultSymbol` es crea un objecte de símbol en funció del tipus de geometria de la capa vectorial
symbol = QgsSymbol.defaultSymbol(vlayer.geometryType())
# És recomenable utilitzar aquest constructor i no crear-ne un de totalment buit, ja que així, entre altres coses, queda garantida la compatibilitat amb el renderer i ja té unes propietats assignades per defecte

# Un cop creat l'objecte símbol, es pot modificar al gust
# Existeixen uns mètodes específics per a modificar fàcilment la simbologia que son comuns per totes les geometries
symbol = QgsSymbol.defaultSymbol(vlayer.geometryType())
## Color de fons (*fill color*)
symbol.setColor(QColor("red"))  # nom
symbol.setColor(QColor(255,0,0,150))  # RGBA
## Mida (*size*) - en el cas de capes puntuals
symbol.setSize(5) # size 2 per defecte
## Gruix (*width*) - en el cas de capes lineals
symbol.setWidth(1.5) # width 0.26 píxels per defecte

# Els canvis de simbologia aplicats al constructor del símbol han de ser assignats a la capa vectorial a través del renderer
vlayer.renderer().setSymbol(symbol)
# Finalment, cal refrescar el renderitzat perquè els canvis siguin visibles al canvas
vlayer.triggerRepaint()
# La llegenda del canvas, és a dir, el panell de capes, no actualitza de manera automàtica la simbologia amb la funció anterior
# Cal fer ús de `iface` per indicar que es vol actualitzar el renderitzat de la capa en qüestió
iface.layerTreeView().refreshLayerSymbology(vlayer.id())

# Els mètodes genèrics anteriors de color i gruix son útils quan es vol fer una modificació mínima de la simbologia, però presenten moltes limitacions
# El mètode `.createSimple()` és molt més versàtil ja que conté, en format diccionari, instruccions per a poder modificar:
## Color de fons (*fill color*)
## Color de contorn (*outline color*)
## Gruix (*outline width*)
## Estil de línia (*outline style*)
# Així, per un element poligonal
symbol = QgsFillSymbol.createSimple({
  "color": "red",
  "outline_color": "white",
  "outline_width": 0.75,
  "outline_style": "dash"  # És millor no afegir aquesta opció
})

# Capa base
symbol.symbolLayer(0)
