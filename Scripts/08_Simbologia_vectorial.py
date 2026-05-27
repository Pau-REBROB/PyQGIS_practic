# import
from qgis.core import (
    QgsSymbol,
    QgsFillSymbol,
    QgsRenderCategory,
    QgsCategorizedSymbolRenderer,
    QgsRendererRange,
    QgsGraduatedSymbolRenderer,
    QgsGradientColorRamp,
    QgsStyle,
    QgsRuleBasedRenderer,
)

from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor



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

# Una manera de poder obtenir un control molt més gran sobre la simbologia única d'una capa és modificant la capa més interna
base_layer = symbol.symbolLayer(0)

# La simbologia cal entendre-la com a un conjunt de capes de simbologia apilades i contingudes en un únic contenidor - el constructor de símbol
# El constructor de la simbologia, segons la geometria, engloba totes les capes de simbologia
# Això permet conèixer quantes capes conté amb el mètode `.symbolLayerCount()` i accedir a les seves capes amb el mètode `.symbolLayer(i)` a través del seu índex 
symbol = QgsSymbol.defaultSymbol(vlayer.geometryType())
symbol.symbolLayerCount()
symbol.symbolLayer(i)
# Com es deia, la capa més interna - la d'índex 0 - és la que més control ofereix en simbologia única, ja que és possible que sigui l'única present
base_layer = symbol.symbolLayer(0)
# Aquest element, i totes les subsegüents capes, és un objecte de classe `QgsSimpleMarkerSymbolLayer`, `QgsSimpleLineSymbolLayer` o `QgsSimpleFillSymbolLayer`, segons el tipus de geometria
# Per sobre d'aquesta, poden existir tantes capes com es desitgi que, a l'igual que amb la GUI, permeten afegir nova simbologia per a crear nous patrons i conjunts de colors
## Quan s'agafa la simbologia d'un renderer ja existent - normalment perquè hem carregat una capa al projecte - la simbologia única fa que només existeixi la capa base
## Si es desitja afegir noves capes de simbologia per sobre, cal crear-les com a objectes individuals de la classe adequada i afegir-les al símbol amb el mètode `.appendSymbolLayer()`
symbol = QgsSymbol.defaultSymbol(vlayer.geometryType())
base_layer = symbol.symbolLayer(0)
layer_1 = symbol.symbolLayer(1)
symbol.appendSymbolLayer(layer_1)
# De manera similar, es pot modificar una capa ja existent i afegida al constructor de símbol amb el mètode `.changeSymbolLayer()`
symbol.changeSymbolLayer(n, layer_n)


# En aquesta capa, existeixen molts més mètodes de modificació de simbologia
## Per a elements PUNTUALS
### Forma (*shape*)
base_layer.setShape(QgsSimpleMarkerSymbolLayerBase.Circle) # Square, Triangle, Cross, Star, Diamond
### Desplaçament (*offset*)
base_layer.setOffset(QPointF(x,y))  # QPointF perquè necessita convertir-ho en tipus *float*
### Inclinació (*angle*)
base_layer.setAngle()

## Per a elements LINEALS
### Patró (*stroke style)
base_layer.setPenStyle(Qt.SolidLine) # DashLine, DotLine, DashDotLine
### Unió entre segments (*join style*)
base_layer.setPenJoinStyle(Qt.RoundJoin) # MiterJoin, BevelJoin
### Final de segment (*cap style*)
base_layer.setPenCapStyle(Qt.RoundCap) # FlatCap, SquareCap 

## Per a elements POLIGONALS
### Color de contorn (*stroke color*)
base_layer.setStrokeColor(QColor())
### Estil de farciment (*brush style*)
base_layer.setBrushStyle(Qt.SolidPattern) # NoBrush, CrossPattern, DiagCrossPattern, HorPattern, VerPattern, BDiagPattern, FDiagPattern
### Estil contorn (*stroke style*)
base_layer.setStrokeStyle(Qt.SolidLine) # Els mateixos patrons Qt que amb els elements lineals
### Unió entre segments
base_layer.setPenJoinStyle(Qt.RoundJoin) # Els mateixos estils Qt que amb els elements lineals 


