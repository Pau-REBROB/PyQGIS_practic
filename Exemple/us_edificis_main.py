"""ÚS EDIFICIS DE BARCELONA"""
"""Detecció automàtica de clústers comercials i anàlisi d'accessibilitat viària a Barcelona mitjançant PyQGIS i QNEAT3"""

"""
00_inicialitzacio.py
01_importacio.py
02_analisi.py
03_simbologia.py
04_layout.py
main.py
 -----
 main.py

config.py              # rutes, colors, paràmetres DBSCAN...

carrega_dades.py
analisi_retail.py
analisi_usos.py

simbologia_unica.py
simbologia_categorica.py
simbologia_graduada.py

layout_general.py
layout_clusters.py

--------

PyQGIS_practic/

main.py

config.py

inicialitzacio.py
importacio.py
analisi.py

simbologia/
    simbol_unic.py
    simbol_categoric.py
    simbol_graduat.py

layouts/
    layout_general.py
    layout_clusters.py
"""

"""
1. Visió general: composició de la distribució dels usos dels edificis
2. Dinàmica comercial: composició dels principals eixos comercials i el seu accés
3. Comparació entre usos: mateix pipeline amb altres usos
"""

"""
1. Composició general usos edificis (potser els residencials molt menys opacs)
2. Atles per districte (10 pàgines)
3. Concentració activitat comercial (graf, clústers i isoàrees)
4. Comparació clústers (un per pàgina, o potser tots junts)
5. Heatmap / Malla hexagonal
"""
# =============================================================================
# 1. Importació de mòduls

from inicialitzacio import inicialitzar_projecte, recarregar_moduls
from importacio import carregar_capes
from preparacio_dades import netejar_capa, desar_carregar_capa, netejar_grup
from analisi_espacial import seleccio_atribut, clusters_dbscan, envolvent_clusters, generacio_centroides, isoarees_qneat3
# simbologia
from layout_general import generar_layout, afegir_mapa, afegir_titol, afegir_llegenda, afegir_escala, afegir_nord, exportar_layout

## Funcions d'alt nivell en ANÀLISI i LAYOUT?

## Arxiu de configuració??
from config import *

# ==============================================================================
# 2. Inicialització

project, root = inicialitzar_projecte()

recarregar_moduls(llista=LLISTA_MODULS)

# ==============================================================================
# 3. Importació de capes

dict_layers, dict_indexs = carregar_capes(layers=LAYERS)

# ==============================================================================
# 4. Neteja de les dades

ddddd

# ==============================================================================

#============================================================================================

"""ANÀLISI ESPACIAL"""

# Identificació de zones d'alta concentració - clústers - d'edificis amb el mateix ús 
## Ús comercial: 4_2_retail

# Seleccionar els edificis d'ús = retail
# Generació centroides
# Agrupació en clústers
# Envolvent convexa dels clústers d'igual ID
# Simbologia dels envolvents
# Anàlisi de xarxes


# Selecció dels edificis comercials a partir d'un request
request_retail = QgsFeatureRequest().setFilterExpression('"currentUse" = \'4_2_retail\'')
###layer_retail = dict_layers["Edificis"].getFeatures(request_retail) ###getFeatures() retorna un iterador de features, no una capa. 
layer_retail = dict_layers["Edificis"].materialize(request_retail)

# Generació dels centroides dels edificis tipus *retail*
result_centroids_retail = processing.run("native:centroids", {
    'INPUT': layer_retail,
    'ALL_PARTS': False,
    'OUTPUT': 'memory:'
})
# Desat del resultat en una capa
layer_centroids_retail = result_centroids_retail['OUTPUT']

# Generació de clústers retail amb mètode DBSCAN a partir dels centroides dels edificis retail
result_clusters_retail = processing.run("native:dbscanclustering", {
    'INPUT': layer_centroids_retail,
    'EPS': 100,          # 100 metres de distància màxima entre edificis
    'MINSIZE': 5,       # mínim 5 edificis per formar un clúster
    'FIELD_NAME': 'CLUSTER_ID',
    'SIZE_FIELD_NAME': 'CLUSTER_SIZE',
    'OUTPUT': 'memory:'
})
# Desat del resultat en una capa
layer_clusters_retail = result_clusters_retail['OUTPUT']

