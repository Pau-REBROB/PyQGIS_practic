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
import simbologia.simbologia_agregacions as simbologia_agregacions
import simbologia.simbologia_especialitzacio as simbologia_especialitzacio
import simbologia.simbologia_hexagons as simbologia_hexagons
import simbologia.simbologia_accessibilitat as simbologia_accessibilitat
import simbologia.simbologia_general as simbologia_general
import layouts.layout_common as layout_common
import layouts.layout_general as layout_general
import layouts.layout_atles as layout_atles
import layouts.layout_maup as layout_maup
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
    hexagons, simbologies, simbologia_agregacions, simbologia_especialitzacio,
    simbologia_hexagons, simbologia_accessibilitat, simbologia_general,
    layout_common, layout_general, layout_atles, layout_maup, layout_analisi,
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
# 5.4. Anàlisi industrial - Densitat industrial
# ------------------------------------------------------------------------------

# Càlcul de densitat d'edificis industrials
# Escriptura dels resultats 
## Per Districte
densitat_industrial_districtes = agregacions.calcular_densitat_per_zona(
    edificis=edificis_industrial_net,
    camp_id_edifici="gml_id",
    zones=districtes_base,
    camp_id_zona="NOM"
)
# {'Ciutat Vella': 2.8537925019109616, 'Eixample': 11.119591155446466, 'Sants-Montjuïc': 13.898692487894122,
#  'Les Corts': 6.488354364332429, 'Sarrià-Sant Gervasi': 1.4062836045522231, 'Gràcia': 5.20799077025363,
#  'Horta-Guinardó': 11.91101011481912, 'Nou Barris': 10.922900976136285, 'Sant Andreu': 61.58532198416397,
#  'Sant Martí': 58.44760368555757}

districtes_zones_densitat_industrial = agregacions.escriure_valors_zonals_a_capa(
    zones=districtes_base,
    dict_valors=densitat_industrial_districtes,
    camp_id_zona="NOM",
    nom_camp_resultat="densitat_industrial_km2"
)

## Per Barri
densitat_industrial_barris = agregacions.calcular_densitat_per_zona(
    edificis=edificis_industrial_net,
    camp_id_edifici="gml_id",
    zones=barris_base,
    camp_id_zona="NOM"
)
# {'el Raval': 2.7265634843773037, 'el Barri Gòtic': 2.452200668772121, 'la Barceloneta': 1.6958034661544819,
#  'Sant Pere, Santa Caterina i la Ribera': 4.505849034472708, 'el Fort Pienc': 9.684127636162055,
#  'la Sagrada Família': 24.95610253010519, "la Dreta de l'Eixample": 3.7738088165542747,
#  "l'Antiga Esquerra de l'Eixample": 4.884259988464307, "la Nova Esquerra de l'Eixample": 14.171689098468015,
#  'Sant Antoni': 18.654236670243844, 'el Poble-sec': 6.324529389514533, 'la Marina del Prat Vermell': 15.592651312039054,
#  'la Marina de Port': 2.3647930992850785, 'la Font de la Guatlla': 10.098647380844538,
#  "el Camp d'en Grassot i Gràcia Nova": 4.61164913145761, 'el Baix Guinardó': 17.778862115958393, 'el Guinardó': 8.40507309065514,
#  'Can Baró': 18.22045119044464, 'el Carmel': 37.23441948550119, 'la Teixonera': 32.58827530724994,
#  'Sant Genís dels Agudells': 2.3744865827312482, 'Montbau': 0.9737151239483247, "la Vall d'Hebron": 4.029382641168529,
#  'la Clota': 56.025225238931164, "la Font d'en Fargues": 15.215544799622181, 'Horta': 12.703513507404692,
#  'Vilapicina i la Torre Llobeta': 8.860848338453309, 'Porta': 13.144931606972728, 'el Turó de la Peira': 5.646325054113575,
#  'Hostafrancs': 29.2734722755591, 'la Bordeta': 27.961625212707638, 'Sants - Badal': 21.708217944174613, 'Sants': 21.92494916055728,
#  'les Corts': 11.34422263315873, 'la Maternitat i Sant Ramon': 9.397657425819444, 'Pedralbes': 1.8622052926612433,
#  'Vallvidrera, el Tibidabo i les Planes': 0.8830403547994439, 'Sarrià': 2.953294189844949, 'les Tres Torres': 1.2691009607006392,
#  'Sant Gervasi - la Bonanova': 2.238497094517822, 'el Putxet i el Farró': 3.5383220538145563, 
# 'Sant Gervasi - Galvany': 0.599082305312369, 'Vallcarca i els Penitents': 1.5987855670146418, 'el Coll': 2.8310591844621396,
#  'la Salut': 3.0845678970070307, 'la Vila de Gràcia': 10.596522818136885, 'Navas': 0.0,
#  "el Camp de l'Arpa del Clot": 39.155687494662416, 'el Clot': 31.57326443505451,
#  'el Parc i la Llacuna del Poblenou': 98.92683222755115, 'la Vila Olímpica del Poblenou': 25.95043566546357,
#  'el Poblenou': 82.9594560753457, 'Diagonal Mar i el Front Marítim del Poblenou': 6.5202194375444655,
#  'el Besòs i el Maresme': 17.374017015289535, 'Provençals del Poblenou': 160.2594171031141, 'Sant Martí de Provençals': 0.0,
#  'la Verneda i la Pau': 80.53251319047949, 'Can Peguera': 0.0, 'la Guineueta': 6.536400701508535, 'Verdun': 29.521139741469945,
#  'la Prosperitat': 11.839946051622706, 'Canyelles': 6.328301757792411, 'les Roquetes': 18.662007870325617,
#  'la Trinitat Nova': 3.467964647675853, 'Torre Baró': 7.463437365028402, 'Ciutat Meridiana': 2.6547504133865965,
#  'Vallbona': 30.95285128736839, 'la Trinitat Vella': 3.714655570609501, 'Baró de Viver': 4.349854459425396,
#  'el Bon Pastor': 195.3746320057572, 'Sant Andreu': 10.17446973022927, 'la Sagrera': 8.111029348092325,
#  'el Congrés i els Indians': 24.43708933167582}

