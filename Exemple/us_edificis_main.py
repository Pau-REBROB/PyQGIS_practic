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
sys.path.append("C:/projectes_git/PyQGIS_practic/Exemple/simbologia")
sys.path.append("C:/projectes_git/PyQGIS_practic/Exemple/layouts")
sys.path.append("C:/projectes_git/PyQGIS_practic/Exemple/analisi")


import inicialitzacio
import importacio
import preparacio_dades
import analisi.agregacions as agregacions
import analisi.grafics as grafics
import analisi.clusters as clusters
import simbologia.simbologia_unica as simbologia_unica
import simbologia.simbologia_categorica as simbologia_categorica
import simbologia.simbologia_graduada as simbologia_graduada
import layouts.layout_common as layout_common
import layouts.layout_general as layout_general
import layouts.layout_atles as layout_atles
import layouts.fusionar_layouts as fusionar_layouts


## Funcions d'alt nivell en ANÀLISI i LAYOUT?

## Arxiu de configuració
import config


# Recàrrega
import importlib

importlib.reload(config)
importlib.reload(inicialitzacio)
importlib.reload(importacio)
importlib.reload(preparacio_dades)
importlib.reload(agregacions)
importlib.reload(grafics)
importlib.reload(clusters)
importlib.reload(simbologia_unica)
importlib.reload(simbologia_categorica)
importlib.reload(simbologia_graduada)
importlib.reload(layout_common)
importlib.reload(layout_general)
importlib.reload(layout_atles)
importlib.reload(fusionar_layouts)


# ==============================================================================
# 2. Inicialització

project, root = inicialitzacio.inicialitzar_projecte()

# ==============================================================================
# 3. Importació de capes

dict_layers, dict_indexs = importacio.carregar_capes(layers=config.LAYERS)

basemap_layer = importacio.carregar_basemap()

# ==============================================================================
# 4. Neteja de les dades

dict_layers_clean = preparacio_dades.netejar_grup(dict_layers=dict_layers, configuracio=config.CAMPS_MANTENIR)

# ==============================================================================
# 5. Anàlisi espacial

# Agregació de dades per districtes
dades_districtes = agregacions.resum_usos_districtes(
    edificis=dict_layers_clean["Cadastre"]["Edificis"],
    districtes=dict_layers_clean["Limits_administratius"]["Districtes"]
)

taula_districtes = agregacions.taula_usos_districtes(dades_districtes)
print(taula_districtes)

taula_percentatges = agregacions.percentatge_usos_districtes(taula_districtes)
print(taula_percentatges)

# Visualització dels resultats
grafics.grafic_usos_districtes(
    df=taula_districtes,
    output_path="C:/projectes_git/PyQGIS_practic/Resultats/Grafic_nombreEdificis_districte.png"
)

grafics.grafic_percentatge_usos_districtes(
    df=taula_percentatges,
    output_path="C:/projectes_git/PyQGIS_practic/Resultats/Grafic_percentatgeEdificis_districte.png"
)


####
# Clústers -> Anàlisi
# Zones -> Representació
retail = clusters.zones_cluster(layer=dict_layers_clean["Cadastre"]["Edificis"],
                                expressio=''' "currentUse" = '4_2_retail' ''',
                                eps=100,
                                min_size=5)
retail_clusters = retail["clusters"]
retail_zones = retail["zones"]

office = clusters.zones_cluster(layer=dict_layers_clean["Cadastre"]["Edificis"],
                                expressio='"currentUse" = \'4_1_office\'',
                                eps=100,
                                min_size=5)
office_clusters = office["clusters"]
office_zones = office["zones"]

public = clusters.zones_cluster(layer=dict_layers_clean["Cadastre"]["Edificis"],
                                expressio='"currentUse" = \'4_3_publicServices\'',
                                eps=100,
                                min_size=5)
public_clusters = public["clusters"]
public_zones = public["zones"]

