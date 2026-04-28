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

# Totes les capes afegides al projecte, tant si estan al canvas com si no, presenten per defecte una simbologia de símbol únic: 'singleSymbol'

# Els símbols tenen diferents classes, segons el tipus de simbologia
# La classe utilitzada, que acostuma a guardar-se en la variable `symbol`, s'ha d'entendre com un contenidor de capes de simbologia que es poden anar afegint per a fer la simbologia més rica

## Utilitzant el renderer es pot extreure la simbologia existent d'una capa
symbol = vlayer.renderer().symbol()


"""Simbologia única"""

# És aquella que no depèn de cap variable

# Amb el mètode `.defaultSymbol` es crea un objecte de símbol en funció del tipus de geometria de la capa vectorial
symbol = QgsSymbol.defaultSymbol(vlayer.geometryType())

# Si ja es coneix el tipus de geometria que conté la capa, es pot utilitzar una classe específica per a aquella geometria
## `QgsMarkerSymbol` per punts
## `QgsLineSymbol` per a línies
## `QgsFillSymbol` per a polígons

# Un cop creat l'objecte símbol, es pot modificar al gust
# Cada una de les classes conté mètodes específics per a modificar diferents aspectes de la simbologia

## Capes PUNTUALS
symbol = QgsMarkerSymbol()
# Color de fons (*fill color*)
symbol.setColor(QColor("red"))  # nom
symbol.setColor(QColor(255,0,0,150))  # RGBA
# Mida (*size*)
symbol.setSize(5) # size 2 per defecte

## Capes LINEALS
symbol = QgsLineSymbol()
# Color (*fill color*)
symbol.setColor(QColor("green"))  # nom
symbol.setColor(QColor(0,255,0,150))  # RGBA
# Gruix (*width*)
symbol.setWidth(0.5) # width 0.26 píxels per defecte