# Per a crear una simbologia completa cal tenir present totes les propietats que defineixen el símbol, tant segons el tipus de geometria com el tipus de renderitzador
# Aquestes propietats son accessibles a través del mètode `.properties()`
vlayer.renderer().symbol().symbolLayer(i).properties()
# Per exemple:
#{'align_dash_pattern': '0', 'capstyle': 'square', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0', 'customdash_unit': 'MM', 
# 'dash_pattern_offset': '0', 'dash_pattern_offset_map_unit_scale': '3x:0,0,0,0,0,0', 'dash_pattern_offset_unit': 'MM', 'draw_inside_polygon': '0', 'joinstyle': 'bevel',
# 'line_color': '255,158,23,255', 'line_style': 'solid', 'line_width': '0.26', 'line_width_unit': 'MM', 'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM',
# 'ring_filter': '0', 'trim_distance_end': '0', 'trim_distance_end_map_unit_scale': '3x:0,0,0,0,0,0', 'trim_distance_end_unit': 'MM', 'trim_distance_start': '0',
# 'trim_distance_start_map_unit_scale': '3x:0,0,0,0,0,0', 'trim_distance_start_unit': 'MM', 'tweak_dash_pattern_on_corners': '0', 'use_custom_dash': '0', 'width_map_unit_scale': '3x:0,0,0,0,0,0'}

# El mètode `.createSimple()` és molt versàtil ja que conté, en format diccionari, instruccions per a poder modificar totes les propietats anteriors
# A nivell més simple, es pot fer servir el següent diccionari per a modificar:
## Color de farcit (*fill color*)
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



"""Simbologia categòrica"""

# És aquella que està condicionada al valor d'una o més variables categòriques

# Les categories son objectes de la classe `QgsRenderCategory`, on s'ha d'especificar, per a cada categoria
## Valor
## Símbol
## Etiqueta
cat = QgsRenderCategory(value, symbol, label)

# Així, es poden definir totes les categories de manera manual - el que implica crear tots els símbols des de zero
cat_1 = QgsRenderCategory(value_1, symbol_1, label_1)
cat_n = QgsRenderCategory(value_n, symbol_n, label_n)
# Generar el renderitzador buit de la classe específica per a la simbologia categòrica
categorized_renderer = QgsCategorizedSymbolRenderer()
# Assignar cada categoria al renderer, tantes vegades com categories hi hagi
categorized_renderer.addCategory(cat_1)
categorized_renderer.addCategory(cat_n)
# I, finalment, assignar el renderer a la capa
vlayer.setRenderer(categorized_renderer)


# Naturalment, la manera més òptima de treballar és a través d'una iteració amb un *for loop*
# Es decideix el camp el valor del qual determinarà les categories
attribute = 'FIELD'
# Es crea un set amb els valors únics del camp, que seran els que determinaran les diferents categories
attribute_values = set([feat[attribute] for feat in vlayer.getFeatures()])
# Es crea una llista buida que encabirà totes les categories
categories = []
# Es crea un diccionari amb aquells valors de simbologia que es vulguin modificar segons la categoria
symbol_map = {
    "cat_1": {"color": "red", "outline_color": "black", "outline_width": "1.5"},
    "cat_2": {"color": "green", "outline_color": "black", "outline_width": "1.0"},
    "cat_3": {"color": "blue", "outline_color": "black", "outline_width": "0.5"},
}
# Finalment, s'itera per a generar un símbol i una categoria per a cada valor categòric
# Després es fa el renderitzat fora del loop
for cat, props in symbol_map.items():
    symbol = QgsSymbol.defaultSymbol(vlayer.geometryType())
    symbol.createSimple(props)
    cat = QgsRenderCategory(value, symbol, str(value))
    categories.append(cat)
categorized_renderer = QgsCategorizedSymbolRenderer(attribute, categories)
vlayer.setRenderer(categorized_renderer)
vlayer.triggerRepaint()

