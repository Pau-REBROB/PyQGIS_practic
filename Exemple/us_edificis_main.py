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

import sys
sys.path.append("C:/projectes_git/PyQGIS_practic/Exemple")

import inicialitzacio
import importacio
import preparacio_dades
import analisi_espacial
import simbologia_unica_2_1
import simbologia_categorica_2_2
import simbologia_graduada_2_3
import layout_general

from simbologia_unica_2_1 import simbologia_unica, simbologia_unica_linia
from simbologia_categorica_2_2 import simbologia_categorica
from simbologia_graduada_2_3 import simbologia_graduada_QGIS
from layout_general import generar_layout, afegir_mapa, afegir_titol, afegir_llegenda, afegir_escala, afegir_nord, exportar_layout

## Funcions d'alt nivell en ANÀLISI i LAYOUT?

## Arxiu de configuració
import config

# LLISTA_MODULS
# LAYERS
# CAMPS_MANTENIR
# SIMBOLOGIA


# ==============================================================================
# 2. Inicialització

project, root = inicialitzacio.inicialitzar_projecte()

inicialitzacio.recarregar_moduls(llista=config.LLISTA_MODULS)

# ==============================================================================
# 3. Importació de capes

dict_layers, dict_indexs = importacio.carregar_capes(layers=config.LAYERS)

# ==============================================================================
# 4. Neteja de les dades

dict_layers_clean = preparacio_dades.netejar_grup(dict_layers=dict_layers, configuracio=config.CAMPS_MANTENIR)

# ==============================================================================
# 5. Anàlisi espacial

zones_retail = analisi_espacial.zones_us(layer=dict_layers_clean["Cadastre"]["Edificis"],
                                         expressio=''' "currentUse" = '4_2_retail' ''',
                                         eps=100,
                                         min_size=5)

zones_office = analisi_espacial.zones_us(layer=dict_layers_clean["Cadastre"]["Edificis"],
                                         expressio='"currentUse" = \'4_1_office\'',
                                         eps=100,
                                         min_size=5)

zones_public = analisi_espacial.zones_us(layer=dict_layers_clean["Cadastre"]["Edificis"],
                                         expressio='"currentUse" = \'4_3_publicServices\'',
                                         eps=100,
                                         min_size=5)

zones_residential = analisi_espacial.zones_us(layer=dict_layers_clean["Cadastre"]["Edificis"],
                                              expressio='"currentUse" = \'1_residential\'',
                                              eps=100,
                                              min_size=5) #EN AQUEST CAS, S'HAURIA DE MIRAR ELS PARÀMETRES

isoarees = analisi_espacial.isoarees_qneat3(graf_layer=dict_layers_clean["Graf"]["Graf_trams"],
                                            points_layer=zones_retail,
                                            strat=0,
                                            max_dist=5000,
                                            interval=250)

#============================================================================================
# 6. Simbologia
## Composició general (general + atles)
layer_districtes = simbologia_unica(layer=dict_layers_clean["Limits_administratius"]["Districtes"],
                                    **config.SIMBOLOGIA["Districtes"]
                                    )

layer_barris = simbologia_unica(layer=dict_layers_clean["Limits_administratius"]["Barris"],
                                **config.SIMBOLOGIA["Barris"]
                                )

layer_edificis = simbologia_categorica(layer=dict_layers_clean["Cadastre"]["Edificis"],
                                       **config.SIMBOLOGIA["Edificis"]
                                       )

## Concentració activitat comercial
layer_graf = simbologia_unica_linia(layer=dict_layers_clean["Graf"]["Graf_trams"],
                                    **config.SIMBOLOGIA["Graf"]
                                    )

layer_cluster_retail = simbologia_unica(layer=zones_retail,
                                        **config.SIMBOLOGIA["Clusters_retail"]
                                        )

layer_isoarees = simbologia_graduada_QGIS(layer=isoarees,
                                          **config.SIMBOLOGIA["Isoarees"]
                                          )

## Comparativa concentracions diferents usos
# layer_cluster_retail - feta
#layer_cluster_office
#layer_cluster_public

#============================================================================================
# 7. Composició

## Composició general
layout_general = generar_layout(nom_layout="Ús dels edificis a Barcelona")

mapa_general = afegir_mapa(layout=layout_general,
                           capes=[layer_edificis, layer_barris, layer_districtes],
                           capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"])

titol_general = afegir_titol(layout=layout_general,
                             titol="Ús dels edificis de la ciutat de Barcelona - font: Cadastre",
                             font="Calibri",
                             size=20,
                             font_color=(0,0,0,255),
                             backg_color=(100,100,100,200),
                             frame_color=(255, 255, 255, 200))

llegenda_general = afegir_llegenda(layout=layout_general,
                                   mapa=mapa_general,
                                   titol="Classificació dels edificis",
                                   font="Calibri",
                                   size=10,
                                   font_color=(0,0,0,255),
                                   backg_color=(100,100,100,255))

escala_general = afegir_escala(layout=layout_general,
                               mapa=mapa_general,
                               font="Calibri",
                               font_color=(0,0,0,255))

nord_general = afegir_nord(layout=layout_general,
                           path="C:/projectes_git/Dades/nord2.png")

exportar_layout(layout=layout_general,
                output_path="C:/projectes_git/PyQGIS_practic/Resultats/Classificacio_edificis.pdf",
                dpi=150)

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