# Filtre de tots els valors únics de CLUSTER_ID - els que no son NULL
cluster_ids = set([f["CLUSTER_ID"] for f in layer_clusters_retail.getFeatures() if f["CLUSTER_ID"] is not 'NULL'])
print(f"Número de clústers: {len(cluster_ids)}")
# Generació d'una consulta per filtrar la capa de clústers a aquells no nuls
request_clusters = QgsFeatureRequest().setFilterExpression('"CLUSTER_ID" IS NOT NULL AND "CLUSTER_ID" != -1')
layer_clusters_retail_notNull = layer_clusters_retail.materialize(request_clusters)

# Generar envolvent per cada clúster
result_hull = processing.run("qgis:minimumboundinggeometry", {
    'INPUT': layer_clusters_retail_notNull,
    'FIELD': 'CLUSTER_ID',
    'TYPE': 2,
    'OUTPUT': 'memory:'
})
# Desat del resultat en una capa
layer_hull_retail = result_hull['OUTPUT']

# Dissolució de les geometria de les envolents per unificar-les
result_dissolved = processing.run("native:dissolve", {
    'INPUT': layer_hull_retail,
    'FIELD': [],
    'SEPARATE_DISJOINT': True,
    'OUTPUT': 'memory:'
})
# Desat del resultat en una capa
layer_zones_retail = result_dissolved['OUTPUT']
# Canvi de nom de la capa 'output'
layer_zones_retail.setName("Zones_comercials")

# Addició capa al projecte
project.addMapLayer(layer_zones_retail, False)

# Generació centroides de les zones dissoltes per a l'anàlisi de xarxa
result_centroids_zones = processing.run("native:centroids", {
    'INPUT': layer_zones_retail,
    'ALL_PARTS': False,
    'OUTPUT': 'memory:'
})
layer_zones_centroids = result_centroids_zones['OUTPUT']


# Anàlisi de xarxes
## Isoàrees de proximitat a les zones de comerços
# S'utilitza el plugin QNEAT3
result_isoareas = processing.run("qneat3:isoareaaspolygonsfromlayer", {
    'INPUT': dict_layers["Graf"],
    'START_POINTS': layer_zones_centroids,
    'ID_FIELD': "id",
    'MAX_DIST': 5000,#DISTÀNCIA MÀXIMA
    'INTERVAL': 100,
    'STRATEGY': 0,#SHORTEST PATH
    'OUTPUT_INTERPOLATION': "C:/projectes_git/PyQGIS_practic/Resultats/output_interpolation.tif",
    'OUTPUT_POLYGONS': "C:/projectes_git/PyQGIS_practic/Resultats/output_polygons.shp"
})

layer_polygons_isoareas = QgsVectorLayer(
    "C:/projectes_git/PyQGIS_practic/Resultats/output_polygons.shp",
    "Isoàrees",
    "ogr"
)
project.addMapLayer(layer_polygons_isoareas, False)

#============================================================================================

"""GENERACIÓ DE CARTOGRAFIA"""
# QUINS LAYOUTS VULL CREAR?
## simbologia única per tenir de fons les divisions administratives
## simbologia categòrica --> ús dels edificis / barris,districtes
## simbologia graduada --> altura dels edificis / àrea barris,districtes / població (CAL AFEGIR-LA)
## simbologia regles --> els barris amb més,menys àrea o població / edificis amb més,menys plantes


# Desactivar la visibilitat de totes les capes importades
for layer in project.mapLayers().values():
    node = root.findLayer(layer)
    if node:
        node.setItemVisibilityChecked(False)


# Aplicació de simbologia per generar la cartografia
## Ordre de capes:
### CartoDarrk
### Districtes
### Barris
### Graf
### Edificis
### Clústers
### Isoàrees

# 1. Mapa base de fons
layer_carto_dark = "type=xyz&url=https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png&zmax=19&zmin=0"
# Creació de la capa de fons
layer_fons = QgsRasterLayer(layer_carto_dark, "CartoDB Dark", "wms")
if layer_fons.isValid():
    project.addMapLayer(layer_fons, False)
    root.addLayer(layer_fons)
    print("Capa de fons carregada correctament")
else:
    print("Error al carregar la capa de fons")


# 2. Límits administratius
layer_base_districtes = simbologia_unica(
    dict_layers["Districtes"],
    (0,0,0,0),
    0.5,
    (255,200,50,255)
)
print("Afegint els límits administratius dels districtes")
root.addLayer(layer_base_districtes)

layer_base_barris = simbologia_unica(
    dict_layers["Barris"],
    (0,0,0,0),
    0.2,
    (150,220,220,255)
)
print("Afegint els límits administratius dels barris")
root.addLayer(layer_base_barris)


