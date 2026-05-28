"""GENERACIÓ DE CARTOGRAFIA"""

# Importació de les funcions definides en els scripts de simbologia
import sys
sys.path.append("C:/projectes_git/PyQGIS_practic/Exemple")

from simbologia_unica_2_1 import simbologia_unica, simbologia_unica_linia
from simbologia_categorica_2_2 import simbologia_categorica
#from simbologia_graduada_2_3 import simbologia_graduada_QGIS
#from simbologia_graduada_manual_2_4 import simbologia_graduada_manual


# QUINS LAYOUTS VULL CREAR?
## simbologia única per tenir de fons les divisions administratives
## simbologia categòrica --> ús dels edificis / barris,districtes
## simbologia graduada --> altura dels edificis / àrea barris,districtes / població (CAL AFEGIR-LA)
## simbologia regles --> els barris amb més,menys àrea o població / edificis amb més,menys plantes

# Aplicació de les funcions per generar la cartografia
## Ús dels edificis a Barcelona - segons cadastre / Simbologia categòrica
layer_base_districtes = simbologia_unica(
    dict_layers["Limits_administratius"]["Districtes"],
    (0,0,0,0),
    0.4,
    (0,0,0,255)
)

layer_base_barris = simbologia_unica(
    dict_layers["Limits_administratius"]["Barris"],
    (0,0,0,0),
    0.2,
    (0,0,0,255)
)

layer_us_edificis = simbologia_categorica(
    dict_layers["Cadastre"]["Edificis"],
    currentUse,
    ['red','orange','yellow','green'],
    0.15,
    "white"
)

# Generació del layout
layout = QgsPrintLayout(project)
layout.initializeDefaults()
layout.setName("Ús dels edificis")

map = QgsLayoutItemMap(layout)
map.attemptResize(QgsLayoutSize(200,200,QgsUnitTypes.LayoutMillimeters))
#map.attemptMove(QgsLayoutPoint(x,y,units))
extent = project.layerTreeRoot().extent()
map.setExtent(extent)
map.zoomToExtent(extent)
layout.addLayoutItem(map)

legend = QgsLayoutItemLegend(layout)
legend.setLinkedMap(map)
#legend.attemptResize(QgsLayoutSize(x,y,units))
legend.attemptMove(QgsLayoutPoint(205,100,QgsUnitTypes.LayoutMillimeters))
legend.setTitle("Classificació dels usos dels edificis de Barcelona")
legend.setAutoUpdateModel(True) 
layout.addLayoutItem(legend)

scale = QgsLayoutItemScaleBar(layout)
scale.setLinkedMap(map)
#scale.attemptResize(QgsLayoutSize(x,y,units))
scale.attemptMove(QgsLayoutPoint(205,180,QgsUnitTypes.LayoutMillimeters))
scale.applyDefaultSize()
scale.setStyle("Line Ticks Up")  
layout.addLayoutItem(scale)

manager = project.layoutManager()
manager.addLayout(layout)

exporter = QgsLayoutExporter(layout)
exporter.exportToImage("C:/projectes_git/PyQGIS_practic/Resultats/Classificacio_edificis.png", QgsLayoutExporter.ImageExportSettings())
