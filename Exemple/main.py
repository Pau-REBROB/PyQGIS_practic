"""
Anàlisi geoespacial de l'activitat industrial de Barcelona amb PyQGIS
========================================================================================

Script principal que orquestra el flux complet d'anàlisi:

########

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

import config #Arxiu de configuració

import processing


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

# # Retorna un diccionari d'índex espacials de cada capa
# dict_indexs = preparacio_dades.crear_indexs(
#     dict_layers=dict_layers_clean
# )


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
# 5.3. Exploració temporal de les dades
# ------------------------------------------------------------------------------

# Edificis industrials
distribucio_industrial = temporal.extreure_any_edificis(edificis_industrial)

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
distribucio_no_industrial = temporal.extreure_any_edificis(edificis_no_industrial)

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

# Anàlisi de la distribució per períodes
percentatge_industrial = temporal.percentatges_distribucio(
    distribucio=distribucio_industrial
)

percentatge_no_industrial = temporal.percentatges_distribucio(
    distribucio=distribucio_no_industrial
)

print("INDUSTRIAL")
print(percentatge_industrial)

print("NO INDUSTRIAL")
print(percentatge_no_industrial)

# Addició del camp "any_construcció"
edificis_industrial_net = temporal.afegir_any_construccio(edificis_industrial)
edificis_no_industrial_net = temporal.afegir_any_construccio(edificis_no_industrial)

# ------------------------------------------------------------------------------
# 5.4. Agregacions
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# 5.4.1. Nombre d'edificis
# ------------------------------------------------------------------------------

# Càlcul del nombre d'edificis industrials a cada zona
# Escriptura dels resultats 

## Districtes
edificis_per_districte = agregacions.calcular_edificis_per_zona(
    edificis=edificis_industrial_net,
    camp_id_edifici="gml_id",
    zones=districtes_base,
    camp_id_zona="NOM"
)

districtes_edificis_industrials = agregacions.escriure_valors_zonals_a_capa(
    zones=districtes_base,
    dict_valors=edificis_per_districte,
    camp_id_zona="NOM",
    nom_camp_resultat="nombre_edificis_industrials"
)

## Barris
edificis_per_barri = agregacions.calcular_edificis_per_zona(
    edificis=edificis_industrial_net,
    camp_id_edifici="gml_id",
    zones=barris_base,
    camp_id_zona="NOM"
)

barris_edificis_industrials = agregacions.escriure_valors_zonals_a_capa(
    zones=barris_base,
    dict_valors=edificis_per_barri,
    camp_id_zona="NOM",
    nom_camp_resultat="nombre_edificis_industrials"
)

## Hexàgons
edificis_per_hexagon = agregacions.calcular_edificis_per_zona(
    edificis=edificis_industrial_net,
    camp_id_edifici="gml_id",
    zones=malla_base,
    camp_id_zona="id"
)

hexagons_edificis_industrials = agregacions.escriure_valors_zonals_a_capa(
    zones=malla_base,
    dict_valors=edificis_per_hexagon,
    camp_id_zona="id",
    nom_camp_resultat="nombre_edificis_industrials"
)

# ------------------------------------------------------------------------------
# 5.4.2. Superfície construïda
# ------------------------------------------------------------------------------

# Càlcul de superfície industrial construïda per zona
# Escriptura dels resultats sobre la capa de nombre d'edificis

## Districtes
superficie_industrial_per_districte = agregacions.calcular_superficie_per_zona(
    edificis=edificis_industrial_net,
    zones=districtes_base,
    camp_id_zona="NOM"
)

districtes_superficie_industrial = agregacions.escriure_valors_zonals_a_capa(
    zones=districtes_edificis_industrials,
    dict_valors=superficie_industrial_per_districte,
    camp_id_zona="NOM",
    nom_camp_resultat="superficie_construida_km2"
)

## Barris
superficie_industrial_per_barri = agregacions.calcular_superficie_per_zona(
    edificis=edificis_industrial_net,
    zones=barris_base,
    camp_id_zona="NOM"
)

barris_superficie_industrial = agregacions.escriure_valors_zonals_a_capa(
    zones=barris_edificis_industrials,
    dict_valors=superficie_industrial_per_barri,
    camp_id_zona="NOM",
    nom_camp_resultat="superficie_construida_km2"
)

## Hexàgons
superficie_industrial_per_hexagon = agregacions.calcular_superficie_per_zona(
    edificis=edificis_industrial_net,
    zones=malla_base,
    camp_id_zona="id"
)

hexagons_superficie_industrial = agregacions.escriure_valors_zonals_a_capa(
    zones=hexagons_edificis_industrials,
    dict_valors=superficie_industrial_per_hexagon,
    camp_id_zona="id",
    nom_camp_resultat="superficie_construida_km2"
)

# ------------------------------------------------------------------------------
# 5.4.3. Densitat de superfície construïda per zona
# ------------------------------------------------------------------------------

# Càlcul de superfície industrial construïda per zona
# Escriptura dels resultats sobre la capa de superfície construïda

## Districtes
densitat_superficie_industrial_districtes = agregacions.calcular_densitat_superficie_per_zona(
    edificis=edificis_industrial_net,
    zones=districtes_base,
    camp_id_zona="NOM"
)

districtes_densitat_superficie_industrial = agregacions.escriure_valors_zonals_a_capa(
    zones=districtes_superficie_industrial,
    dict_valors=densitat_superficie_industrial_districtes,
    camp_id_zona="NOM",
    nom_camp_resultat="densitat_superficie_industrial_km2"
)

## Barris
densitat_superficie_industrial_barris = agregacions.calcular_densitat_superficie_per_zona(
    edificis=edificis_industrial_net,
    zones=barris_base,
    camp_id_zona="NOM"
)

barris_densitat_superficie_industrial = agregacions.escriure_valors_zonals_a_capa(
    zones=barris_superficie_industrial,
    dict_valors=densitat_superficie_industrial_barris,
    camp_id_zona="NOM",
    nom_camp_resultat="densitat_superficie_industrial_km2"
)

## Hexàgons
densitat_superficie_industrial_hexagons = agregacions.calcular_densitat_superficie_per_zona(
    edificis=edificis_industrial_net,
    zones=malla_base,
    camp_id_zona="id"
)

hexagons_densitat_superficie_industrial = agregacions.escriure_valors_zonals_a_capa(
    zones=hexagons_superficie_industrial,
    dict_valors=densitat_superficie_industrial_hexagons,
    camp_id_zona="id",
    nom_camp_resultat="densitat_superficie_industrial_km2"
)

# ------------------------------------------------------------------------------
# 5.4.4. Densitat de d'edificis per zona
# ------------------------------------------------------------------------------

# Càlcul de densitat d'edificis industrials
# Escriptura dels resultats
 
## Districte
densitat_edificis_industrials_districtes = agregacions.calcular_densitat_edificis_per_zona(
    edificis=edificis_industrial_net,
    camp_id_edifici="gml_id",
    zones=districtes_base,
    camp_id_zona="NOM"
)

districtes_densitat_edificis_industrials = agregacions.escriure_valors_zonals_a_capa(
    zones=districtes_densitat_superficie_industrial,
    dict_valors=densitat_edificis_industrials_districtes,
    camp_id_zona="NOM",
    nom_camp_resultat="densitat_industrial_km2"
)

## Barri
densitat_edificis_industrials_barris = agregacions.calcular_densitat_edificis_per_zona(
    edificis=edificis_industrial_net,
    camp_id_edifici="gml_id",
    zones=barris_base,
    camp_id_zona="NOM"
)

barris_densitat_edificis_industrials = agregacions.escriure_valors_zonals_a_capa(
    zones=barris_densitat_superficie_industrial,
    dict_valors=densitat_edificis_industrials_barris,
    camp_id_zona="NOM",
    nom_camp_resultat="densitat_industrial_km2"
)

## Hexàgons
densitat_edificis_industrials_hexagons = agregacions.calcular_densitat_edificis_per_zona(
    edificis=edificis_industrial_net,
    camp_id_edifici="gml_id",
    zones=malla_base,
    camp_id_zona="id"
)

hexagons_densitat_edificis_industrials = agregacions.escriure_valors_zonals_a_capa(
    zones=hexagons_densitat_superficie_industrial,
    dict_valors=densitat_edificis_industrials_hexagons,
    camp_id_zona="id",
    nom_camp_resultat="densitat_industrial_km2"
)

# ------------------------------------------------------------------------------
# 5.4.5. Intervals de representació per zona
# ------------------------------------------------------------------------------

# Determinació dels rangs de valors a partir de l'agregació hexagonal
# El valor 0 es tracta com una classe pròpia - "sense indústria"

## Nombre d'edificis
breaks_nombre_edificis_industrial = simbologia_agregacions.calcular_breaks_compartits(
    diccionari_valors=edificis_per_hexagon,
    n_classes=6
)
print(breaks_nombre_edificis_industrial)
# [0.0, 0.0, 2.0, 5.0, 9.0, 16.0, 30.0]

## Densitat d'edificis
breaks_densitat_edificis_industrial = simbologia_agregacions.calcular_breaks_compartits(
    diccionari_valors=densitat_edificis_industrials_hexagons,
    n_classes=6
)
print(breaks_densitat_edificis_industrial)
# [0.0, 0.0, 102.64004785641126, 256.60011964102813, 461.88021535314425, 821.1203828475225, 1539.600717834395]

## Superfície construïda
breaks_superficie_industrial = simbologia_agregacions.calcular_breaks_compartits(
    diccionari_valors=superficie_industrial_per_hexagon,
    n_classes=6
)
print(breaks_superficie_industrial)
# [0.0, 0.0, 0.009690514350033364, 0.029347486908760854, 0.06606970128950569, 0.11278709819313325, 0.19762085729022696]

## Densitat superfície construïda
breaks_densitat_superficie_industrial = simbologia_agregacions.calcular_breaks_compartits(
    diccionari_valors=densitat_superficie_industrial_hexagons,
    n_classes=6
)
print(breaks_densitat_superficie_industrial)
# [0.0, 0.0, 0.49731742831919135, 1.5061137303810943, 3.3906986510964585, 5.788236578024638, 10.141907124808178]





# # Classificació dels valors de densitat en intervals
# # Ús de les dades d'hexàgons - l'agregació més petita
# # Comprovació de la distribució de les dades al contenir gran quantitat de valors 0
# recompte_classes_districtes = agregacions.comptar_zones_per_classe(
#     dict_valors=densitat_edificis_industrials_hexagons,
#     breaks=breaks_densitat_edificis_industrial
# )

# recompte_classes_barris = agregacions.comptar_zones_per_classe(
#     dict_valors=densitat_industrial_barris,
#     breaks=breaks_densitat_industrial
# )

# recompte_classes_hexagons = agregacions.comptar_zones_per_classe(
#     dict_valors=densitat_industrial_hexagons,
#     breaks=breaks_densitat_industrial
# )

# ------------------------------------------------------------------------------
# 5.4. Anàlisi temporal
# ------------------------------------------------------------------------------

# El període 1960–1980 concentra el 43% dels industrials 
# i, juntament amb els períodes anteriors, ens permet separar un parc industrial més antic del més recent.

# Filtre edificis anteriors a 1980
edificis_industrials_anteriors_1980 = clusters.filtrar_capa(
    edificis_industrial_net,
    expressio='"any_construccio" <= 1980'
)

malla_industrial_antic = hexagons.comptar_edificis_per_hexagon(
    edificis=edificis_industrials_anteriors_1980,
    malla=malla_base
)
malla_industrial = hexagons.comptar_edificis_per_hexagon(
    edificis=edificis_industrial_net,
    malla=malla_base
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

zones_clusters_seleccionats = clusters.envolvent_clusters(
    layer=clusters_seleccionats
)

# ------------------------------------------------------------------------------
# 5.6. Accessibilitat
# ------------------------------------------------------------------------------

# Càlcul d'isoàrees d'accessibilitat multi-origen
isoarees_industrial = accessibilitat.analisi_accessibilitat(
    graf=dict_layers_clean["Graf"]["Graf_osm"],
    origen=clusters_seleccionats,
    **config.CONFIG_ANALISI["Isoarees_globals"]
)

# Càlcul d'isoàrees d'accessibilitat individualment
isoarees_per_cluster = accessibilitat.analisi_accessibilitat_individual(
    graf=dict_layers_clean["Graf"]["Graf_osm"],
    origen=clusters_seleccionats,
    **config.CONFIG_ANALISI["Isoarees_individuals"]
)

# Comparació de la cobertura de les isoàrees
llindars_comparacio = [500, 1000, 1500, 2000, 2500, 3000]

for cluster_id, isoarea in isoarees_per_cluster.items():
    resultat = accessibilitat.area_coberta_per_llindar(
        isoarees=isoarea,
        llindars=llindars_comparacio
    )
    print(f"Cluster {cluster_id}:", resultat)

# Resultats
#Cluster 24: {
#   500: 326306.46482907515, 1000: 1982951.445349127, 1500: 4909606.273723032,
#   2000: 8576268.59377075, 2500: 13031288.592719823, 3000: 18227628.431523204
# }
#Cluster 2: {
#   500: 359224.40429566335, 1000: 1489299.1504833587, 1500: 2872486.7499795556,
#   2000: 4775327.897160877, 2500: 6652060.368146252, 3000: 8405186.772574663
# }
#Cluster 27: {
#   500: 407035.93737074174, 1000: 1955767.351290375, 1500: 4139887.3407575935,
#   2000: 7201950.9986871155, 2500: 10785305.45604671, 3000: 15074048.936193772
# }
#Cluster 28: {
#   500: 389912.93736368464, 1000: 2085224.3000795022, 1500: 5092805.512293063,
#   2000: 9104471.990774022, 2500: 13428742.272372171, 3000: 17920921.40379775
# }

resultats_area_per_cluster = {
    cluster_id: accessibilitat.area_coberta_per_llindar(
        isoarees=isoarea,
        llindars=llindars_comparacio
    )
    for cluster_id, isoarea in isoarees_per_cluster.items()
}

grafics.grafic_area_accessibilitat(
    resultats_per_cluster=resultats_area_per_cluster,
    output_path=config.EXPORTACIO_GRAFICS["Grafic_area_isoarees"],
    noms_clusters={24: "Poblenou", 2: "Zona Franca", 27: "Bon Pastor", 28: "Sant Martí"}
)

# Assignar el valor d'accessibilitat de les isoàrees als edificis
edificis_amb_accessibilitat = accessibilitat.assignar_isoarees_a_edificis(
    edificis=edificis_base,
    isoarees=isoarees_industrial
)

# Assignació de ID clúster a cada edifici
edificis_industrial_amb_cluster = clusters.assignar_cluster_id_a_edificis(
    edificis=edificis_industrial_net,
    clusters=resultat_clusters_industrials["3_industrial"]["clusters"],
    camp_id_edifici="gml_id"
)

# Càlcul accessibilitat als edificis
edificis_industrial_final = accessibilitat.assignar_isoarees_a_edificis(
    edificis=edificis_industrial_amb_cluster,
    isoarees=isoarees_industrial
)

# Gràfic de dispersió accessibilitat-any de construcció
clusters_ids_origen = {24, 2, 27, 28}

grafics.grafic_scatter_any_accessibilitat(
    layer=edificis_industrial_final,
    cluster_ids_origen=clusters_ids_origen,
    output_path=config.EXPORTACIO_GRAFICS["Grafic_scatter_anyconstruccio_accessibilitat"]
)

# Estadística de la correlació
from scipy import stats

anys = []
accessibilitats = []

for feat in edificis_industrial_final.getFeatures():
    if feat["CLUSTER_ID"] in clusters_ids_origen:
        continue
    if feat["any_construccio"] is None or feat["accessibilitat"] is None:
        continue
    anys.append(feat["any_construccio"])
    accessibilitats.append(feat["accessibilitat"])

correlacio, p_valor = stats.pearsonr(anys, accessibilitats)
print(f"N = {len(anys)}")
print(f"Correlació de Pearson: {correlacio:.3f} (p={p_valor:.4f})")




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
# 6.3.1. Agregacions - Nombre d'edificis / Superfície construïda
# ------------------------------------------------------------------------------

layers_simbologia_densitat_industrial = simbologia_general.simbologia_densitat_agregacions(
    capa_districtes=districtes_zones_densitat_industrial,
    capa_barris=barris_zones_densitat_industrial,
    capa_hexagons=hexagons_zones_densitat_industrial
)

# ------------------------------------------------------------------------------
# 6.3.2. Agregacions - Densitat superfície industrial MAUP
# ------------------------------------------------------------------------------

layers_simbologia_densitat_industrial = simbologia_general.simbologia_densitat_agregacions(
    capa_districtes=districtes_zones_densitat_industrial,
    capa_barris=barris_zones_densitat_industrial,
    capa_hexagons=hexagons_zones_densitat_industrial
)

# ------------------------------------------------------------------------------
# 6.4. Clústers i accessibilitat
# ------------------------------------------------------------------------------

layers_simbologia_accessibilitat_clusters = simbologia_general.simbologia_accessibilitat_clusters(
    capa_clusters=zones_clusters_seleccionats,
    capa_edificis=edificis_amb_accessibilitat,
    capa_terme=terme_base,
    capa_graf=dict_layers_clean["Graf"]["Graf_osm"]
)



#------------------------

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
    **layers_simbologia_densitat_industrial,
    **layers_simbologia_accessibilitat_clusters
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

# ------------------------------------------------------------------------------
# 7.4. Composició d'accessibilitat
# ------------------------------------------------------------------------------

layout_accessibilitat.composicio_accessibilitat(
    capes=[
        layers_simbologia_accessibilitat_clusters["graf"],
        layers_simbologia_accessibilitat_clusters["edificis"],
        layers_simbologia_accessibilitat_clusters["clusters"],
        layers_simbologia_accessibilitat_clusters["terme"]
    ],
    capa_extent=terme_base
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