# 3. Graf viari
print("Afegint el graf viari")
root.addLayer(dict_layers["Graf"]) ##FUNCIÓ SIMBOLOGIA ÜNICA? 


# 4. Edificis amb usos
dict_colors_edificis = {
    "1_residential": (255, 235, 175, 255),
    "2_agriculture": (170, 255, 115, 255),
    "3_industrial": (178, 178, 178, 255),
    "4_1_office": (255, 170, 0, 255),
    "4_2_retail": (255, 127, 0, 255),
    "4_3_publicServices": (200, 170, 220, 255)
} # Colors basats en convencions cartogràfiques habituals per a usos del sòl

layer_us_edificis = simbologia_categorica(
    dict_layers["Edificis"],
    'currentUse',
    dict_colors_edificis, 
    0.1,
    "white"
)

print("Afegint els edificis classificats per ús")
root.addLayer(layer_us_edificis)


# 5. Clústers retail
cluster_symbol = QgsSymbol.defaultSymbol(layer_zones_retail.geometryType())
cluster_symbol.setColor(QColor(255, 127, 0, 125))
cluster_symbol.symbolLayer(0).setStrokeColor(QColor(255, 127, 0, 255))
renderer = QgsSingleSymbolRenderer(cluster_symbol)
layer_zones_retail.setRenderer(renderer)
print("Afegint els clústers")
root.addLayer(layer_zones_retail)


# 6. Isoàrees
layer_isoareas = simbologia_graduada_QGIS(layer_polygons_isoareas,
                                          "cost_level",
                                          7, 
                                          "Spectral",
                                          "Jenks",
                                          (255,255,255,100),
                                          0.2) 

print("Afegint les isoàrees")
root.addLayer(layer_isoareas)


#========================================================================================

""" GENERACIÓ DE LA COMPOSICIÓ"""

### DEFINIR ELEMENT
### ADDICIÓ AL LAYOUT
### CONFIGURACIÓ

# LAYOUT
layout = QgsPrintLayout(project)
layout.initializeDefaults()
layout.setName("Ús dels edificis")

manager = project.layoutManager()


# MAP
layout_map = QgsLayoutItemMap(layout)
layout.addLayoutItem(layout_map)

#layout_map.setLayers([layer_us_edificis, layer_base_barris, layer_base_districtes, layer_fons])
layout_map.setLayers([layer_us_edificis, layer_base_districtes, layer_fons])
layout_map.setKeepLayerSet(True)

extent = dict_layers["TermeMunicipal"].extent() 
layout_map.zoomToExtent(extent)

layout_map.attemptResize(QgsLayoutSize(297,210,QgsUnitTypes.LayoutMillimeters))    #DIN A4 apaisat 297x210mm
layout_map.attemptMove(QgsLayoutPoint(0,0,QgsUnitTypes.LayoutMillimeters))


# TITLE
title = QgsLayoutItemLabel(layout)
layout.addLayoutItem(title)

title.attemptMove(QgsLayoutPoint(10, 5, QgsUnitTypes.LayoutMillimeters))
title.attemptResize(QgsLayoutSize(275, 10, QgsUnitTypes.LayoutMillimeters))

title.setText("Ús dels edificis de Barcelona - Districte: [% \"NOM\" %]")
title_format = QgsTextFormat()
title_format.setFont(QFont("Arial", 20))
title_format.setSize(20)
title_format.setSizeUnit(QgsUnitTypes.RenderPoints)
title_format.setColor(QColor(255, 255, 255))
title.setTextFormat(title_format)

#title.setHAlign(Qt.AlignCenter)
title.setMarginX(5)  # marge horitzontal en mm
title.setMarginY(1)  # marge vertical en mm

title.setBackgroundEnabled(True)
title.setBackgroundColor(QColor(100, 100, 100, 200))
title.setFrameEnabled(True)
title.setFrameStrokeColor(QColor(255, 255, 255, 200))
title.setFrameStrokeWidth(QgsLayoutMeasurement(0.75, QgsUnitTypes.LayoutMillimeters))


# LEGEND
legend = QgsLayoutItemLegend(layout)
layout.addLayoutItem(legend)

legend.setLinkedMap(layout_map)
legend.setAutoUpdateModel(True) 

legend.setTitle("Ús dels edificis")

