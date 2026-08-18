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
1. Què hi ha a Barcelona?
↓
2. Com es distribueix?
↓
3. On es concentra?
↓
4. Quines zones estan especialitzades?
↓
5. Quines són més diverses?
↓
6. Són també les més accessibles?
↓
7. En quin tipus de parc edificatori es produeixen aquests patrons?
↓
8. Què ens diu tot plegat sobre Barcelona?
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

# Crea les capes base d'edificis i malla hexagonal que serviran de suport
#  per a totes les anàlisis posteriors
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
    zones=districtes_base,
    idx_zones=dict_indexs["Limits_administratius"]["Districtes"]
)

barris_agregacions = agregacions.analisi_usos_zones(
    edificis=edificis_base,
    zones=barris_base,
    idx_zones=dict_indexs["Limits_administratius"]["Barris"]
)

# ------------------------------------------------------------------------------
# 5.5. Especialització funcional
# ------------------------------------------------------------------------------

# Calcula la diversitat i dominància d'usos per cada districte, barri i hexagon
# a partir dels edificis base
# L'índex de Shannon mesura la diversitat funcional 
# La dominància identifica l'ús predominant

# L'ús residencial queda omès de l'anàlisi al ser l'ús predominant amb diferència
# L'ús agricultura també queda omès per la seva baixa presència

# # Conservant l'ús residencial - 1_residential
# ## Districtes
# resultats_especialitzacio_districtes = especialitzacio.analisi_especialitzacio(
#     zones=districtes_base,
#     edificis=edificis_base,
#     idx_zones=dict_indexs["Limits_administratius"]["Districtes"]
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
#     idx_zones=dict_indexs["Limits_administratius"]["Barris"]
# )
# # Addició dels camps d'especialització
# barris_especialitzacio = especialitzacio.afegir_resultats_especialitzacio(
#     zones=barris_base,
#     resultats=resultats_especialitzacio_barris
# )

# # Assignar els camps d'especialització a la malla a partir dels edificis
# malla_especialitzacio = especialitzacio.assignar_especialitzacio_per_hexagons(
#     edificis=edificis_accessibilitat_publicS,
#     malla=malla_accessibilitat_publicS
# )


## Districtes
resultats_especialitzacio_districtes = especialitzacio.analisi_especialitzacio(
    zones=districtes_base,
    edificis=edificis_base,
    idx_zones=dict_indexs["Limits_administratius"]["Districtes"],
    usos_exclosos=["1_residential", "2_agriculture"]
)
# Addició dels camps d'especialització
districtes_especialitzacio = especialitzacio.afegir_resultats_especialitzacio(
    zones=districtes_base,
    resultats=resultats_especialitzacio_districtes
)

## Barris
resultats_especialitzacio_barris = especialitzacio.analisi_especialitzacio(
    zones=barris_base,
    edificis=edificis_base,
    idx_zones=dict_indexs["Limits_administratius"]["Barris"],
    usos_exclosos=["1_residential", "2_agriculture"]
)
# Addició dels camps d'especialització
barris_especialitzacio = especialitzacio.afegir_resultats_especialitzacio(
    zones=barris_base,
    resultats=resultats_especialitzacio_barris
)

# Assignar els camps d'especialització a la malla a partir dels edificis
malla_especialitzacio = especialitzacio.assignar_especialitzacio_per_hexagons(
    edificis=edificis_base,
    malla=malla_base,
    usos_exclosos=['1_residential', "2_agriculture"]
)

# ------------------------------------------------------------------------------
# 5.3. Agrupacions espacials - clústers
# ------------------------------------------------------------------------------

clusters_dict = clusters.analisi_clusters(
    layer=edificis_base,
    usos=config.USOS
)

# ------------------------------------------------------------------------------
# 5.4. Accessibilitat
# ------------------------------------------------------------------------------
### CANVI A SERVEIS PÚBLICS
### NO FAREM COMPARATIVA
# # ------------------------------------------------------------------------------
# # 5.4.1. Accessibilitat àrees comercials
# # ------------------------------------------------------------------------------

