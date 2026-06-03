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
    0.4,
    (200,200,200,255)
)

layer_base_barris = simbologia_unica(
    dict_layers["Barris"],
    (0,0,0,0),
    0.2,
    (150,220,220,255)
)

dict_colors_edificis = {
    "1_residential": (255, 235, 175, 255),
    "2_agriculture": (170, 255, 115, 255),
    "3_industrial": (178, 178, 178, 255),
    "4_1_office": (255, 170, 0, 255),
    "4_2_retail": (255, 127, 0, 255),
    "4_3_publicServices": ( 255, 190, 190, 255)
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


""" GENERACIÓ DE LA COMPOSICIÓ"""

### DEFINIR ELEMENT
### ADDICIÓ AL LAYOUT
### CONFIGURACIÓ

layout = QgsPrintLayout(project)
layout.initializeDefaults()
layout.setName("Ús dels edificis")

manager = project.layoutManager()

layout_map = QgsLayoutItemMap(layout)

extent = dict_layers["TermeMunicipal"].extent() 
# Afegir un marge del 5% al voltant
#margin = extent.width() * 0.1
#extent.grow(margin)
#layout_map.setExtent(extent)

layout_map.zoomToExtent(extent)
layout_map.setLayers([layer_us_edificis, layer_base_barris, layer_base_districtes, layer_fons])


layout_map.setKeepLayerSet(True)
layout.addLayoutItem(layout_map)


layout_map.attemptResize(QgsLayoutSize(297,210,QgsUnitTypes.LayoutMillimeters))    #DIN A4 apaisat 297x210mm
layout_map.attemptMove(QgsLayoutPoint(0,0,QgsUnitTypes.LayoutMillimeters))


title = QgsLayoutItemLabel(layout)
title.attemptMove(QgsLayoutPoint(205, 5, QgsUnitTypes.LayoutMillimeters))
title.attemptResize(QgsLayoutSize(100, 20, QgsUnitTypes.LayoutMillimeters))
title.setText("Ús dels edificis de Barcelona\n Districte de [% \"NOM\" %]")
title_format = QgsTextFormat()
title_format.setFont(QFont("Arial", 20))
title_format.setSize(20)
title_format.setSizeUnit(QgsUnitTypes.RenderPoints)
title_format.setColor(QColor(255, 255, 255))
title.setTextFormat(title_format)
title.setBackgroundEnabled(True)
title.setBackgroundColor(QColor(100, 100, 100, 200))

layout.addLayoutItem(title)


legend = QgsLayoutItemLegend(layout)
legend.setLinkedMap(layout_map)
#legend.attemptResize(QgsLayoutSize(x,y,units))

legend.attemptMove(QgsLayoutPoint(10,10,QgsUnitTypes.LayoutMillimeters))
legend.setTitle("Ús dels edificis de Barcelona")

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

legend.setAutoUpdateModel(True) 
layout.addLayoutItem(legend)


scale = QgsLayoutItemScaleBar(layout)
scale.setLinkedMap(layout_map)
#scale.attemptResize(QgsLayoutSize(x,y,units))
scale.attemptMove(QgsLayoutPoint(270,170,QgsUnitTypes.LayoutMillimeters))
scale.setFontColor(QColor(255, 255, 255))
scale.applyDefaultSize()
scale.setStyle("Numeric")
numeric_format = QgsBasicNumericFormat()
numeric_format.setShowThousandsSeparator(True)
numeric_format.setNumberDecimalPlaces(0)
scale.setNumericFormat(numeric_format)  
layout.addLayoutItem(scale)

north = QgsLayoutItemPicture(layout)
north.setPicturePath("C:/projectes_git/Dades/nord2.png")
north.attemptResize(QgsLayoutSize(15, 15, QgsUnitTypes.LayoutMillimeters))
north.attemptMove(QgsLayoutPoint(270, 180, QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(north)

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
layout_map.setAtlasMargin(0.5)


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