## RESIDENCIAL VA UNA MICA APART
zones_residential = clusters.zones_cluster(layer=dict_layers_clean["Cadastre"]["Edificis"],
                                              expressio='"currentUse" = \'1_residential\'',
                                              eps=100,
                                              min_size=5) #EN AQUEST CAS, S'HAURIA DE MIRAR ELS PARÀMETRES

industrial = clusters.zones_cluster(layer=dict_layers_clean["Cadastre"]["Edificis"],
                                    expressio='"currentUse" = \'3_industrial\'',
                                    eps=100,
                                    min_size=5)
industrial_clusters = industrial["clusters"]
industrial_zones = industrial["zones"]


# Anàlisi de clústers
resum_retail = clusters.resum_clusters(retail_clusters)
resum_office = clusters.resum_clusters(office_clusters)
resum_public = clusters.resum_clusters(public_clusters)
resum_industrial = clusters.resum_clusters(industrial_clusters)

taula_retail = clusters.taula_clusters(
    resultats=resum_retail,
    us="Comerços"
)
print(taula_retail)



isoarees = clusters.isoarees_qneat3(graf_layer=dict_layers_clean["Graf"]["Graf_trams"],
                                            points_layer=zones_retail,
                                            strat=0,
                                            max_dist=5000,
                                            interval=250)

#============================================================================================
# 6. Simbologia
## Composició general (general + atles)
layer_districtes = simbologia_unica.simbologia_unica(layer=dict_layers_clean["Limits_administratius"]["Districtes"],
                                                         **config.SIMBOLOGIA["Districtes"]
                                                         )

layer_barris = simbologia_unica.simbologia_unica(layer=dict_layers_clean["Limits_administratius"]["Barris"],
                                                     **config.SIMBOLOGIA["Barris"]
                                                     )

layer_edificis = simbologia_categorica.simbologia_categorica(layer=dict_layers_clean["Cadastre"]["Edificis"],
                                                                 **config.SIMBOLOGIA["Edificis"]
                                                                 )

# Modificació dels noms
basemap_layer.setName("Fons cartogràfic CartoDB")
layer_districtes.setName("Districtes")
layer_barris.setName("Barris")
layer_edificis.setName("Ús dels edificis")
zones_office.setName("Clúster oficines")
zones_public.setName("Clúster serveis públics")
zones_retail.setName("Clúster comerços")
zones_residential.setName("Clúster residencial")
zones_industrial.setName("Clúster industrial")

# Addició de capes al projecte
QgsProject.instance().addMapLayer(basemap_layer)
QgsProject.instance().addMapLayer(layer_districtes)
QgsProject.instance().addMapLayer(layer_barris)
QgsProject.instance().addMapLayer(layer_edificis)
QgsProject.instance().addMapLayer(zones_residential)
QgsProject.instance().addMapLayer(zones_office)
QgsProject.instance().addMapLayer(zones_retail)
QgsProject.instance().addMapLayer(zones_public)
QgsProject.instance().addMapLayer(zones_industrial)


## Concentració activitat comercial
layer_graf = simbologia_unica.simbologia_unica_linia(layer=dict_layers_clean["Graf"]["Graf_trams"],
                                                         **config.SIMBOLOGIA["Graf"]
                                                         )

layer_cluster_retail = simbologia_unica.simbologia_unica(layer=zones_retail,
                                                             **config.SIMBOLOGIA["Clusters_retail"]
                                                             )

layer_isoarees = simbologia_graduada.simbologia_graduada_QGIS(layer=isoarees,
                                                                  **config.SIMBOLOGIA["Isoarees"]
                                                                  )

## Comparativa concentracions diferents usos
# layer_cluster_retail - feta
#layer_cluster_office
#layer_cluster_public

#============================================================================================
# 7. Composició

## Composició general
cfg_layout_general = config.LAYOUT["GENERAL"]

layout = layout_common.generar_layout(nom_layout="Ús dels edificis a Barcelona")

mapa_general = layout_general.afegir_mapa(
    layout=layout,
    capes=[layer_edificis, layer_barris, layer_districtes, basemap_layer],
    capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
)