legend.attemptMove(QgsLayoutPoint(10,30,QgsUnitTypes.LayoutMillimeters))

text_format = QgsTextFormat()
text_format.setSize(10)
text_format.setSizeUnit(QgsUnitTypes.RenderPoints)
text_format.setColor(QColor(255, 255, 255))
# Títol
legend.rstyle(QgsLegendStyle.Title).setTextFormat(text_format)
# Grups
legend.rstyle(QgsLegendStyle.Group).setTextFormat(text_format)
# Subgrups
legend.rstyle(QgsLegendStyle.Subgroup).setTextFormat(text_format)
# Elements individuals
legend.rstyle(QgsLegendStyle.SymbolLabel).setTextFormat(text_format)

legend.setBackgroundEnabled(True)
legend.setBackgroundColor(QColor(80, 80, 80, 200))
legend.setFrameEnabled(False)

legend.setAutoUpdateModel(False)  
root_legend = legend.model().rootGroup()
noms_a_eliminar = ["Simbologia_única", "CartoDB Dark"]
for child in root_legend.children()[:]:
    if child.name() in noms_a_eliminar:
        root_legend.removeChildNode(child)


# SCALE
scale = QgsLayoutItemScaleBar(layout)
layout.addLayoutItem(scale)

scale.setLinkedMap(layout_map)

#scale.attemptResize(QgsLayoutSize(15,15,QgsUnitTypes.LayoutMillimeters))
scale.attemptMove(QgsLayoutPoint(270,200,QgsUnitTypes.LayoutMillimeters))

scale.setStyle("Numeric")
numeric_format = QgsBasicNumericFormat()
numeric_format.setShowThousandsSeparator(True)
numeric_format.setNumberDecimalPlaces(0)
scale.setNumericFormat(numeric_format)

scale_format = QgsTextFormat()
scale_format.setFont(QFont("Arial"))
scale_format.setSize(16)
scale_format.setSizeUnit(QgsUnitTypes.RenderPoints)
scale_format.setColor(QColor(255, 255, 255))
scale.setTextFormat(scale_format)
#scale.setFontColor(QColor(255, 255, 255))


# NORTH
north = QgsLayoutItemPicture(layout)
layout.addLayoutItem(north)

north.setPicturePath("C:/projectes_git/Dades/nord2.png")
north.attemptResize(QgsLayoutSize(15, 15, QgsUnitTypes.LayoutMillimeters))
north.attemptMove(QgsLayoutPoint(270, 180, QgsUnitTypes.LayoutMillimeters))



#output_path = "C:/projectes_git/PyQGIS_practic/Resultats/Classificacio_edificis.png"
#if os.path.exists(output_path):
#    os.remove(output_path)  


# Activar l'atlas com a layout
atlas = layout.atlas()
atlas.setEnabled(True)

# Definir la capa de cobertura
atlas.setCoverageLayer(dict_layers["Districtes"])

# Establir el camp que genera els fulls - el nom de cada full
atlas.setPageNameExpression('"NOM"')
atlas.setFilenameExpression('"NOM"')

# Filtrar o ordenar els fulls, si es desitja
#atlas.setFilterExpression('"FIELD" < 5')
#atlas.setSortExpression('"NOM"')
#atlas.setSortAscending(True)


# Ajustar la composició amb diferents mètodes
# Fer que el mapa s'ajusti automàticament a cada feature
layout_map.setAtlasDriven(True)
# Establir zoom automàtic a cada element
layout_map.setAtlasScalingMode(QgsLayoutItemMap.Auto)
# Establir un marge percentual al voltant del mapa
layout_map.setAtlasMargin(0.1)


atlas.updateFeatures()
atlas.beginRender()


# Exportar tots els fulls
exporter = QgsLayoutExporter(layout)
image_settings = QgsLayoutExporter.ImageExportSettings()
image_settings.dpi = 125
exporter.exportToImage(
    atlas,
    "C:/projectes_git/PyQGIS_practic/Resultats/",
    ".png",          
    image_settings
)

atlas.endRender()


#exporter = QgsLayoutExporter(layout)
#image_settings = QgsLayoutExporter.ImageExportSettings()
#image_settings.dpi = 300
#result = exporter.exportToImage(output_path, image_settings)
#print(f"Resultat: {result}")
#print(f"Fitxer existeix: {os.path.exists(output_path)}")

existing = manager.layoutByName("Ús dels edificis")
if existing:
    manager.removeLayout(existing)

manager.addLayout(layout)