## Si només es desitja simbolitzar cada categiria amb un color diferent, es pot simplificar el codi declarant una llista de colors
colors = ["red", "green", "blue"]
for value, color in zip(attribute_values, colors):
  col = QColor(color)
  symbol = QgsSymbol.defaultSymbol(vlayer.geometryType()).createSimple({"color": col})
  cat_n = QgsRenderCategory(value, symbol, str(value))
  categories.append(cat_n)
categorized_renderer = QgsCategorizedSymbolRenderer(attribute, categories)
vlayer.setRenderer(categorized_renderer)
vlayer.triggerRepaint()



"""Simbologia graduada"""

# És aquella que utilitza una rampa de color per a representar el rang de valors d'una variable numèrica contínua

# En la simbologia graduada cal tenir present quatre elements:
## Atribut numèric
## Mètode de classificació
## Número de classes (o intervals)
## Rampa de colors

# Les classes son objectes de la classe `QgsRendererRange`, on s'ha d'especificar, per a cada interval de dades
## Rang inferior
## Rang superior
## Símbol
## Etiqueta
range = QgsRendererRange(lower, upper, symbol, label)

# Així, es poden definir totes les classes de manera manual - el que implica crear tots els símbols des de zero
range_1 = QgsRendererRange(lower_1, upper_1, symbol_1, label_1)
range_n = QgsRendererRange(lower_n, upper_n, symbol_n, label_n)
# Generar el renderitzador buit de la classe específica per a la simbologia graduada
graduated_renderer = QgsGraduatedSymbolRenderer()
# Afegir cada rang al renderer, tantes vegades com categories hi hagi
graduated_renderer.addClassRange(range_1)
graduated_renderer.addClassRange(range_n)
# I, finalment, assignar el renderer a la capa
vlayer.setRenderer(graduated_renderer)


# El mètode manual anterior implica l'elecció per part de l'usuari de la variable, la rampa de colors i del mètode de classificació de manera "implícita"
# De manera alternativa, es pot crear un renderer buit i omplir-lo amb el mètode `.createRender()`, que permet homogeneïtzar el resultat
# i escollir el camp, el mètode de classificació i la rampa de colors propis de QGIS
renderer = QgsGraduatedSymbolRenderer.createRenderer(
  vlayer,
  attribute,
  num_classes,
  mode,
  symbol,
  ramp
)
## *mode* és un mètode de classificació de QGIS
## S'assigna amb `QgsGraduatedSymbolRender.mode`, on mode pot ser entre *Quantile*, *Jenks*, *StdDev*, *EqualInterval*, *Pretty*
## *ramp* és la rampa de colors
## Les rampes de colors per defecte de QGIS son accessibles a través de la classe `QgsStyle`
col_ramp = QgsStyle().defaultStyle().colorRamp("color_ramp_name")
## El nom de les rampes de colors és el que es veu a la GUI de QGIS: 'reds', 'blues', 'Magma', 'Viridis', 'RdGy', 'YlOrBr', 'Spectral', etc.
# Amb aquest mètode, es creen el número de classes indicades en funció del mètode especificat i amb la simbologia indicada de manera automàtica


# Si no es volen utilitzar els mètodes de classificació de QGIS i es desitja establir les classes de manera manual, com es veia anteriorment,
# però treballant de manera més eficient, cal fer-ho a través d'una iteració amb un *for loop*
# Es defineixen els intervals de valors
breaks = [0,100,500,1000]
# Es defineixen els colors que s'utilitzaran
colors = ["white", "yellow", "orange", "red", "purple"] # Un valor més que el número d'intervals
# Es crea una llista buida que englobarà tots els rangs de valors
ranges = []
# Finalment, s'itera per cada element de la llista de colors - és a dir, per cada rang
for i in range(len(colors)):
  symbol = QgsSymbol.defaultSymbol(vlayer.geometryType())
  # El símbol es pot fer més complex dins o fora del loop
  symbol.setColor(QColor(colors[i]))
  range = QgsRendererRange(breaks[i], breaks[i+1], symbol, f"{breaks[i]}-{breaks[i+1]}")
  ranges.append(range)