barris_zones_densitat_industrial = agregacions.escriure_valors_zonals_a_capa(
    zones=barris_base,
    dict_valors=densitat_industrial_barris,
    camp_id_zona="NOM",
    nom_camp_resultat="densitat_industrial_km2"
)

## Per Hexàgon
densitat_industrial_hexagons = agregacions.calcular_densitat_per_zona(
    edificis=edificis_industrial_net,
    camp_id_edifici="gml_id",
    zones=malla_base,
    camp_id_zona="id"
)

hexagons_zones_densitat_industrial = agregacions.escriure_valors_zonals_a_capa(
    zones=malla_base,
    dict_valors=densitat_industrial_hexagons,
    camp_id_zona="id",
    nom_camp_resultat="densitat_industrial_km2"
)

# Determinació dels rangs de valors
# El valor 0 es tracta com una classe pròpia - "sense indústria"
breaks_densitat_industrial = simbologia_agregacions.calcular_breaks_compartits(
    diccionari_valors=densitat_industrial_hexagons,
    n_classes=6
)
print(breaks_densitat_industrial)
# [0.0, 0.0, 102.64004785641126, 256.60011964102813, 461.88021535314425, 821.1203828475225, 1539.600717834395]

# Classificació dels valors de densitat en intervals
# Ús de les dades d'hexàgons - l'agregació més petita
# Comprovació de la distribució de les dades al contenir gran quantitat de valors 0
recompte_classes_districtes = agregacions.comptar_zones_per_classe(
    dict_valors=densitat_industrial_districtes,
    breaks=breaks_densitat_industrial
)

recompte_classes_barris = agregacions.comptar_zones_per_classe(
    dict_valors=densitat_industrial_barris,
    breaks=breaks_densitat_industrial
)

recompte_classes_hexagons = agregacions.comptar_zones_per_classe(
    dict_valors=densitat_industrial_hexagons,
    breaks=breaks_densitat_industrial
)

# ------------------------------------------------------------------------------
# 5.5. Agrupacions espacials - clústers industrials
# ------------------------------------------------------------------------------

distancies_industrial = clusters.distancia_veins_propers(
    layer=edificis_industrial_net
)

