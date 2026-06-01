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
    0.3,
    (0,0,0,255)
)

layer_base_barris = simbologia_unica(
    dict_layers["Barris"],
    (0,0,0,0),
    0.1,
    (0,0,0,255)
)

layer_us_edificis = simbologia_categorica(
    dict_layers["Edificis"],
    'currentUse',
    ['red','green','grey','yellow', 'blue', 'purple'],
    0.15,
    "white"
)


""" GENERACIÓ DE LA COMPOSICIÓ"""

layout = QgsPrintLayout(project)
layout.initializeDefaults()
layout.setName("Ús dels edificis")

manager = project.layoutManager()

map = QgsLayoutItemMap(layout)
map.attemptResize(QgsLayoutSize(200,200,QgsUnitTypes.LayoutMillimeters))
#map.attemptMove(QgsLayoutPoint(x,y,units))
extent = dict_layers["TermeMunicipal"].extent() 
# Afegir un marge del 5% al voltant
margin = extent.width() * 0.1
extent.grow(margin)
map.setExtent(extent)
map.zoomToExtent(extent)
map.setLayers([layer_us_edificis, layer_base_barris, layer_base_districtes])
map.setKeepLayerSet(True)
layout.addLayoutItem(map)

legend = QgsLayoutItemLegend(layout)
legend.setLinkedMap(map)
#legend.attemptResize(QgsLayoutSize(x,y,units))
legend.attemptMove(QgsLayoutPoint(205,100,QgsUnitTypes.LayoutMillimeters))
legend.setTitle("Classificació dels usos dels edificis de Barcelona")
# Títol
legend.setStyleFont(QgsLegendStyle.Title, QFont("Arial", 10))
# Grups
legend.setStyleFont(QgsLegendStyle.Group, QFont("Arial", 8))
# Subgrups
legend.setStyleFont(QgsLegendStyle.Subgroup, QFont("Arial", 6))
# Elements individuals
legend.setStyleFont(QgsLegendStyle.SymbolLabel, QFont("Arial", 6))

legend.setAutoUpdateModel(True) 
layout.addLayoutItem(legend)

scale = QgsLayoutItemScaleBar(layout)
scale.setLinkedMap(map)
#scale.attemptResize(QgsLayoutSize(x,y,units))
scale.attemptMove(QgsLayoutPoint(205,180,QgsUnitTypes.LayoutMillimeters))
scale.applyDefaultSize()
scale.setStyle("Line Ticks Up")  
layout.addLayoutItem(scale)

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
map.setAtlasDriven(True)
# Establir zoom automàtic a cada element
map.setAtlasScalingMode(QgsLayoutItemMap.Auto)
# Establir un marge percentual al voltant del mapa
map.setAtlasMargin(0.2)

# Exportar tots els fulls
exporter = QgsLayoutExporter(layout)
image_settings = QgsLayoutExporter.ImageExportSettings()
image_settings.dpi = 350
exporter.exportToImage(
    atlas,
    "C:/projectes_git/PyQGIS_practic/Resultats/",
    ".png",          
    image_settings
)
    

#exporter = QgsLayoutExporter(layout)
#image_settings = QgsLayoutExporter.ImageExportSettings()
#image_settings.dpi = 350
#result = exporter.exportToImage(output_path, image_settings)
#print(f"Resultat: {result}")
#print(f"Fitxer existeix: {os.path.exists(output_path)}")

manager.addLayout(layout)