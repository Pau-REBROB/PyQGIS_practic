"""ÚS EDIFICIS DE BARCELONA"""


"""INICIALITZACIÓ PROJECTE"""

# Importació de mòduls i funcions
import sys
sys.path.append("C:/projectes_git/PyQGIS_practic/Exemple")
import importlib
import os
import processing

# Forçar la recàrrega dels mòduls de simbologia
mods_a_recarregar = [
    "simbologia_unica_2_1",
    "simbologia_categorica_2_2",
    "simbologia_graduada_2_3",
]

for mod in mods_a_recarregar:
    if mod in sys.modules:
        importlib.reload(sys.modules[mod])

from simbologia_unica_2_1 import simbologia_unica, simbologia_unica_linia
from simbologia_categorica_2_2 import simbologia_categorica
from simbologia_graduada_2_3 import simbologia_graduada_QGIS

# Generació instància del projecte
project = QgsProject.instance()

# Generació instància del panell de capes
root = project.layerTreeRoot()

# Neteja de totes les capes i grups prexistents al projecte
project.removeAllMapLayers()
root.removeAllChildren()

#============================================================================================

"""IMPORTACIÓ DE CAPES"""

# Diccionari de rutes - Nom de la capa: ruta absoluta
layers = {
    "Barris": "C:/projectes_git/Dades/PyQGIS_Repo/Limits_administratius_BCN/0301040100_Barris_UNITATS_ADM.shp",
    "Districtes": "C:/projectes_git/Dades/PyQGIS_Repo/Limits_administratius_BCN/0301040100_Districtes_UNITATS_ADM.shp",
    "TermeMunicipal": "C:/projectes_git/Dades/PyQGIS_Repo/Limits_administratius_BCN/0301040100_TermeMunicipal_UNITATS_ADM.shp",
    "Edificis": "C:/projectes_git/Dades/PyQGIS_Repo/Cadastre/08900/A.ES.SDGC.BU.08900.building.gml",
    "Graf": "C:/projectes_git/Dades/PyQGIS_Repo/Graf_viari/BCN_GrafVial_Trams_ETRS89_SHP.shp"
}

# Diccionari buit de les capes
dict_layers = {}

# Diccionari buit dels índex de les capes
dict_indexs = {}


# Importació de les capes al projecte i generació dels índex espacials sobre les geometries de cada capa
for i, (nom, path) in enumerate(layers.items()):
    
    # Creació de la capa vectorial amb la ruta i utilitzant el nom
    layer = QgsVectorLayer(path, nom, "ogr")
    
    # Comprovació que la capa és vàlida
    if not layer.isValid():
        print(f"Error al carregar la capa de {nom}!")
    else:
        # Addició de la capa al projecte, sense afegir-la al llenç
        project.addMapLayer(layer, False)
               
        # Addició de la capa al diccionari de diccionaris de capes, al grup de Límits administratius
        # El key és el nom de la capa, i el value és la capa vectorial pròpiament (QgsVectorLayer)
        dict_layers[nom] = layer
        
        # Generació de l'índex i addició al diccionari d'índexs
        dict_indexs[nom] = QgsSpatialIndex(layer.getFeatures())

#============================================================================================

"""SISTEMES DE REFERÈNCIA"""

# Comprovació dels sistema de referència de coordenades del projecte
print("SRC del projecte:", project.crs().authid())

# Comprovació dels sistema de referència de coordenades de les capes
for layer in dict_layers.values():
    # Impresió per pantalla del SRC de cada capa, en codi EPSG
    print(f"El SRC de la capa {layer.name()} és {layer.crs().authid()}")
       
    # Comparació amb el SRC del projecte
    if layer.crs().authid() == project.crs().authid():
        print(f"La capa {layer.name()} i el projecte estan en el mateix SRC")
    else:
        print(f"La capa {layer.name()} està en el SRC {layer.crs().authid()} i necessita ser reprojectada a EPSG:25831!")

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




# Composició global
# LAYOUT
layout_isoareas = QgsPrintLayout(project)
layout_isoareas.initializeDefaults()
layout_isoareas.setName("Proximitat als eixos comercials")

#manager = project.layoutManager()


# MAP
layout_map_isoareas = QgsLayoutItemMap(layout_isoareas)
layout_isoareas.addLayoutItem(layout_map_isoareas)

#layout_map.setLayers([layer_us_edificis, layer_base_barris, layer_base_districtes, layer_fons])
layout_map_isoareas.setLayers([layer_isoareas, 
                      layer_us_edificis,
                      dict_layers["Graf"],
                      layer_base_districtes,
                      layer_fons])
layout_map_isoareas.setKeepLayerSet(True)

extent = dict_layers["TermeMunicipal"].extent() 
layout_map_isoareas.zoomToExtent(extent)

layout_map_isoareas.attemptResize(QgsLayoutSize(297,210,QgsUnitTypes.LayoutMillimeters))    #DIN A4 apaisat 297x210mm
layout_map_isoareas.attemptMove(QgsLayoutPoint(0,0,QgsUnitTypes.LayoutMillimeters))


# TITLE
title = QgsLayoutItemLabel(layout_isoareas)
layout_isoareas.addLayoutItem(title)

title.attemptMove(QgsLayoutPoint(10, 5, QgsUnitTypes.LayoutMillimeters))
title.attemptResize(QgsLayoutSize(275, 10, QgsUnitTypes.LayoutMillimeters))

title.setText("Proximitat als eixos comercials de Barcelona")
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
legend = QgsLayoutItemLegend(layout_isoareas)
layout_isoareas.addLayoutItem(legend)

legend.setLinkedMap(layout_map_isoareas)
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
scale = QgsLayoutItemScaleBar(layout_isoareas)
layout_isoareas.addLayoutItem(scale)

scale.setLinkedMap(layout_map_isoareas)

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
north = QgsLayoutItemPicture(layout_isoareas)
layout_isoareas.addLayoutItem(north)

north.setPicturePath("C:/projectes_git/Dades/nord2.png")
north.attemptResize(QgsLayoutSize(15, 15, QgsUnitTypes.LayoutMillimeters))
north.attemptMove(QgsLayoutPoint(270, 180, QgsUnitTypes.LayoutMillimeters))



output_path = "C:/projectes_git/PyQGIS_practic/Resultats/Proximitat_retail.png"
if os.path.exists(output_path):
    os.remove(output_path)  

exporter_isoareas = QgsLayoutExporter(layout_isoareas)
image_settings = QgsLayoutExporter.ImageExportSettings()
image_settings.dpi = 300
result = exporter_isoareas.exportToImage(output_path, image_settings)
print(f"Resultat: {result}")
print(f"Fitxer existeix: {os.path.exists(output_path)}")

existing = manager.layoutByName("Proximitat als eixos comercials")
if existing:
    manager.removeLayout(existing)

manager.addLayout(layout_isoareas)