titol_general = layout_common.afegir_titol(
    layout=layout,
    **cfg_layout_general["Titol"]
)

llegenda_general = layout_common.afegir_llegenda(
    layout=layout,
    mapa=mapa_general,
    **cfg_layout_general["Llegenda"]
)

escala_general = layout_common.afegir_escala(
    layout=layout,
    mapa=mapa_general,
    **cfg_layout_general["Escala"]
)

nord_general = layout_common.afegir_nord(
    layout=layout,
    mapa=mapa_general,
    **cfg_layout_general["Nord"]
)

layout_general.exportar_layout(
    layout=layout,
    **cfg_layout_general["Exportacio"]
)


## Composició atles
cfg_layout_atles = config.LAYOUT["ATLES"]

layout_a = layout_common.generar_layout(nom_layout="Ús dels edificis a Barcelona per districte")

mapa_atles = layout_atles.afegir_mapa(
    layout=layout_a,
    capes=[layer_edificis, layer_barris, layer_districtes, basemap_layer],
    capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
)

mapa_localitzador = layout_atles.afegir_mapa_localitzador(
    layout=layout_a,
    layer_location=layer_districtes,
    capa_extensio=dict_layers_clean["Limits_administratius"]["TermeMunicipal"],
    mapa=mapa_atles
)

titol_atles = layout_common.afegir_titol(
    layout=layout_a,
    **cfg_layout_atles["Titol"]
)

llegenda_atles = layout_common.afegir_llegenda(
    layout=layout_a,
    mapa=mapa_atles,
    **cfg_layout_atles["Llegenda"]
)

escala_general = layout_common.afegir_escala(
    layout=layout_a,
    mapa=mapa_atles,
    **cfg_layout_atles["Escala"]
)

nord_general = layout_common.afegir_nord(
    layout=layout_a,
    mapa=mapa_atles,
    **cfg_layout_atles["Nord"]
)

atles = layout_atles.generar_atles(
    layout=layout_a,
    capa_cobertura=dict_layers_clean["Limits_administratius"]["Districtes"],
    mapa=mapa_atles,
    **cfg_layout_atles["Generacio"]
)

layout_atles.exportar_atles(
    atlas=atles,
    **cfg_layout_atles["Exportacio"]
)


## Composició anàlisi
cfg_layout_analisi = config.LAYOUT["ANALISI"]

layout = layout_common.generar_layout(nom_layout="Anàlisi dels usos dels edificis a Barcelona")

mapa_analisi = layout_general.afegir_mapa(
    layout=layout,
    capes=[layer_edificis, layer_barris, layer_districtes, basemap_layer],
    capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
)

titol_analisi = layout_common.afegir_titol(
    layout=layout,
    **cfg_layout_analisi["Titol"]
)

llegenda_analisi = layout_common.afegir_llegenda(
    layout=layout,
    mapa=mapa_analisi,
    **cfg_layout_analisi["Llegenda"]
)

escala_analisi = layout_common.afegir_escala(
    layout=layout,
    mapa=mapa_analisi,
    **cfg_layout_analisi["Escala"]
)

nord_analisi = layout_common.afegir_nord(
    layout=layout,
    mapa=mapa_analisi,
    **cfg_layout_analisi["Nord"]
)

imatge_totals = layout_common.afegir_grafic(
    layout=layout,
    **cfg_layout_analisi["Grafic_total"]
)

imatge_percentatges = layout_common.afegir_grafic(
    layout=layout,
    **cfg_layout_analisi["Grafic_percentatge"]
)

layout_general.exportar_layout(
    layout=layout,
    **cfg_layout_analisi["Exportacio"]
)


## Unió de composicions
fusionar_layouts.fusionar_pdf(
    pdfs=[
        config.EXPORTACIO["Mapa_general"],
        config.EXPORTACIO["Atles"]
        ],
    output_path=config.EXPORTACIO["Informe"]
)

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



#========================================================================================
