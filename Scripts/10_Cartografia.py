"""Generació i exportació de cartografia"""

# La classe central per al disseny de mapes - el que s'anomena *layouts* - és la classe `QgsLayout`

# Es comença creant una instància d'aquesta classe que, seguidament, cal inicialitzar
layout = QgsPrintLayout(project)
layout.initializeDefaults()

# La inicialització per defecte crea un disseny amb una configuració predeterminada, com que sigui un DIN A4 blanc horitzontal

# El nom del *layout* es configura amb el mètode `.setName()`
layout.setName("layout_name")


# Elements de la composició
# Tots els elements que s'afegeixin a la composició estan representats per classes que hereden de la classe base `QgsLayoutItem`
# Un cop definits, s'afegeixen a la composició amb el mètode `.addLayoutItem()`
layout.addLayoutItem(item)

## Mapa
# La classe `QgsLayoutItemMap` afegeix un mapa buit, sense mida ni posició
map = QgsLayoutItemMap(layout)
# Per defecte, `QgsLayoutItemMap` agafarà totes les capes visibles del canvas
# Es poden definir explícitament les capes que ha de mostrar la composició amb el mètode `.setLayers()`
map.setLayers([vlayer_1, vlayer_2, vlayer_3])
map.setKeepLayerSet(True)

# Per defecte, la mida del mapa és 0x0 i es situa a la posició (0,0)
# Per a redimensionar-lo, s'utilitza el mètode `.attemptResize()`
map.attemptResize(QgsLayoutSize(x,y,units))
# Per a posicionar-lo, s'utilitza el mètode `.attemptMove()`
map.attemptMove(QgsLayoutPoint(x,y,units))
## Les unitats (*units*) de mida i posició son variables tipus `QgsUnitTypes.LayoutMillimeters` o `QgsUnitTypes.LayoutPixels`

# Per a establir una extensió, s'utilitza algun dels diferents mètodes següents 
## Es pot seleccionar l'extensió d'una capa del mapa amb `layer.extent()`
## Es pot seleccionar l'extensió actual del canvas amb `iface.mapCanvas().extent()`
## Es pot definir manualment amb `QgsRectangle(xmin, ymin, xmax, ymax)`
# Establerta l'extensió, s'assigna al mapa amb el mètode `.setExtent()` i, posteriorment, cal forçar la seva renderització 
map.setExtent(extent)
map.zoomToExtent(extent)

# A vegades pot ser necessari augmentar l'extensió del mapa, si aquest queda tallat en la composició final, per exemple
# El mètode `.grow()` expandeix l'extensió en totes les direccions segons el valor indicat
extent = vlayer.extent()
margin = extent.width() * 0.05  # Marge del 5%
extent.grow(margin)

# Finalment, s'afegeix el mapa a la composició
layout.addLayoutItem(map)

## Llegenda
# La classe `QgsLayoutItemLegend` afegeix una llegenda buida
legend = QgsLayoutItemLegend(layout)

# La llegenda es vincula al mapa a través del mètode `.setLinkedMap()`
legend.setLinkedMap(map)

# La mida i posició s'ajusten de la mateixa manera que en el cas del mapa
legend.attemptResize(QgsLayoutSize(x,y,units))
legend.attemptMove(QgsLayoutPoint(x,y,units))

# El títol s'estableix amb el mètode `.setTitle()`
legend.setTitle("legend title")

# Per tal que la llegenda s'actualitzi automàticament amb el contingut del mapa, cal especificar-ho amb el mètode `.setAutoUpdateModel()` com a *True*
legend.setAutoUpdateModel(True) 

# Finalment, s'afegeix la llegenda a la composició
layout.addLayoutItem(legend)

## Barra d'escala
# La classe `QgsLayoutItemScaleBar` afegeix una barra d'escala
scale = QgsLayoutItemScaleBar(layout)

# De nou, cal fer una vinculació al mapa a través del mètode `.setLinkedMap()`
scale.setLinkedMap(map)

# La mida i posició s'ajusten de la mateixa manera que en el cas del mapa
scale.attemptResize(QgsLayoutSize(x,y,units))
scale.attemptMove(QgsLayoutPoint(x,y,units))
# En aquest cas, existeix també el mètode de mida per defecte
scale.applyDefaultSize()

# L'estil de la barra d'escala es controla amb el mètode `.setStyle()`, sent per defecte *Numeric*
scale.setStyle("Numeric")   # "Line Ticks Up", "Double Box", "Single Box"

# Finalment, s'afegeix l'escala a la composició
layout.addLayoutItem(scale)


# Per a qualsevol element, la seva posició per defecte és la (0,0), corresponent a la cantonada superior esquerra del canvas
# Per tant, valors de X superiors centren verticalment l'element
# Mentre que, valors de Y superiors centren l'element horitzontalment


