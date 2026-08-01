"""ÚS EDIFICIS DE BARCELONA"""
"""Detecció automàtica de clústers comercials i anàlisi d'accessibilitat viària a Barcelona mitjançant PyQGIS i QNEAT3"""


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

"""
estructura:
    Importació → retorna capes.
    Anàlisi → retorna diccionaris de resultats.
    Simbologia → retorna capes simbolitzades.
    Layouts → consumeixen capes i exporten PDFs.
"""

"""
el mateix ordre per a cada script:

Docstring inicial del mòdul
Responsabilitat del mòdul.
Organització interna.
(Sense entrar en detalls d'implementació.)
Imports
Ordenats i sense import *.
Un element per línia si són molts.
Agrupats:
llibreries estàndard;
tercers (QGIS, pandas...);
mòduls propis.
Noms de funcions
Que siguin coherents amb la resta del projecte.
Verbs clars (carregar_, filtrar_, generar_, analisi_, exportar_...).
Variables internes
Només canviar-les si realment milloren la llegibilitat.
Evitar abreviatures poc clares.
Docstrings de les funcions
Mateix format a tot el projecte.
Especial atenció als dict i DataFrame, documentant-ne l'estructura.
Comentaris
Eliminar els que expliquen una línia evident.
Mantenir els que expliquen el perquè o un pas important de l'algoritme.
Petits refactors
Eliminar variables intermèdies innecessàries.
Simplificar retorns.
Evitar duplicació.
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
import analisi.espacialitzacio as especialitzacio
import analisi.hexagons as hexagons
import simbologia.simbologies as simbologies
import simbologia.simbologia_especialitzacio as simbologia_especialitzacio
import simbologia.simbologia_hexagons as simbologia_hexagons
import simbologia.simbologia_general as simbologia_general
import layouts.layout_common as layout_common
import layouts.layout_general as layout_general
import layouts.layout_atles as layout_atles
import layouts.layout_analisi as layout_analisi
import layouts.layout_clusters as layout_clusters
import layouts.layout_especialitzacio as layout_especialitzacio
import layouts.layout_bivariant_barris as layout_bivariant_barris
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
importlib.reload(especialitzacio)
importlib.reload(hexagons)
importlib.reload(simbologies)
importlib.reload(simbologia_especialitzacio)
importlib.reload(simbologia_hexagons)
importlib.reload(simbologia_general)
importlib.reload(layout_common)
importlib.reload(layout_general)
importlib.reload(layout_atles)
importlib.reload(layout_analisi)
importlib.reload(layout_clusters)
importlib.reload(layout_especialitzacio)
importlib.reload(layout_bivariant_barris)
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

dict_layers_clean = preparacio_dades.preparar_grup(dict_layers=dict_layers, configuracio=config.CAMPS_CAPES)

# ==============================================================================
# 5. Anàlisi espacial

# Agregació de dades per districtes
dict_districtes = agregacions.analisi_districtes(
    edificis=dict_layers_clean["Cadastre"]["Edificis"],
    districtes=dict_layers_clean["Limits_administratius"]["Districtes"]
)

# Visualització dels resultats
grafics.generar_grafics_districtes(
    resultats=dict_districtes
)


# Anàlisi d'agrupacions espacials (clústers)
dict_clusters = clusters.analisi_clusters(
    layer=dict_layers_clean["Cadastre"]["Edificis"],
    usos=config.USOS
)

taula_clusters = clusters.taula_general_clusters(
    resultats=dict_clusters
)

# Visualització dels resultats
grafics.generar_grafics_clusters(
    df=taula_clusters
)

# Funcions d'especialització funcional
## Districtes
resultats_especialitzacio = especialitzacio.analisi_especialitzacio(
    districtes=dict_layers_clean["Limits_administratius"]["Districtes"],
    edificis=dict_layers_clean["Cadastre"]["Edificis"]
)

resultats_especialitzacio_no_residencial = especialitzacio.analisi_especialitzacio(
    districtes=dict_layers_clean["Limits_administratius"]["Districtes"],
    edificis=dict_layers_clean["Cadastre"]["Edificis"],
    usos_exclosos=["1_residential"]
)

# Anàlisi bivariant 
#### CANVIAR NOMS
classificacio_no_residencial = especialitzacio.classificar_especialitzacio(
    resultats=resultats_especialitzacio_no_residencial
)

bivariant_no_residencial = especialitzacio.classificar_bivariant(
    resultats=classificacio_no_residencial
)

# Addició dels camps d'especialització a la capa de districtes
districtes_especialitzacio = especialitzacio.afegir_resultats_especialitzacio(
    districtes=dict_layers_clean["Limits_administratius"]["Districtes"],
    resultats=bivariant_no_residencial
)

districtes_especialitzacio_no_residencial = especialitzacio.afegir_resultats_especialitzacio(
    districtes=dict_layers_clean["Limits_administratius"]["Districtes"],
    resultats=bivariant_no_residencial
)

## Barris
resultats_especialitzacio = especialitzacio.analisi_especialitzacio(
    districtes=dict_layers_clean["Limits_administratius"]["Barris"],
    edificis=dict_layers_clean["Cadastre"]["Edificis"]
)

resultats_especialitzacio_no_residencial = especialitzacio.analisi_especialitzacio(
    districtes=dict_layers_clean["Limits_administratius"]["Barris"],
    edificis=dict_layers_clean["Cadastre"]["Edificis"],
    usos_exclosos=["1_residential"]
)

# Anàlisi bivariant 
#### CANVIAR NOMS
classificacio = especialitzacio.classificar_especialitzacio(
    resultats=resultats_especialitzacio
)
classificacio_no_residencial = especialitzacio.classificar_especialitzacio(
    resultats=resultats_especialitzacio_no_residencial
)

bivariant = especialitzacio.classificar_bivariant(
    resultats=classificacio
)
bivariant_no_residencial = especialitzacio.classificar_bivariant(
    resultats=classificacio_no_residencial
)

# Addició dels camps d'especialització a la capa de barris
barris_especialitzacio = especialitzacio.afegir_resultats_especialitzacio(
    districtes=dict_layers_clean["Limits_administratius"]["Barris"],
    resultats=bivariant
)

barris_especialitzacio_no_residencial = especialitzacio.afegir_resultats_especialitzacio(
    districtes=dict_layers_clean["Limits_administratius"]["Barris"],
    resultats=bivariant_no_residencial
)


# Hexàgons
malla_hex = hexagons.generar_malla_retallada(
    capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"],
    mida_hexagon=config.MIDA_HEXAGON
)

especialitzacio_no_residencial = hexagons.analisi_especialitzacio(
    malla=malla_hex,
    edificis=dict_layers_clean["Cadastre"]["Edificis"],
    expressio="\"currentUse\" <> '1_residential'"
)
especialitzacio_residencial = hexagons.analisi_especialitzacio(
    malla=malla_hex,
    edificis=dict_layers_clean["Cadastre"]["Edificis"]
)

espec_classificat_residencial = hexagons.classificar_especialitzacio(
    resultats=especialitzacio_residencial
)
espec_classificat_no_residencial = hexagons.classificar_especialitzacio(
    resultats=especialitzacio_no_residencial
)

bivariant_hex_residencial = hexagons.classificar_bivariant(
    resultats=espec_classificat_residencial
)
bivariant_hex_no_residencial = hexagons.classificar_bivariant(
    resultats=espec_classificat_no_residencial
)

hex_espec_residencial = hexagons.afegir_resultats_especialitzacio(
    malla=malla_hex,
    resultats=bivariant_hex_residencial
)
hex_espec_no_residencial = hexagons.afegir_resultats_especialitzacio(
    malla=malla_hex,
    resultats=bivariant_hex_no_residencial
)



####################
isoarees = clusters.isoarees_qneat3(graf_layer=dict_layers_clean["Graf"]["Graf_trams"],
                                            points_layer=zones_retail,
                                            strat=0,
                                            max_dist=5000,
                                            interval=250)

#============================================================================================
# 6. Simbologia
# Capes de base cartogràfica
layers_simbologia_base = simbologia_general.simbologia_base(
    dict_layers=dict_layers_clean
)

# Addició de capes al projecte
QgsProject.instance().addMapLayer(basemap_layer)

for layer in layers_simbologia_base.values():
    QgsProject.instance().addMapLayer(layer)


# Simbologia de les capes d'agrupacions espacials (clústers)
layers_simbologia_clusters = simbologia_general.simbologia_clusters(
    resultats=dict_clusters
)

# Addició de capes al projecte
for layer in layers_simbologia_clusters.values():
    QgsProject.instance().addMapLayer(layer)



# Simbologia d'anàlisi d'especialització per districtes
layers_especialitzacio = simbologia_general.simbologia_especialitzacio_funcional(
    districtes=districtes_especialitzacio
)

# Addició de capes al projecte
for layer in layers_especialitzacio.values():
    QgsProject.instance().addMapLayer(layer)

layers_especialitzacio_no_residencial = simbologia_general.simbologia_especialitzacio_funcional(
    districtes=districtes_especialitzacio_no_residencial
)

# Addició de capes al projecte
for layer in layers_especialitzacio_no_residencial.values():
    QgsProject.instance().addMapLayer(layer)


# Simbologia d'anàlisi d'especialització per barris
layers_especialitzacio = simbologia_general.simbologia_especialitzacio_funcional(
    districtes=barris_especialitzacio
)

# Addició de capes al projecte
for layer in layers_especialitzacio.values():
    QgsProject.instance().addMapLayer(layer)

layers_especialitzacio_no_residencial = simbologia_general.simbologia_especialitzacio_funcional(
    districtes=barris_especialitzacio_no_residencial
)

# Addició de capes al projecte
for layer in layers_especialitzacio_no_residencial.values():
    QgsProject.instance().addMapLayer(layer)


## Hexàgons
# Distribució de les dades
dominancies = []
shannon = []

for dades in especialitzacio.values():
    dominancies.append(dades["dominancia"])
    shannon.append(dades["shannon_normalitzat"])

min(dominancies)
max(dominancies)

min(shannon)
max(shannon)

sorted(dominancies)
sorted(shannon)

total = len(especialitzacio_no_residencial)

valids = sum(
    1 for d in especialitzacio_no_residencial.values()
    if d["n_edificis"] >= 3
)

print(valids, "/", total)
print(f"{valids/total*100:.1f}%")


layers_hexagons_especialitzacio_no_residencial = simbologia_general.simbologia_hexagons_especialitzacio_funcional(
    hexagons=hex_espec_no_residencial
)
# Addició de capes al projecte
for layer in layers_hexagons_especialitzacio_no_residencial.values():
    QgsProject.instance().addMapLayer(layer)



##############################
layer_graf = simbologia_unica.simbologia_unica_linia(layer=dict_layers_clean["Graf"]["Graf_trams"],
                                                         **config.SIMBOLOGIA["Graf"]
                                                         )

layer_isoarees = simbologia_graduada.simbologia_graduada_QGIS(layer=isoarees,
                                                                  **config.SIMBOLOGIA["Isoarees"]
                                                                  )

#============================================================================================
# 7. Composició

## Composició general
layout_general.composicio_general(
    capes=[
        layers_simbologia_base["Edificis"],
        layers_simbologia_base["Barris"],
        layers_simbologia_base["Districtes"],
        basemap_layer
    ],
    capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
)

## Composició atles
layout_atles.composicio_atles(
    capes=[
        layers_simbologia_base["Edificis"],
        layers_simbologia_base["Barris"],
        layers_simbologia_base["Districtes"],
        basemap_layer
    ],
    capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"],
    capa_cobertura=layers_simbologia_base["Districtes"]
)

## Composició anàlisi
layout_analisi.composicio_analisi(
    capes=[
        layers_simbologia_base["Edificis"],
        layers_simbologia_base["Barris"],
        layers_simbologia_base["Districtes"],
        basemap_layer
    ],
    capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
)

## Composició clusters
layout_clusters.composicio_clusters(
    capes=[
        *layers_simbologia_clusters.values(),
        layers_simbologia_base["Edificis"],
        layers_simbologia_base["Barris"],
        layers_simbologia_base["Districtes"],
        basemap_layer
    ],
    capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
)

## Composició especialització districtes
layout_especialitzacio.composicio_especialitzacio(
    capes=layers_especialitzacio_no_residencial,
    capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
)

## Composició bivariant barris
layout_bivariant_barris.composicio_bivariant_barris(
    districtes=dict_layers_clean["Limits_administratius"]["Districtes"],
    capes=layers_especialitzacio_no_residencial["bivariant"],
    capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
)


## Unió de composicions en un informe final
fusionar_layouts.fusionar_pdf(
    pdfs=[
        config.LAYOUTS["GENERAL"]["Exportacio"]["output_path"],
        config.LAYOUTS["ATLES"]["Exportacio"]["output_path"],
        config.LAYOUTS["ANALISI"]["Exportacio"]["output_path"],
        config.LAYOUTS["CLUSTERS"]["Exportacio"]["output_path"]
    ],
    output_path=f"{config.PATH_RESULTATS}/Informe_final.pdf"
)

#============================================================================================