# Resultats distàncies
import statistics
print("Mitjana:", statistics.mean(distancies_industrial)) # 67,4
print("Mediana:", statistics.median(distancies_industrial)) # 34,6

distancies_k = clusters.distancia_k_vei(
    edificis_industrial_net,
    k=10
)
print(len(distancies_k))
print(distancies_k[::25])  # una mostra cada 25 valors, per no saturar la resposta

grafics.grafic_k_distance(
    distancies_k=distancies_k,
    k=10,
    output_path=config.EXPORTACIO_GRAFICS["Grafic_k_veins"],
    eps_candidat=150
)

# No existeix una zona de transició clara
# Es proven diferents valors d'eps
resultats_eps = {}
for eps_prova in [100, 150, 200]:
    config.CONFIG_ANALISI["Clusters"]["eps"] = eps_prova
    resultat = clusters.analisi_clusters(
        layer=edificis_industrial_net,
        usos=["3_industrial"]
    )
    resultats_eps[eps_prova] = resultat["3_industrial"]["resum"]

for eps_prova, resum in resultats_eps.items():
    print(f"eps={eps_prova}:", resum)

# A la vista dels resultats, eps = 200 min_size = 10

resultat_clusters_industrials = clusters.analisi_clusters(
    layer=edificis_industrial_net,
    usos=["3_industrial"]
)

# Filtratge dels clústers
## Diccionari de mides segons ID del clúster
mides_per_cluster = {
    feat["CLUSTER_ID"]: feat["CLUSTER_SIZE"]
    for feat in resultat_clusters_industrials["3_industrial"]["clusters"].getFeatures()
    if feat["CLUSTER_ID"] != -1 and feat["CLUSTER_SIZE"] is not None
}

## Valor de tall per obtenir els ID vàlids
mida_minima = 50

ids_seleccionats = [
    cluster_id
    for cluster_id, mida in mides_per_cluster.items()
    if mida >= mida_minima
]

## Filtre per pertinença a la llista de IDs - no segons SIZE
expressio = f'"CLUSTER_ID" IN ({", ".join(map(str, ids_seleccionats))})'

clusters_seleccionats = clusters.filtrar_capa(
    resultat_clusters_industrials["3_industrial"]["clusters"],
    expressio
)

# ------------------------------------------------------------------------------
# 5.6. Accessibilitat
# ------------------------------------------------------------------------------

# Càlcul d'isoàrees d'accessibilitat multi-origen
isoarees_industrial = accessibilitat.analisi_accessibilitat(
    graf=dict_layers_clean["Graf"]["Graf_trams"],
    origen=clusters_seleccionats
)

# Càlcul d'isoàrees d'accessibilitat individualment
isoarees_per_cluster = accessibilitat.analisi_accessibilitat_individual(
    graf=dict_layers_clean["Graf"]["Graf_trams"],
    origen=clusters_seleccionats,
    **config.CONFIG_ANALISI["Isoarees_individuals"]
)




# Assignar el valor d'accessibilitat de les isoàrees als edificis
edificis_accessibilitat = accessibilitat.assignar_isoarees_a_edificis(
    edificis=edificis_base,
    isoarees=isoarees
)

# Assignar el valor d'accessibilitat dels edificis a la malla hexagonal
malla_accessibilitat = accessibilitat.assignar_accessibilitat_per_hexagons(
    edificis=edificis_accessibilitat,
    malla=malla_especialitzacio
)


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
# 6.3. Agregacions - Densitat industrial
# ------------------------------------------------------------------------------

layers_simbologia_densitat_industrial = simbologia_general.simbologia_densitat_agregacions(
    capa_districtes=districtes_zones_densitat_industrial,
    capa_barris=barris_zones_densitat_industrial,
    capa_hexagons=hexagons_zones_densitat_industrial
)


#------------------------
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
    **layers_simbologia_densitat_industrial
    #**layers_simbologia_clusters,
    #**layers_simbologia_zones,
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

# ------------------------------------------------------------------------------
# 7.3. Composició densitat industrial MAUP
# ------------------------------------------------------------------------------

layout_maup.composicio_maup_densitat_industrial(
    capes=layers_simbologia_densitat_industrial,
    capa_terme=layers_simbologia_base["TermeMunicipal"],
    capa_extent=layers_simbologia_base["TermeMunicipal"],
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