# # Clústers comercials - 4_2_retail
# clusters_retail = clusters_dict["4_2_retail"]["clusters"]

# # Càlcul d'isoàrees d'accessibilitat
# isoarees_retail = accessibilitat.analisi_accessibilitat(
#     graf=dict_layers_clean["Graf"]["Graf_trams"],
#     origen=clusters_retail
# )

# # Assignar el valor d'accessibilitat de les isoàrees als edificis
# edificis_accessibilitat_retail = accessibilitat.assignar_isoarees_a_edificis(
#     edificis=edificis_base,
#     isoarees=isoarees_retail
# )

# # Assignar el valor d'accessibilitat dels edificis a la malla hexagonal
# malla_accessibilitat_retail = accessibilitat.assignar_accessibilitat_per_hexagons(
#     edificis=edificis_accessibilitat_retail,
#     malla=malla_base
# )

# ------------------------------------------------------------------------------
# 5.4.2. Accessibilitat serveis públics
# ------------------------------------------------------------------------------

# Serveis públics - 4_3_publicServices
clusters_publicS = clusters_dict["4_3_publicServices"]["clusters"]

# Càlcul d'isoàrees d'accessibilitat
isoarees = accessibilitat.analisi_accessibilitat(
    graf=dict_layers_clean["Graf"]["Graf_trams"],
    origen=clusters_publicS
)

# Assignar el valor d'accessibilitat de les isoàrees als edificis
edificis_accessibilitat = accessibilitat.assignar_isoarees_a_edificis(
    edificis=edificis_base,
    isoarees=isoarees
)

# Assignar el valor d'accessibilitat dels edificis a la malla hexagonal
malla_accessibilitat = accessibilitat.assignar_accessibilitat_per_hexagons(
    edificis=edificis_accessibilitat,
    malla=malla_base
)

# ------------------------------------------------------------------------------
# 5.6. Anàlisi bivariant
# ------------------------------------------------------------------------------
# # ------------------------------------------------------------------------------
# # 5.6.1. Anàlisi bivariant diversitat funcional - dominància
# # ------------------------------------------------------------------------------

# ## Districtes
# districtes_bivariant_DF_D = especialitzacio.afegir_classe_bivariant_DF_D(
#     layer=districtes_especialitzacio
# )

# ## Barris
# barris_bivariant_DF_D = especialitzacio.afegir_classe_bivariant_DF_D(
#     layer=barris_especialitzacio
# )

# ## Malla hexagonal
# malla_bivariant_DF_D = especialitzacio.afegir_classe_bivariant_DF_D(
#     layer=malla_especialitzacio
# )

# # Separar els hexàgons vàlids dels no vàlids - aquells amb el camp
# # de l'anàlisi bivariant NULL
# hexagons_valids_DF_D, hexagons_no_valids_DF_D = hexagons.separar_hexagons_valids(
#     malla=malla_bivariant_DF_D
# )

# ------------------------------------------------------------------------------
# 5.6.2. Anàlisi bivariant diversitat funcional - accessibilitat
# ------------------------------------------------------------------------------

## Districtes
districtes_bivariant_DF_A = especialitzacio.afegir_classe_bivariant_DF_A(
    layer=districtes_especialitzacio
)

## Barris
barris_bivariant_DF_A = especialitzacio.afegir_classe_bivariant_DF_A(
    layer=barris_especialitzacio
)

## Malla hexagonal
malla_bivariant_DF_A = especialitzacio.afegir_classe_bivariant_DF_A(
    layer=malla_especialitzacio
)