# Una composició pot tenir més d'una pàgina
# Les pàgines es gestionen des de la col·lecció de pàgines (*page collection*) de la composició
pc = layout.pageCollection()

# Les pàgines s'han de gestionar com a objectes individuals - son objectes de la classe `QgsLayoutItemPage`
page = QgsLayoutItemPage(layout)
# Existeixen diferents mètodes per a configurar les pàgines
## Mida i orientació de la pàgina
page.setPageSize("name", orientation)
## La mida ha de ser el nom del format - "A3", "A4", etc.
## L'orientació és una variable del tipus `QgsLayoutItemPage.Landscape` o `QgsLayoutItemPage.Portrait`
# De manera alternativa, es pot utilitzar `QgsLayoutSize` per a personalitzar la mida de la pàgina
page.setPageSize(QgsLayoutSize(x,y,units))
# Mètodes de consulta de mida i orientació
page.setSize()
page.orientation()  # No existeix un mètode directe per a establir l'orientació
# Color de fons de la pàgina
page.setPageStyleSymbol(QgsFillSymbol.createSimple({"color": "white"}))

# Per moure's per dins la col·lecció de pàgines cal fer ús dels seus índex posicionals
pc.page(i)
# Per afegir noves pàgines es fa ús del mètode `.addPage()`
# La pàgina sempre s'afegeix a l'última posició
pc.addPage(page)
# Per eliminar pàgines es fa ús del mètode `.deletePage()`, indicant l'índex de la pàgina dins la col·lecció
pc.deletePage(i)
# Per a eliminar totes les pàgines, es fa ús del mètode `.clear()`
pc.clear()

# El mètode `.pageCount()` retorna el número total de pàgines presents
pc.pageCount()
# El mètode `.pages()` retorna un llistat de totes les pàgines
pc.pages()


# És important destacar que no existeix el concepte de "pàgina activa"
# Quan el *layout* només conté una pàgina, tots els mètodes vistos s'apliquen sobre l'única pàgina "activa"
# Quan la composició és de més d'una pàgina, simplement cal afegir el paràmetre `page=i`


# L'exportació de la composició es duu a terme amb un objecte de la classe `QgsLayoutExporter`
exporter = QgsLayoutExporter(layout)
# El mètode `.exportToX()` permet exportar la composició a arxiu PDF o a imatge format PNG
## Exportar a PDF
exporter.exportToPdf("ruta/output.pdf", QgsLayoutExporter.PdfExportSettings())
## Exportar a imatge
exporter.exportToImage("ruta/output.png", QgsLayoutExporter.ImageExportSettings())

# La configuració de sortida es controla a través de `QgsLayoutExporter.ImageExportSettings`
image_settings = QgsLayoutExporter.ImageExportSettings()
# Un dels elements que es poden configurar és la resolució de l'arxiu generat - els seus dpi
image_settings.dpi = 300
# També es pot establir el nombre de pàgines a exportar (a través dels seus índex), que per defecte és únicament la primera
image_settings.pages = [0] 

# És bona pràctica comprovar anteriorment a l'exportació que no hi hagi cap element anterior creat
# Amb el mòdul `os` es defineix el directori de sortida de les composicions i s'elimina l'arxiu anterior que pugui haver-hi al directori 
import os
output_path = "ruta/output.png"
if os.path.exists(output_path):
    os.remove(output_path)


# Un tipus de composició especial son els ATLES, que requeixen d'un procés de generació particular
# Activar l'atlas com a layout
atlas = layout.atlas()
atlas.setEnabled(True)

# Definir la capa de cobertura
atlas.setCoverageLayer(vlayer)

# Establir el camp que genera els fulls - el nom de cada full
atlas.setPageNameExpression('"FIELD"')

# Filtrar o ordenar els fulls, si es desitja
atlas.setFilterExpression('"FIELD" < 5')
atlas.setSortExpression('"NOM"')
atlas.setSortAscending(True)

# Ajustar la composició amb diferents mètodes
# Fer que el mapa s'ajusti automàticament a cada feature
map.setAtlasDriven(True)
# Establir zoom automàtic a cada element
map.setAtlasScalingMode(QgsLayoutItemMap.Auto)
# Establir un marge percentual al voltant del mapa
map.setAtlasMargin(0.1)

# Exportar tots els fulls
exporter = QgsLayoutExporter(layout)
exporter.exportAtlasToImage(
    atlas,
    "ruta/",
    "prefix_",          
    QgsLayoutExporter.ImageExportSettings()
)


# Generat el layout, cal afegir-lo al gestor de layouts del projecte perquè no quedi en memòria
# Es defineix un objecte gestor de composicions, normalment al començament del codi
manager = project.layoutManager()
# S'afegeix el layout amb el mètode `.addLayout()`
manager.addLayout(layout)

# El flux de treball correcte en la creació de composicions és:
## Creació layout
## Addició elements
## Exportació
## Addició layout al gestor