"""ÚS EDIFICIS DE BARCELONA"""


"""INICIALITZACIÓ PROJECTE"""

# Importació de mòduls i funcions
import sys
sys.path.append("C:/projectes_git/PyQGIS_practic/Exemple")
import importlib
import os

# Forçar la recàrrega dels mòduls de simbologia
mods_a_recarregar = [
    "simbologia_unica_2_1",
    "simbologia_categorica_2_2",
    "simbologia_graduada_2_3",
    "simbologia_graduada_manual_2_4"
]

for mod in mods_a_recarregar:
    if mod in sys.modules:
        importlib.reload(sys.modules[mod])

from simbologia_unica_2_1 import simbologia_unica, simbologia_unica_linia
from simbologia_categorica_2_2 import simbologia_categorica
#from simbologia_graduada_2_3 import simbologia_graduada_QGIS
#from simbologia_graduada_manual_2_4 import simbologia_graduada_manual

# Generació instància del projecte
project = QgsProject.instance()

# Generació instància del panell de capes
root = project.layerTreeRoot()

# Neteja de totes les capes i grups prexistents al projecte
project.removeAllMapLayers()
root.removeAllChildren()


"""IMPORTACIÓ DE CAPES"""

# Diccionari de rutes - Nom de la capa: ruta absoluta
layers = {
    "Barris": "C:/projectes_git/Dades/PyQGIS_Repo/Limits_administratius_BCN/0301040100_Barris_UNITATS_ADM.shp",
    "Districtes": "C:/projectes_git/Dades/PyQGIS_Repo/Limits_administratius_BCN/0301040100_Districtes_UNITATS_ADM.shp",
    "TermeMunicipal": "C:/projectes_git/Dades/PyQGIS_Repo/Limits_administratius_BCN/0301040100_TermeMunicipal_UNITATS_ADM.shp",
    "Edificis": "C:/projectes_git/Dades/PyQGIS_Repo/Cadastre/08900/A.ES.SDGC.BU.08900.building.gml"
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

#===================================================================

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

# Aplicació de les funcions per generar la cartografia
## Ús dels edificis a Barcelona - segons cadastre / Simbologia categòrica
layer_base_districtes = simbologia_unica(
    dict_layers["Districtes"],
    (0,0,0,0),
    0.5,
    (255,200,50,255)
)

#layer_base_barris = simbologia_unica(
#    dict_layers["Barris"],
#    (0,0,0,0),
#    0.2,
#    (150,220,220,255)
#)

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

layer_carto_dark = "type=xyz&url=https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png&zmax=19&zmin=0"
# Creació de la capa de fons
layer_fons = QgsRasterLayer(layer_carto_dark, "CartoDB Dark", "wms")
if layer_fons.isValid():
    project.addMapLayer(layer_fons, True)
    print("Capa de fons carregada correctament")
else:
    print("Error al carregar la capa de fons")

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

#=============================================================================================0

"""ANÀLISI ESPACIAL"""

# Identificació de zones d'alta concentració - clústers - d'edificis amb el mateix ús 
## Ús comercial: 4_2_retail

import processing

# Filtrar els edificis comercials
request_retail = QgsFeatureRequest().setFilterExpression("\"currentUse\" = '4_2_retail'")
###layer_retail = dict_layers["Edificis"].getFeatures(request_retail) ###getFeatures() retorna un iterador de features, no una capa. 
layer_retail = dict_layers["Edificis"].materialize(request_retail)

# Convertir a centroides
result_centroids = processing.run("native:centroids", {
    'INPUT': layer_retail,
    'ALL_PARTS': False,
    'OUTPUT': 'memory:'
})
layer_retail_centroids = result_centroids['OUTPUT']
print(f"Centroides: {layer_retail_centroids.featureCount()}")
print(f"Geometria: {layer_retail_centroids.geometryType()}")

# Aplicar DBSCAN
result = processing.run("native:dbscanclustering", {
    'INPUT': layer_retail_centroids,
    'EPS': 50,          # 100 metres de distància màxima entre edificis
    'MINSIZE': 5,       # mínim 10 edificis per formar un clúster
    'FIELD_NAME': 'CLUSTER_ID',
    'SIZE_FIELD_NAME': 'CLUSTER_SIZE',
    'OUTPUT': 'memory:'
})

# Guardar el resultat
layer_clusters_retail = result['OUTPUT']
project.addMapLayer(layer_clusters_retail, False)

# Obtenir tots els valors únics de CLUSTER_ID
cluster_ids = set([f["CLUSTER_ID"] for f in layer_clusters_retail.getFeatures() if f["CLUSTER_ID"] is not None])
print(f"Valors únics de CLUSTER_ID: {sorted(cluster_ids)}")

# Estadístiques
cluster_ids = set([f["CLUSTER_ID"] for f in layer_clusters_retail.getFeatures() if f["CLUSTER_ID"] is not None])
num_clusters = len([c for c in cluster_ids if c != -1])
num_outliers = sum(1 for f in layer_clusters_retail.getFeatures() if f["CLUSTER_ID"] == -1)

print(f"Número de clústers: {num_clusters}")
print(f"Número d'outliers: {num_outliers}")


# Aplicar simbologia
def simbologia_clusters(layer, cluster_field, color_ramp, outlier_color=(128,128,128,255)):
    """
    Aplica simbologia categòrica a una capa de clústers

    La funció:
        Clona la capa d'entrada
        Assigna un nom nou a la capa clonada
        Genera simbologia assignant un color interpolat de la rampa a cada clúster
        Els outliers (CLUSTER_ID = -1) reben un color neutre

    Paràmetres de la funció:
        layer : capa vectorial amb els clústers
        cluster_field : nom del camp que conté els identificadors de clúster
        color_ramp : nom de la rampa de colors de QGIS
        outlier_color : color dels outliers en format (R,G,B,A) - gris per defecte
    """
    # Clonació de la capa d'entrada
    layer_clone = layer.clone()

    # Assignació d'un nou nom
    layer_clone.setName(f"{layer_clone.name()}_clusters")

    # Obtenir els valors únics de CLUSTER_ID, excloent None
    cluster_ids = sorted(set(
        f[cluster_field] for f in layer_clone.getFeatures()
        if f[cluster_field] is not None and f[cluster_field] != -1
    ))

    # Rampa de colors
    rampa = QgsStyle().defaultStyle().colorRamp(color_ramp)
    num_clusters = len(cluster_ids)

    # Generació de les categories
    categories = []

    # Outliers
    symbol_outlier = QgsSymbol.defaultSymbol(layer_clone.geometryType())
    symbol_outlier.setColor(QColor(*outlier_color))
    categories.append(QgsRendererCategory(-1, symbol_outlier, "Outlier"))

    # Clústers
    for i, cluster_id in enumerate(cluster_ids):
        symbol = QgsSymbol.defaultSymbol(layer_clone.geometryType())
        # Interpolació del color de la rampa
        t = float(i) / (num_clusters - 1) if num_clusters > 1 else 0
        color = rampa.color(t)
        symbol.setColor(color)
        categories.append(QgsRendererCategory(cluster_id, symbol, f"Clúster {cluster_id}"))

    # Renderer categòric
    renderer = QgsCategorizedSymbolRenderer(cluster_field, categories)
    layer_clone.setRenderer(renderer)

    # Addició de la capa al projecte
    project.addMapLayer(layer_clone)

    # Actualització
    layer_clone.triggerRepaint()
    iface.mapCanvas().refresh()
    iface.layerTreeView().refreshLayerSymbology(layer_clone.id())

    return layer_clone

layer_clusters_visual = simbologia_clusters(
    layer=layer_clusters_retail,
    cluster_field="CLUSTER_ID",
    color_ramp="Spectral"
)

project.addMapLayer(layer_clusters_visual)


#Ajuntar geometries per clúster
result_collect = processing.run("native:collect", {
    'INPUT': layer_clusters_retail,
    'FIELD': ['CLUSTER_ID'],
    'OUTPUT': 'memory:'
})
layer_collected = result_collect['OUTPUT']

# Generar polígon convex per cada clúster
result_hull = processing.run("native:convexhull", {
    'INPUT': layer_collected,
    'OUTPUT': 'memory:'
})
layer_hull_retail = result_hull['OUTPUT']
project.addMapLayer(layer_hull_retail, True)