graduated_renderer = QgsGraduatedSymbolRenderer(attribute, ranges)
vlayer.setRenderer(graduated_renderer)
vlayer.triggerRepaint()

# Si es desitja un millor control sobre el color que tindrà cada classe, es pot fer una interpolació d'una rampa de colors
col_ramp = QgsStyle().defaultStyle().colorRamp("color_ramp_name")
col_ramp = QgsGradientColorRamp(QColor("col_inicial"), QColor("color_final"))  # De manera alternativa, es pot crear una rampa definint els dos extrems
breaks = []
num_intervals = len(num_classes)-1 # 4
ranges = []
for i in range(num_intervals):
  symbol = QgsSymbol.defaultSymbol(vlayer.geometryType())
  color = col_ramp.color(float(i)/(num_intervals-1))
  range = QgsRendererRange(breaks[i], breaks[i+1], symbol, f"{breaks[i]}-{breaks[i+1]}")
  ranges.append(range)
graduated_renderer = QgsGraduatedSymbolRenderer(attribute, ranges)
vlayer.setRenderer(graduated_renderer)
vlayer.triggerRepaint()
# El mètode `.color()` permet extreure un color d'una rampa de colors segons la seva posició percentual
## Així, quan i = 0, *float(i)/(num_intervals-1)* - és a dir, t - és també 0, i agafa el color del 0%, és a dir, el color inicial
## Quan i = 3 (el màxim), t = 1 i agafa el color del 100%, és a dir, el color final
## Quan i=1 o i=2, t=0.33 o t=0.66, i el mètode interpola el color corresponent al 33% i 66% de la rampa de color



"""Simbologia basada en regles"""

# És aquella que utilitza una o més condicions per a assignar una simbologia

# A diferència de la resta de simbologies, la simbologia basada en regles no funciona per assignació directa sinó que ha de passar per un arbre de decisions
# Cada *feature* de la capa ha de passar per l'arbre sencer; Si compleix una de les regles, se li aplica la simbologia corresponent i segueix baixant per l'arbre

# L'ordre més adequat per treballar amb simbologia basada en regles és, primerament, definir el constructor del símbol
symbol = QgsSymbol.defaultSymbol(vlayer.geometryType())
# Aquest no és el símbol final, és simplement un valor provisional (*placeholder*) que permet al constructor inicialitzar l'arbre de decisions amb el tipus de geometria correcte

# I després definir totes les regles de simbologia amb la classe `QgsRuleBasedRenderer`
# Amb el mètode `.Rule()` es defineix, per cada regla
## Símbol
## Escala màxima
## Escala mínima
## Expressió
## Etiqueta
## Descripció
## Regla alternativa (*else rule*)
rule = QgsRuleBasedRenderer.Rule(
  symbol,
  maximumScale=10000 # per exemple,
  minimumScale=100000 # per exemple,
  filterExp = '"FIELD"<1000',
  label,
  description,
  elseRule
)
## El símbol serà un clon del constructor definit prèviament `symbol.clone()`
## L'expressió està definida entre comes simples '', amb els camps definits entre comes dobles ""
### És important utilitzar el nom dels arguments de manera explícita, ja que està confirmat que sinó peta QGIS 

# Definides totes les regles, es modifica la simbologia de cada una d'elles amb els mètodes adequats
rule_n.symbol().setColor(QColor()) # per exemple

# Seguidament es pot crear el renderitzador - de la classe `QgsRuleBasedRenderer` - i l'arbre de decisions
rule_renderer = QgsRuleBasedRenderer(symbol)
root_rule = rule_renderer.rootRule()
# Un cop creat l'arbre de decisions, la peça clau d'aquesta simbologia, s'hi poden anar afegint les regles definides anteriorment amb el mètode `.appendChild()`
root_rule.appendChild(rule_n)
## De manera més eficient, es pot definir una llista de regles i afegir-les de manera iterativa a l'arbre de decisions
rules = [rule_1, rule_2, ... rule_n]
for rule in rules:
  root_rule.appendChild(rule)
  
