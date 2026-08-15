"""
Anàlisi geoespacial de la distribució funcional i l'accessibilitat comercial a Barcelona
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
import layouts.layout_hexagons as layout_hexagons
import layouts.layout_accessibilitat as layout_accessibilitat 
import layouts.fusionar_layouts as fusionar_layouts

# Arxiu de configuració
import config

# ------------------------------------------------------------------------------
# 1.2. Recàrrega de mòduls
# ------------------------------------------------------------------------------

_moduls = [
    config, inicialitzacio, importacio, preparacio_dades,
    agregacions, grafics, clusters, accessibilitat, especialitzacio,
    hexagons, simbologies, simbologia_especialitzacio,
    simbologia_hexagons, simbologia_accessibilitat, simbologia_general,
    layout_common, layout_general, layout_atles, layout_analisi,
    layout_clusters, layout_especialitzacio, layout_bivariant_zones,
    layout_hexagons, layout_accessibilitat, fusionar_layouts
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
dict_layers, dict_indexs = importacio.carregar_capes(layers=config.LAYERS)

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


# ==============================================================================
# 5. ANÀLISI ESPACIAL
# ==============================================================================

# ------------------------------------------------------------------------------
# 5.1. Capes base del projecte
# ------------------------------------------------------------------------------

# Crea les capes base d'edificis i malla hexagonal
# que serviran de suport per a totes les anàlisis posteriors
## Districtes
districtes_base = dict_layers_clean["Limits_administratius"]["Districtes"]

## Barris
barris_base = dict_layers_clean["Limits_administratius"]["Barris"]

## Malla hexagonal
malla_base = hexagons.generar_malla_retallada(
    capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"],
    mida_hexagon=config.MIDA_HEXAGON
)

## Edificis
edificis = dict_layers_clean["Cadastre"]["Edificis"]

## Edificis amb el seu hexagon associat
edificis_base = hexagons.assignar_hexagons_a_edificis(
    edificis=edificis,
    malla=malla_base
)

# ------------------------------------------------------------------------------
# 5.2. Agregacions zonals
# ------------------------------------------------------------------------------

districtes_agregacions = agregacions.analisi_usos_zones(
    edificis=edificis_base,
    zones=districtes_base
)

barris_agregacions = agregacions.analisi_usos_zones(
    edificis=edificis_base,
    zones=barris_base
)

# ------------------------------------------------------------------------------
# 5.3. Agrupacions espacials - clústers
# ------------------------------------------------------------------------------

clusters_dict = clusters.analisi_clusters(
    layer=edificis_base,
    usos=config.USOS
)

# ------------------------------------------------------------------------------
# 5.4. Accessibilitat àrees comercials
# ------------------------------------------------------------------------------

# Clústers comercials - 4_2_retail
clusters_retail = clusters_dict["4_2_retail"]["clusters"]

isoarees_retail = accessibilitat.analisi_accessibilitat(
    graf=dict_layers_clean["Graf"]["Graf_trams"],
    origen=clusters_retail
)

edificis_accessibilitat = accessibilitat.assignar_isoarees_a_edificis(
    edificis=edificis_base,
    isoarees=isoarees_retail
)

malla_accessibilitat = accessibilitat.assignar_accessibilitat_per_hexagons(
    edificis=edificis_accessibilitat,
    malla=malla_base
)

# ------------------------------------------------------------------------------
# 5.5. Especialització funcional
# ------------------------------------------------------------------------------

# Calcula la diversitat i dominància d'usos per cada districte, barri i hexagon
# a partir dels edificis base
# L'índex de Shannon mesura la diversitat funcional 
# i la dominància identifica l'ús predominant

# Conservant l'ús residencial - 1_residential
## Districtes
resultats_especialitzacio_districtes = especialitzacio.analisi_especialitzacio(
    zones=districtes_base,
    edificis=edificis_base
)
# Addició dels camps d'especialització
districtes_especialitzacio = especialitzacio.afegir_resultats_especialitzacio(
    zones=districtes_base,
    resultats=resultats_especialitzacio_districtes
)

## Barris
resultats_especialitzacio_barris = especialitzacio.analisi_especialitzacio(
    zones=barris_base,
    edificis=edificis_base
)
# Addició dels camps d'especialització
barris_especialitzacio = especialitzacio.afegir_resultats_especialitzacio(
    zones=barris_base,
    resultats=resultats_especialitzacio_barris
)


# Excloent l'ús residencial
## Districtes
resultats_especialitzacio_no_residencial_districtes = especialitzacio.analisi_especialitzacio(
    zones=districtes_base,
    edificis=edificis_base,
    usos_exclosos=["1_residential"]
)
# Addició dels camps d'especialització
districtes_especialitzacio_no_residencial = especialitzacio.afegir_resultats_especialitzacio(
    zones=districtes_base,
    resultats=resultats_especialitzacio_no_residencial_districtes
)

## Barris
resultats_especialitzacio_no_residencial_barris = especialitzacio.analisi_especialitzacio(
    zones=barris_base,
    edificis=edificis_base,
    usos_exclosos=["1_residential"]
)
# Addició dels camps d'especialització
barris_especialitzacio_no_residencial = especialitzacio.afegir_resultats_especialitzacio(
    zones=barris_base,
    resultats=resultats_especialitzacio_no_residencial_barris
)


# Assignar l'especialització a la malla
malla_especialitzacio = especialitzacio.assignar_especialitzacio_per_hexagons(
    edificis=edificis_accessibilitat,
    malla=malla_accessibilitat
)

## Excloent l'ús residencial
malla_especialitzacio_no_residencial = especialitzacio.assignar_especialitzacio_per_hexagons(
    edificis=edificis_accessibilitat,
    malla=malla_accessibilitat,
    usos_exclosos=['1_residential']
)

# ------------------------------------------------------------------------------
# 5.6. Anàlisi bivariant
# ------------------------------------------------------------------------------

## Districtes
districtes_bivariant = especialitzacio.afegir_classe_bivariant(
    layer=districtes_especialitzacio_no_residencial
)

## Barris
barris_bivariant = especialitzacio.afegir_classe_bivariant(
    layer=barris_especialitzacio_no_residencial
)

## Malla
malla_bivariant = especialitzacio.afegir_classe_bivariant(
    layer=malla_especialitzacio_no_residencial
)

# ------------------------------------------------------------------------------
# 5.7. Malla hexagonal - hexgrid
# ------------------------------------------------------------------------------

# Omissió ús residencial
hexagons_valids, hexagons_no_valids = hexagons.separar_hexagons_valids(
    malla=malla_bivariant
)


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

# Addició de capes al projecte
for layer in layers_simbologia_base.values():
    project.addMapLayer(layer)

project.addMapLayer(basemap_layer)

# ------------------------------------------------------------------------------
# 6.2. Agrupacions espacials - clústers
# ------------------------------------------------------------------------------

layers_simbologia_clusters = simbologia_general.simbologia_clusters(
    resultats=clusters_dict
)

# Addició de capes al projecte
for layer in layers_simbologia_clusters.values():
    project.addMapLayer(layer)

# ------------------------------------------------------------------------------
# 6.3. Especialització funcional
# ------------------------------------------------------------------------------

# Omissió de l'ús residencial
## Districtes
layers_simbologia_especialitzacio_districtes = simbologia_general.simbologia_especialitzacio_funcional(
    zones=districtes_bivariant,
    ua="Districtes"
)

# Addició de capes al projecte
for layer in layers_simbologia_especialitzacio_districtes.values():
    project.addMapLayer(layer)


## Barris
layers_simbologia_especialitzacio_barris = simbologia_general.simbologia_especialitzacio_funcional(
    zones=barris_bivariant,
    ua="Barris"
)

# Addició de capes al projecte
for layer in layers_simbologia_especialitzacio_barris.values():
    project.addMapLayer(layer)

# ------------------------------------------------------------------------------
# 6.4. Malla hexagonal bivariant
# ------------------------------------------------------------------------------

# Omissió de l'ús residencial
## Hexàgons
layers_simbologia_hexagons = simbologia_general.simbologia_hexagons_especialitzacio_funcional(
    hexagons=hexagons_valids
)

# Addició de capes al projecte
for layer in layers_simbologia_hexagons.values():
    project.addMapLayer(layer)

## Hexàgons no vàlids
layer_simbologia_hexagons_no_valids = simbologies.simbologia_unica(
    layer=hexagons_no_valids,
    **config.SIMBOLOGIA["Hexagons_no_valids"]
)

# Addició de capes al projecte
project.addMapLayer(layer_simbologia_hexagons_no_valids)

# ------------------------------------------------------------------------------
# 6.5. Accessibilitat
# ------------------------------------------------------------------------------

layers_simbologia_accessibilitat = simbologia_general.simbologia_edificis_accessibilitat(
    edificis=edificis_accessibilitat,
    graf=dict_layers_clean["Graf"]["Graf_trams"],
    clusters=clusters_dict["4_2_retail"]["zones"],
    terme=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
)

# Addició de les capes al projecte
for layer in layers_simbologia_accessibilitat.values():
    project.addMapLayer(layer)

# ------------------------------------------------------------------------------
# 6.6. Addició de capes al projecte
# ------------------------------------------------------------------------------

totes_les_capes = {
    **layers_simbologia_base,
    "base_map": basemap_layer,
    **layers_simbologia_clusters,
    **layers_simbologia_especialitzacio_districtes,
    **layers_simbologia_especialitzacio_barris,
    **layers_simbologia_hexagons,
    "hexagons_no_valids": layer_simbologia_hexagons_no_valids,
    **layers_simbologia_accessibilitat
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
        layers_simbologia_base["Edificis"],
        layers_simbologia_base["Barris"],
        layers_simbologia_base["Districtes"],
        basemap_layer
    ],
    capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
)

# ------------------------------------------------------------------------------
# 7.2. Composició atles
# ------------------------------------------------------------------------------

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

# # ------------------------------------------------------------------------------
# # 7.3. Composició anàlisi agrupacions espacials
# # ------------------------------------------------------------------------------

# layout_analisi.composicio_analisi(
#     capes=[
#         layers_simbologia_base["Edificis"],
#         layers_simbologia_base["Barris"],
#         layers_simbologia_base["Districtes"],
#         basemap_layer
#     ],
#     capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
# )

# ------------------------------------------------------------------------------
# 7.3. Composició anàlisi agrupacions espacials
# ------------------------------------------------------------------------------

layout_clusters.composicio_clusters(
    capes=[
        layers_simbologia_clusters["2_agriculture"],
        layers_simbologia_clusters["3_industrial"],
        layers_simbologia_clusters["4_1_office"],
        layers_simbologia_clusters["4_2_retail"],
        layers_simbologia_clusters["4_3_publicServices"],
        layers_simbologia_base["Edificis"],
        layers_simbologia_base["Barris"],
        layers_simbologia_base["Districtes"],
        basemap_layer
    ],
    capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
)

# ------------------------------------------------------------------------------
# 7.3. Composicions especialització funcional - Anàlisi bivariant
# ------------------------------------------------------------------------------

# ## Districtes
# layout_especialitzacio.composicio_especialitzacio(
#     capes=districtes_especialitzacio_no_residencial,
#     capa_extent=districtes_base
# )

## Districtes
layout_bivariant_zones.composicio_bivariant_zones(
    zona="Districtes",
    capes=layers_simbologia_especialitzacio_districtes["bivariant"],
    capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
)

## Barris
layout_bivariant_zones.composicio_bivariant_zones(
    zona="Barris",
    districtes=districtes_base,
    capes=layers_simbologia_especialitzacio_barris["bivariant"],
    capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
)


### LAYOUT COMPARATIU DISTRICTES / BARRIS
### aprofitar el d'especialització


## Malla hexagonal
layout_hexagons.composicio_bivariant_hexagons(
    districtes=districtes_base,
    capes=[
        layers_simbologia_hexagons["bivariant"],
        layer_simbologia_hexagons_no_valids
    ],
    capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
)

# ------------------------------------------------------------------------------
# 7.4. Composició d'accessibilitat
# ------------------------------------------------------------------------------

layout_accessibilitat.composicio_accessibilitat(
    capes=[
        layers_simbologia_accessibilitat["clusters"],
        layers_simbologia_accessibilitat["accessibilitat"],
        layers_simbologia_accessibilitat["terme"]
        #layers_accessibilitat["graf"]
    ],
    capa_extent=layers_simbologia_accessibilitat["clusters"]
)

# ------------------------------------------------------------------------------
# 7.5. Composició final
# ------------------------------------------------------------------------------

## Unió de composicions en un informe final
fusionar_layouts.fusionar_pdf(
    pdfs=[
        config.LAYOUTS["GENERAL"]["Exportacio"]["output_path"],
        config.LAYOUTS["ATLES"]["Exportacio"]["output_path"],
        config.LAYOUTS["CLUSTERS"]["Exportacio"]["output_path"],
        config.LAYOUTS["BIVARIANT"]["Districtes"]["Exportacio"]["output_path"],
        config.LAYOUTS["BIVARIANT"]["Barris"]["Exportacio"]["output_path"],
        config.LAYOUTS["HEXAGONS"]["Exportacio"]["output_path"],
        config.LAYOUTS["ACCESSIBILITAT"]["Exportacio"]["output_path"]
    ],
    output_path=f"{config.PATH_RESULTATS}/Informe_final.pdf"
)