# Separar els hexàgons vàlids dels no vàlids - aquells amb el camp
# de l'anàlisi bivariant NULL
hexagons_valids_DF_A, hexagons_no_valids_DF_A = hexagons.separar_hexagons_valids(
    malla=malla_bivariant_DF_A
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
# 6.3. Especialització funcional - Dominància / Diversitat
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
    hexagons=malla_especialitzacio
)

# ------------------------------------------------------------------------------
# 6.4. Accessibilitat
# ------------------------------------------------------------------------------
# # ------------------------------------------------------------------------------
# # 6.4.1. Accessibilitat comercial
# # ------------------------------------------------------------------------------

# layers_simbologia_accessibilitat_retail = simbologia_general.simbologia_edificis_accessibilitat(
#     edificis=edificis_accessibilitat_retail,
#     graf=dict_layers_clean["Graf"]["Graf_trams"],
#     clusters=clusters_dict["4_2_retail"]["clusters"],
#     terme=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
# )

# ------------------------------------------------------------------------------
# 6.4.2. Accessibilitat serveis públics
# ------------------------------------------------------------------------------

layers_simbologia_accessibilitat = simbologia_general.simbologia_edificis_accessibilitat(
    edificis=edificis_accessibilitat,
    graf=dict_layers_clean["Graf"]["Graf_trams"],
    clusters=clusters_dict["4_3_publicServices"]["clusters"],
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
    **layers_simbologia_clusters,
    **layers_simbologia_especialitzacio_districtes,
    **layers_simbologia_especialitzacio_barris,
    **layers_simbologia_especialitzacio_hexagons,
    **layers_simbologia_accessibilitat,
    **layers_simbologia_bivariant_valids,
    "hexagons_no_valids_DF_A": layers_simbologia_bivariant_valids
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

###NOMÉS ELS DE PUBLIC SERVICE??
layout_clusters.composicio_clusters(
    capes=[
        layers_simbologia_clusters["3_industrial"],
        layers_simbologia_zones["3_industrial"],
        layers_simbologia_clusters["4_1_office"],
        layers_simbologia_zones["4_1_office"],
        layers_simbologia_clusters["4_2_retail"],
        layers_simbologia_zones["4_2_retail"],
        layers_simbologia_clusters["4_3_publicServices"],
        layers_simbologia_zones["4_3_publicServices"],
        layers_simbologia_base["Edificis"],
        layers_simbologia_base["Barris"],
        layers_simbologia_base["Districtes"],
        basemap_layer
    ],
    capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
)

# ------------------------------------------------------------------------------
# 7.4. Composicions especialització funcional
# ------------------------------------------------------------------------------

# ## Districtes
# layout_especialitzacio.composicio_especialitzacio(
#     capes=districtes_especialitzacio_no_residencial,
#     capa_extent=districtes_base
# )

# ## Districtes
# layout_bivariant_zones.composicio_bivariant_zones(
#     zona="Districtes",
#     capes=layers_simbologia_especialitzacio_districtes["bivariant"],
#     capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
# )

# ## Barris
# layout_bivariant_zones.composicio_bivariant_zones(
#     zona="Barris",
#     districtes=districtes_base,
#     capes=layers_simbologia_especialitzacio_barris["bivariant"],
#     capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
# )


### LAYOUT COMPARATIU DISTRICTES / BARRIS
### aprofitar el d'especialització

layout_especialitzacio.composicio_especialitzacio(
    capes=malla_especialitzacio,
    capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
)


# ------------------------------------------------------------------------------
# 7.5. Composició d'accessibilitat
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
# 7.4. Composicions especialització funcional - Anàlisi bivariant
# ------------------------------------------------------------------------------

## Malla hexagonal
layout_bivariant_zones.composicio_bivariant_zones(
    zona="Hexagons",
    districtes=districtes_base,
    capes=[
        layers_simbologia_hexagons["bivariant"],
        layer_simbologia_hexagons_no_valids
    ],
    capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"],
    amb_capçalera=False
)

# ------------------------------------------------------------------------------
# 7.6. Composició final
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