# Fent passar el constructor de símbol pel renderer es crea una regla arrel buida, amb una regla filla per defecte amb el símbol especificat, i les connecta
# A la posició 0 ja existeix una regla creada, doncs
root_rule.children()[0]
## És bona pràctica eliminar aquesta regla que ja existeix, amb el mètode `.removeChildAt()`, ABANS d'afegir noves regles
root_rule.removeChildAt(0)

# Amb totes les regles afegides, s'assigna el renderitzador a la capa vectorial
vlayer.setRenderer(rule_renderer)
vlayer.triggerRepaint()



"""Etiquetatge"""

# L'etiquetatge de les capes vectorials es configura de manera independent a les capes de simbologia
# La classe `QgsPalLayerSettings()` és la que permet configurar els diferents paràmetres referents a les etiquetes
label_settings = QgsPalLayerSettings()

# El mètode `.fieldName()` permet establir el camp que s'utilitza com a etiqueta
label_settings.fieldName = "FIELD"

# El format del text es controla a través d'una classe del mètode `QgsTextFormat`
text_format = QgsTextFormat()
text_format.setFont(QFont("Arial", 10))
text_format.setSize(10)
text_format.setColor(QColor("black"))
# El format cal assignar-lo a la configuració
label_settings.setFormat(text_format)

# Els *buffers* cal crear-los separadament
buffer = QgsTextBufferSettings()
buffer.setEnabled(True)
buffer.setSize(1)
buffer.setColor(QColor("white"))
text_format.setBuffer(buffer)

# La posició de les etiquetes es controla des de la configuració, amb el mètode `.placement`
label_settings.placement = QgsPalLayerSettings.Placement.Horizontal    # AroundPoint, OverPoint, Line, Curved, Perimeter
# Per a desplaçaments manuals (en mm) s'utilitza els mètodes `.MOffset`
label_settings.xOffset = 0.0
label_settings.yOffset = -2.0
# La rotació es controla, en graus, amb el mètode `.angleOffset`
label_settings.angleOffset = 45.0

# Altres mètodes permeten
# Forçar l'etiqueta dins del polígon
label_settings.fitInPolygonOnly = True
# Mostrar totes les etiquetes, encara que se solapin
label_settings.displayAll = True
# Establir la prioritat de l'etiqueta (0-10, on 0 és la més prioritària)
label_settings.priority = 5

# Les línies d'etiqueta - els *callouts* - es generen com a objectes de la classe `QgsCallout`
## `QgsSimpleLineCallout`
## `QgsCurvedLineCallout`
## `QgsManhattanLineCallout`
## `QgsBalloonCallout`
callout = QgsSimpleLineCallout()
# Es pot establir la seva llargada mínima, per defecte en mil·límetres
callout.setMinimumLength(3.0)
callout.setMinimumLengthUnit(QgsUnitTypes.RenderMillimeters)
# Posteriorment, es pot personalitzar la línia del callout
line_symbol = callout.lineSymbol()
line_symbol.setColor(QColor())
line_symbol.setWidth()
# Un cop definit el callout, s'assigna a la configuració d'etiquetes
label_settings.setCallout(callout)
# També cal activar-los explícitament
label_settings.calloutVisibility = QgsCallout.DrawCallouts

# Configurat l'etiquetatge, cal activar-lo explícitament
label_settings.enabled = True

# La configuarció d'etiquetatge s'utilitza per a crear el motor d'etiquetes i assignar-lo a la capa amb el mètode `.setLabeling()`
layer_labels = QgsVectorLayerSimpleLabeling(label_settings)
vlayer.setLabeling(layer_labels)
vlayer.setLabelsEnabled(True)

# Finalment, cal actualitzar el llenç i el panell de capes
vlayer.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(vlayer.id())
