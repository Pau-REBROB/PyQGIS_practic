"""
Anàlisi geoespacial dels edificis industrials a Barcelona
========================================================================================

Script principal que orquestra el flux complet d'anàlisi:

    1. Inicialització del projecte QGIS i importació de mòduls
    2. Preparació de les capes base
        - Edificis (cadastre GML)
        - Malla hexagonal
        - Graf viari
        - Límits administratius (districtes i barris)
    3. Especialització funcional per hexàgon
        - Agrupació d'edificis per hexàgon
        - Càlcul de l'índex de Shannon i dominància
        - Escriptura dels resultats a la malla
    4. Anàlisi de clústers comercials i accessibilitat
        - Identificació de nuclis comercials (DBSCAN)
        - Càlcul d'isoàrees d'accessibilitat (QNEAT3)
        - Assignació de l'accessibilitat als edificis
        - Agregació de l'accessibilitat a la malla hexagonal
    5. Cartografia i exportació dels resultats
        - Aplicació de simbologia
        - Generació del layout
        - Exportació a PNG/PDF

Dades
-----
    Cadastre de Barcelona (GML)
    Institut Cartogràfic i Geològic de Catalunya
    Open Data BCN - Ajuntament de Barcelona (CC-BY 4.0)

Dependències
------------
    QGIS 3.44, PyQGIS, QNEAT3

Autor
-----
    Pau Rebull Robert
"""

