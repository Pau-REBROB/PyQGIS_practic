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

# Per defecte, la mida del mapa és 0x0 i es situa a la posició (0,0)
# Per a redimensionar-lo, s'utilitza el mètode `.attemptResize()`
map.attemptResize(QgsLayoutSize(x,y,units))
# Per a posicionar-lo, s'utilitza el mètode `.attemptMove()`
map.attemptMove(QgsLayoutPoint(x,y,units))
## Les unitats de mida i posició son objectes de la classe `QgsUnitTypes.LayoutMillimeters` o `QgsUnitTypes.LayoutPixels`

# Per a establir una extensió, s'utilitza el mètode `.setExtent()`
extent = map.setExtent()
## Es pot seleccionar l'extensió del mapa amb `map.extent()`
## Es pot seleccionar l'extensió actual del canvas amb `iface.mapCanvas().extent()`
## Es pot seleccionar l'extensió màxima de totes les capes del panell de capes del projecte amb `project.layerTreeRoot().extent()`
## Es pot definir manualment amb `QgsRectangle(xmin, ymin, xmax, ymax)`
# Establerta l'extensió, cal forçar la seva renderització
map.zoomToExtent(extent)

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