"""
1. Crear Edificis_base (materialitzar + camps bàsics)
2. Join espacial Edificis_base ↔ Malla → afegir hex_id als edificis
3. DBSCAN sobre edificis retail → clusters
4. QNEAT3 sobre clusters → isoàrees
5. Assignar accessibilitat als edificis (isoàrees → edificis)
6. Calcular especialització per hexàgon (edificis → malla)
7. Calcular accessibilitat per hexàgon (edificis → malla)
8. Classificació bivariant (malla → malla)
9. Cartografia final
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

# ==============================================================================
# 1. MÒDULS
# ==============================================================================

# ------------------------------------------------------------------------------
# 1.1. Importació de mòduls
# ------------------------------------------------------------------------------

import importlib
from pathlib import Path
import sys

# Carpeta del main.py i altres scripts
# Intentar obtenir la ruta de l'arxiu, sinó utilitzar rutes absolutes
try:
    _base = Path(__file__).parent
except NameError:
    _base = Path("C:/projectes_git/PyQGIS_practic/Exemple")

# Rutes relatives als mòduls i scripts
sys.path.append(str(_base))
sys.path.append(str(_base / "analisi"))
sys.path.append(str(_base / "simbologia"))
sys.path.append(str(_base / "layouts"))


import inicialitzacio
import importacio
import preparacio_dades
import analisi.temporal as temporal
import analisi.agregacions as agregacions
import analisi.grafics as grafics
import analisi.clusters as clusters
import analisi.accessibilitat as accessibilitat 
import analisi.especialitzacio as especialitzacio
import analisi.hexagons as hexagons
import simbologia.simbologies as simbologies
import simbologia.simbologia_especialitzacio as simbologia_especialitzacio
import simbologia.simbologia_hexagons as simbologia_hexagons
import simbologia.simbologia_accessibilitat as simbologia_accessibilitat
import simbologia.simbologia_general as simbologia_general
import layouts.layout_common as layout_common
import layouts.layout_general as layout_general
import layouts.layout_atles as layout_atles
import layouts.layout_analisi as layout_analisi
import layouts.layout_clusters as layout_clusters
import layouts.layout_especialitzacio as layout_especialitzacio
import layouts.layout_bivariant_zones as layout_bivariant_zones
import layouts.layout_accessibilitat as layout_accessibilitat 
import layouts.fusionar_layouts as fusionar_layouts

# Arxiu de configuració
import config

# ------------------------------------------------------------------------------
# 1.2. Recàrrega de mòduls
# ------------------------------------------------------------------------------

_moduls = [
    config, inicialitzacio, importacio, preparacio_dades, temporal,
    agregacions, grafics, clusters, accessibilitat, especialitzacio,
    hexagons, simbologies, simbologia_especialitzacio,
    simbologia_hexagons, simbologia_accessibilitat, simbologia_general,
    layout_common, layout_general, layout_atles, layout_analisi,
    layout_clusters, layout_especialitzacio, layout_bivariant_zones,
    layout_accessibilitat, fusionar_layouts
]

for _modul in _moduls:
    importlib.reload(_modul)


# ==============================================================================
# 2. INICIALITZACIÓ
# ==============================================================================

# Inicialitza el projecte QGIS i retorna
# la instància del projecte (project) i l'arrel del panell de capes (root)
project, root = inicialitzacio.inicialitzar_projecte()


# ==============================================================================
# 3. IMPORTACIÓ DE CAPES
# ==============================================================================

# Carrega les capes vectorials definides a config.LAYERS
# Retorna un diccionari de capes i un diccionari d'índexs espacials
dict_layers = importacio.carregar_capes(layers=config.LAYERS)

# Carrega la capa de fons cartogràfic (CartoDB Positron No Labels)
basemap_layer = importacio.carregar_basemap()


# ==============================================================================
# 4. NETEJA DE LES DADES
# ==============================================================================

# Neteja les capes vectorials eliminant els camps no necessaris
# i guardant les còpies netes a disc com a GeoPackage

# Retorna un diccionari de capes netes
dict_layers_clean = preparacio_dades.preparar_grup(
    dict_layers=dict_layers,
    configuracio=config.CAMPS_CAPES
)

# Retorna un diccionari d'índex espacials de cada capa
dict_indexs = preparacio_dades.crear_indexs(
    dict_layers=dict_layers_clean
)


# ==============================================================================
# 5. ANÀLISI ESPACIAL
# ==============================================================================

# ------------------------------------------------------------------------------
# 5.1. Capes base del projecte
# ------------------------------------------------------------------------------

# Crea les capes base d'unitats administratives, així com d'edificis i 
# la malla hexagonal que serviran de suport per a totes les anàlisis posteriors
## Terme municipal
terme_base = dict_layers_clean["Limits_administratius"]["TermeMunicipal"]

## Districtes
districtes_base = dict_layers_clean["Limits_administratius"]["Districtes"]

## Barris
barris_base = dict_layers_clean["Limits_administratius"]["Barris"]

## Malla hexagonal
malla_base = hexagons.generar_malla_retallada(
    capa_extent=terme_base,
    mida_hexagon=config.MIDA_HEXAGON
)

## Edificis
edificis = dict_layers_clean["Cadastre"]["Edificis"]

## Edificis amb el seu barri i districte associat ???
##################

## Edificis amb el seu hexagon associat
edificis_base = hexagons.assignar_hexagons_a_edificis(
    edificis=edificis,
    malla=malla_base
)

# ------------------------------------------------------------------------------
# 5.2. Ús industrial
# ------------------------------------------------------------------------------

edificis_industrial = especialitzacio.filtrar_usos_edificis(
    edificis=edificis_base,
    expressio='"currentUse" = \'3_industrial\''
)

edificis_no_industrial = especialitzacio.filtrar_usos_edificis(
    edificis=edificis_base,
    expressio='"currentUse" != \'3_industrial\''
)

# ------------------------------------------------------------------------------
# 5.3. Exploració de les dades
# ------------------------------------------------------------------------------

# Edificis industrials
temporal.extreure_any_edificis(edificis_industrial)

# Distribució anys de construcció
# {
#     '<1859': 8,
#     '1859-1900': 20,
#     '1900-1936': 217,
#     '1936-1945': 127,
#     '1945-1960': 194,
#     '1960-1980': 752,
#     '1980-2000': 323,
#     '2000-2008': 51,
#     '2008-2015': 22,
#     '2015-2026': 33
# }

# Edificis no industrials
temporal.extreure_any_edificis(edificis_no_industrial)

# Distribució anys de construcció
# {
#     '<1859': 1193,
#     '1859-1900': 2801,
#     '1900-1936': 14891,
#     '1936-1945': 5466,
#     '1945-1960': 7540,
#     '1960-1980': 22967,
#     '1980-2000': 7533,
#     '2000-2008': 2900,
#     '2008-2015': 1213,
#     '2015-2026': 1217
# }

# Addició del camp "any_construcció"
edificis_industrial_net = temporal.afegir_any_construccio(edificis_industrial)
edificis_no_industrial_net = temporal.afegir_any_construccio(edificis_no_industrial)

# ------------------------------------------------------------------------------
# 5.4. Anàlisi industrial
# ------------------------------------------------------------------------------

# Densitat d'edificis industrials 
## Per Districte
agregacions.calcular_densitat_per_zona(
    edificis=edificis_industrial_net,
    idx_edificis=dict_indexs["Cadastre"]["Edificis"],
    camp_id_edifici="gml_id",
    zones=barris_base,
    camp_id_zona="fid"
)
# {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 3.7738088165542747, 8: 4.884259988464307, 9: 0.0, 10: 0.0, 11: 0.0, 
#  12: 2.9499610590344156, 13: 0.0, 14: 0.0, 15: 0.0, 16: 0.0, 17: 0.0, 18: 0.0, 19: 0.0, 20: 0.0, 21: 0.0, 
#  22: 0.0, 23: 0.0, 24: 0.0, 25: 0.0, 26: 0.0, 27: 0.0, 28: 0.0, 29: 0.0, 30: 0.0, 31: 0.0, 32: 0.0, 33: 0.0, 
#  34: 0.0, 35: 0.0, 36: 0.0, 37: 0.0, 38: 0.0, 39: 0.0, 40: 0.0, 41: 0.0, 42: 0.0, 43: 0.0, 44: 0.0, 45: 0.0, 
#  46: 2.2706834610293325, 47: 0.0, 48: 0.0, 49: 0.0, 50: 0.0, 51: 0.0, 52: 0.0, 53: 0.0, 54: 0.0, 55: 0.0, 56: 0.0, 
#  57: 0.0, 58: 0.0, 59: 0.0, 60: 0.0, 61: 0.0, 62: 0.0, 63: 0.0, 64: 0.0,
#   65: 0.0, 66: 0.0, 67: 0.0, 68: 0.0, 69: 0.0, 70: 0.0, 71: 0.0, 72: 0.0, 73: 0.0}
## Toca canviar el id de la zona pel NOM





#----------------
# Antiguitat dels edificis industrial
## Per exemple:
# abans de 1900
# 1900–1945
# 1946–1975
# 1976–2000
# 2001–2010
# 2011–actualitat


# Any de construcció de tots els edificis de Barcelona vs any de construcció dels edificis industrials actuals
## La indústria que queda a Barcelona és més antiga que el parc edificat general?


# concentració d'edificis industrials per districte/barri.


# Accessibilitat?



# ------------------------------------------------------------------
# # ------------------------------------------------------------------------------
# # 5.2. Agrupacions espacials - clústers
# # ------------------------------------------------------------------------------

# clusters_dict = clusters.analisi_clusters(
#     layer=edificis_base,
#     usos=config.USOS
# )

# # ------------------------------------------------------------------------------
# # 5.3. Especialització funcional - Dominància i diversitat funcional
# # ------------------------------------------------------------------------------

# ## Districtes
# resultats_especialitzacio_districtes = especialitzacio.analisi_especialitzacio(
#     zones=districtes_base,
#     edificis=edificis_base,
#     idx_zones=dict_indexs["Limits_administratius"]["Districtes"],
#     usos_exclosos=["1_residential", "2_agriculture"]
# )
# # Addició dels camps d'especialització
# districtes_especialitzacio = especialitzacio.afegir_resultats_especialitzacio(
#     zones=districtes_base,
#     resultats=resultats_especialitzacio_districtes
# )

# ## Barris
# resultats_especialitzacio_barris = especialitzacio.analisi_especialitzacio(
#     zones=barris_base,
#     edificis=edificis_base,
#     idx_zones=dict_indexs["Limits_administratius"]["Barris"],
#     usos_exclosos=["1_residential", "2_agriculture"]
# )
# # Addició dels camps d'especialització
# barris_especialitzacio = especialitzacio.afegir_resultats_especialitzacio(
#     zones=barris_base,
#     resultats=resultats_especialitzacio_barris
# )

# # Assignar els camps d'especialització a la malla a partir dels edificis
# malla_especialitzacio = especialitzacio.assignar_especialitzacio_per_hexagons(
#     edificis=edificis_base,
#     malla=malla_base,
#     usos_exclosos=['1_residential', "2_agriculture"]
# )

# # ------------------------------------------------------------------------------
# # 5.4. Anàlisi bivariant dominància i diversitat funcional
# # ------------------------------------------------------------------------------

# malla_especialitzacio_bivariantDDF = especialitzacio.afegir_classe_bivariant_DF_D(
#     layer=malla_especialitzacio
# )

# # ------------------------------------------------------------------------------
# # 5.4. Accessibilitat
# # ------------------------------------------------------------------------------

# # Comerços - 4_2_retail
# clusters_retail = clusters_dict["4_2_retail"]["clusters"]
# # Serveis públics - 4_3_publicServices
# clusters_publicS = clusters_dict["4_3_publicServices"]["clusters"]

# # Càlcul d'isoàrees d'accessibilitat
# isoarees = accessibilitat.analisi_accessibilitat(
#     graf=dict_layers_clean["Graf"]["Graf_trams"],
#     origen=clusters_publicS
# )

# # Assignar el valor d'accessibilitat de les isoàrees als edificis
# edificis_accessibilitat = accessibilitat.assignar_isoarees_a_edificis(
#     edificis=edificis_base,
#     isoarees=isoarees
# )

# # Assignar el valor d'accessibilitat dels edificis a la malla hexagonal
# malla_accessibilitat = accessibilitat.assignar_accessibilitat_per_hexagons(
#     edificis=edificis_accessibilitat,
#     malla=malla_especialitzacio
# )

# # ------------------------------------------------------------------------------
# # 5.5. Anàlisi bivariant
# # ------------------------------------------------------------------------------

# ## Districtes
# districtes_bivariant_DF_A = especialitzacio.afegir_classe_bivariant_DF_A(
#     layer=districtes_especialitzacio
# )

# ## Barris
# barris_bivariant_DF_A = especialitzacio.afegir_classe_bivariant_DF_A(
#     layer=barris_especialitzacio
# )

# ## Malla hexagonal
# malla_bivariant_DF_A = especialitzacio.afegir_classe_bivariant_DF_A(
#     layer=malla_accessibilitat
# )

# # Separar els hexàgons vàlids dels no vàlids - aquells amb el camp
# # de l'anàlisi bivariant NULL
# hexagons_valids_DF_A, hexagons_no_valids_DF_A = hexagons.separar_hexagons_valids(
#     malla=malla_bivariant_DF_A
# )

# # ------------------------------------------------------------------------------
# # 5.2. Agregacions zonals - APARCAT FINS A ANYS DE CONSTRUCCIÓ
# # ------------------------------------------------------------------------------

# districtes_agregacions = agregacions.analisi_usos_zones(
#     edificis=edificis_base,
#     zones=districtes_base,
#     idx_zones=dict_indexs["Limits_administratius"]["Districtes"]
# )

# barris_agregacions = agregacions.analisi_usos_zones(
#     edificis=edificis_base,
#     zones=barris_base,
#     idx_zones=dict_indexs["Limits_administratius"]["Barris"]
# )


# ==============================================================================
# 6. SIMBOLOGIA
# ==============================================================================

# ------------------------------------------------------------------------------
# 6.1. Base cartogràfica
# ------------------------------------------------------------------------------

layers_simbologia_base = simbologia_general.simbologia_base(
    dict_layers=dict_layers_clean
)

# Capa base CartoDB Positron No Labels
basemap_layer

# ------------------------------------------------------------------------------
# 6.2. Edificis industrials
# ------------------------------------------------------------------------------

layers_simbologia_atles = simbologia_general.simbologia_atles(
    edificis=edificis_base,
    districtes=districtes_base
)

# ------------------------------------------------------------------------------
# 6.2. Agrupacions espacials - clústers
# ------------------------------------------------------------------------------

# Clústers
layers_simbologia_clusters = simbologia_general.simbologia_clusters(
    resultats=clusters_dict
)

# Zones
layers_simbologia_zones = simbologia_general.simbologia_zones(
    resultats=clusters_dict
)

# ------------------------------------------------------------------------------
# 6.3. Especialització funcional - Dominància / Diversitat funcional
# ------------------------------------------------------------------------------

# Omissió dels usos residencial i agricultura

## Districtes
layers_simbologia_especialitzacio_districtes = simbologia_general.simbologia_especialitzacio_funcional(
    zones=districtes_especialitzacio,
    ua="Districtes"
)

## Barris
layers_simbologia_especialitzacio_barris = simbologia_general.simbologia_especialitzacio_funcional(
    zones=barris_especialitzacio,
    ua="Barris"
)

## Malla hexagonal
layers_simbologia_especialitzacio_hexagons = simbologia_general.simbologia_hexagons_especialitzacio_funcional(
    hexagons=malla_especialitzacio_bivariantDDF,
    terme=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
)

# ------------------------------------------------------------------------------
# 6.4. Accessibilitat
# ------------------------------------------------------------------------------

layers_simbologia_accessibilitat = simbologia_general.simbologia_composicio_accessibilitat(
    edificis=edificis_accessibilitat,
    graf=dict_layers_clean["Graf"]["Graf_trams"],
    clusters=clusters_publicS,
    terme=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
)

# ------------------------------------------------------------------------------
# 6.4. Anàlisi bivariant Diversitat funcional - Accessibilitat
# ------------------------------------------------------------------------------

## Malla hexagonal - hexàgons vàlids
layers_simbologia_bivariant_valids = simbologia_general.simbologia_hexagons_especialitzacio_funcional(
    hexagons=hexagons_valids_DF_A
)

## Malla hexagonal - hexàgons no vàlids
layer_simbologia_bivariant_no_valids = simbologies.simbologia_unica(
    layer=hexagons_no_valids_DF_A,
    **config.SIMBOLOGIA["Hexagons_no_valids"]
)

# ------------------------------------------------------------------------------
# 6.5. Addició de capes al projecte
# ------------------------------------------------------------------------------

totes_les_capes = {
    **layers_simbologia_base,
    "base_map": basemap_layer,
    **layers_simbologia_atles,
    **layers_simbologia_clusters,
    **layers_simbologia_zones,
    # **layers_simbologia_especialitzacio_districtes,
    # **layers_simbologia_especialitzacio_barris,
    # **layers_simbologia_especialitzacio_hexagons["hexagons"],
    # "terme_hexagons": layers_simbologia_especialitzacio_hexagons["terme_municipal"],
    # **layers_simbologia_accessibilitat,
    # **layers_simbologia_bivariant_valids,
    # "hexagons_no_valids_DF_A": layer_simbologia_bivariant_no_valids
}

for capa in totes_les_capes.values():

    # Afegir al projecte si no hi és
    if not project.mapLayer(capa.id()):
        project.addMapLayer(capa)
    
    # Activar la visibilitat sempre
    node = root.findLayer(capa)
    if node:
        node.setItemVisibilityChecked(True)


# ==============================================================================
# 7. COMPOSICIONS
# ==============================================================================

# ------------------------------------------------------------------------------
# 7.1. Composició general
# ------------------------------------------------------------------------------

layout_general.composicio_general(
    capes=[
        layers_simbologia_base["TermeMunicipal"],
        layers_simbologia_base["Edificis"],
        basemap_layer
    ],
    capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"],
    capes_llegenda=[layers_simbologia_base["Edificis"]]
)

# ------------------------------------------------------------------------------
# 7.2. Composició atles
# ------------------------------------------------------------------------------

layout_atles.composicio_atles(
    districtes=districtes_base,
    capes=[
        layers_simbologia_atles["Districtes"],
        layers_simbologia_atles["Edificis"],
        basemap_layer
    ],
    capa_extent=terme_base,
    capa_cobertura=districtes_base
)

# # ------------------------------------------------------------------------------
# # 7.3. Composició anàlisi agrupacions espacials serveis públics
# # ------------------------------------------------------------------------------

# layout_clusters.composicio_clusters(
#     capes=[
#         layers_simbologia_zones['4_2_retail'],
#         layers_simbologia_base["TermeMunicipal"],
#         layers_simbologia_base["Edificis"],
#         basemap_layer
#     ],
#     capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
# )

# ------------------------------------------------------------------------------
# 7.4. Composicions especialització funcional
# ------------------------------------------------------------------------------

layout_especialitzacio.composicio_especialitzacio(
    capes=layers_simbologia_especialitzacio_hexagons["hexagons"],
    capa_terme=layers_simbologia_especialitzacio_hexagons["terme_municipal"],
    capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
)

# ------------------------------------------------------------------------------
# 7.5. Composició d'accessibilitat
# ------------------------------------------------------------------------------

layout_accessibilitat.composicio_accessibilitat(
    capes=[
        layers_simbologia_zones["4_3_publicServices"],
        layers_simbologia_accessibilitat["clusters"],
        layers_simbologia_accessibilitat["accessibilitat"],
        layers_simbologia_accessibilitat["terme"],
        layers_simbologia_accessibilitat["graf"]
    ],
    capa_extent=layers_simbologia_accessibilitat["clusters"]
)

# ------------------------------------------------------------------------------
# 7.6. Composició anàlisi bivariant
# ------------------------------------------------------------------------------

## Malla hexagonal
layout_bivariant_zones.composicio_bivariant_zones(
    zona="Hexagons",
    districtes=districtes_base,
    capes=[
        layers_simbologia_bivariant_valids["bivariant"],
        layer_simbologia_bivariant_no_valids
    ],
    capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"],
    amb_capçalera=False
)

# ------------------------------------------------------------------------------
# 7.7. Composició final
# ------------------------------------------------------------------------------

## Unió de composicions en un informe final
fusionar_layouts.fusionar_pdf(
    pdfs=[
        config.LAYOUTS["GENERAL"]["Exportacio"]["output_path"],
        config.LAYOUTS["ATLES"]["Exportacio"]["output_path"],
        config.LAYOUTS["CLUSTERS"]["Exportacio"]["output_path"],
        config.LAYOUTS["ESPECIALITZACIO"]["Exportacio"]["output_path"],
        config.LAYOUTS["ACCESSIBILITAT"]["Exportacio"]["output_path"],
        config.LAYOUTS["BIVARIANT"]["Hexagons"]["Exportacio"]["output_path"]
    ],
    output_path=f"{config.PATH_RESULTATS}/Informe_final.pdf"
)





# -------------------------------------


accessibilitat.distribucio_distancia(layers_simbologia_accessibilitat["accessibilitat"])
accessibilitat.frequencies(layers_simbologia_accessibilitat["accessibilitat"])