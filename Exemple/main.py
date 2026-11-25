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

"""
ESTRUCTURA GENERAL:
main.py
│
├── 1. Imports i configuració
│
├── 2. Inicialització del projecte QGIS
│
├── 3. Importació de capes
│
├── 4. Preparació de dades
│
├── 5. Anàlisi
│   ├── Capes base i malla hexagonal
│   ├── Filtratge d'usos
│   ├── Anàlisi temporal
│   ├── Agregacions territorials
│   └── Clústers industrials
│
├── 6. Simbologia
│   ├── Base
│   ├── Edificis industrials
│   ├── Agregacions
│   └── Anàlisi temporal
│
├── 7. Composicions
│   ├── General
│   ├── Atles
│   ├── Comparació d'agregacions
│   ├── MAUP
│   └── Temporal
│
└── 8. Exportació i desament

----

Configuració i inicialització

Imports, configuració de rutes, QGIS i projecte.



Importació i preparació de dades

Càrrega, preparació de capes i obtenció de les capes base.



Preparació de les unitats d'anàlisi

Malla hexagonal i classificació dels edificis per ús.



Anàlisi temporal

Any de construcció, distribucions i antiguitat relativa.



Agregacions territorials

Nombre d'edificis, superfície i densitats a les tres escales.



Anàlisi de clústers

Distàncies, DBSCAN, selecció i identificació de concentracions.



Simbologia

Cartografia base, atles, agregacions, MAUP i temporal.



Composicions i exportació

Mapes generals, atles, comparació d'agregacions, MAUP i temporal.
"""

"""
PyQGIS_practic/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── Scripts/
│   └── ...
│
├── Exemple/
│   ├── main.py
│   ├── config.py
│   ├── importacio.py
│   ├── inicialitzacio.py
│   ├── preparacio_dades.py
│   │
│   ├── analisi/
│   │   ├── agregacions.py
│   │   ├── clusters.py
│   │   ├── hexagons.py
│   │   ├── temporal.py
│   │   └── grafics.py
│   │
│   ├── simbologia/
│   │   ├── simbologies.py
│   │   ├── simbologia_general.py
│   │   ├── simbologia_agregacions.py
│   │   └── simbologia_temporal.py
│   │
│   ├── layouts/
│   │   ├── layout_common.py
│   │   ├── layout_general.py
│   │   ├── layout_atles.py
│   │   ├── layout_comparacio_agregacions.py
│   │   ├── layout_maup.py
│   │   ├── layout_temporal.py
│   │   └── fusionar_layouts.py
│   │
│   ├── resources/
│   │   └── ...
│   │
│   └── experimental/
│       └── ...
│
└── docs/
    ├── metodologia.md
    ├── dades.md
    └── decisions_analitiques.md
"""

# ==============================================================================
# 1. CONFIGURACIÓ DE L'ENTORN
# ==============================================================================

# ------------------------------------------------------------------------------
# 1.1. Importació de mòduls
# ------------------------------------------------------------------------------

import importlib
import statistics
import sys
from pathlib import Path

# Carpeta del projecte (Exemple/)
_base = Path(__file__).resolve().parent

# Afegim l'arrel del projecte a les rutes d'importació
if str(_base) not in sys.path:
    sys.path.insert(0, str(_base))

# Configuració general
import config

# Mòduls del projecte
## Inicialització i dades
import inicialitzacio
import importacio
import preparacio_dades

## Anàlisi
import analisi.temporal as temporal
import analisi.agregacions as agregacions
import analisi.grafics as grafics
import analisi.clusters as clusters
import analisi.especialitzacio as especialitzacio
import analisi.hexagons as hexagons

## Simbologia
import simbologia.simbologia_agregacions as simbologia_agregacions
import simbologia.simbologia_general as simbologia_general

## Composicions
import layouts.layout_common as layout_common
import layouts.layout_general as layout_general
import layouts.layout_atles as layout_atles
import layouts.layout_comparacio_agregacions as layout_comparacio_agregacions
import layouts.layout_maup as layout_maup
import layouts.layout_temporal as layout_temporal
import layouts.fusionar_layouts as fusionar_layouts


# ------------------------------------------------------------------------------
# 1.2. Recàrrega de mòduls
# ------------------------------------------------------------------------------

_moduls = [
    config, inicialitzacio, importacio, preparacio_dades, temporal,
    agregacions, grafics, clusters, 
    especialitzacio,
    hexagons, 
    simbologia_agregacions,
    simbologia_general, layout_common, layout_general, layout_atles,
    layout_comparacio_agregacions, layout_maup, layout_temporal, 
    fusionar_layouts
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

# Edificis no industrials
distribucio_no_industrial = temporal.extreure_any_edificis(edificis_no_industrial)


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

## Densitat d'edificis
breaks_densitat_edificis_industrial = simbologia_agregacions.calcular_breaks_compartits(
    diccionari_valors=densitat_edificis_industrials_hexagons,
    n_classes=6
)

## Superfície construïda
breaks_superficie_industrial = simbologia_agregacions.calcular_breaks_compartits(
    diccionari_valors=superficie_industrial_per_hexagon,
    n_classes=6
)

## Densitat superfície construïda
breaks_densitat_superficie_industrial = simbologia_agregacions.calcular_breaks_compartits(
    diccionari_valors=densitat_superficie_industrial_hexagons,
    n_classes=6
)

# Classificació dels valors de densitat en intervals
# Ús de les dades d'hexàgons - l'agregació més petita
# Comprovació de la distribució de les dades al contenir gran quantitat de valors 0
## Densitat de superfície industrial
recompte_classes_districtes = agregacions.comptar_zones_per_classe(
    dict_valors=densitat_superficie_industrial_districtes,
    breaks=breaks_densitat_superficie_industrial
)

recompte_classes_barris = agregacions.comptar_zones_per_classe(
    dict_valors=densitat_superficie_industrial_barris,
    breaks=breaks_densitat_superficie_industrial
)

recompte_classes_hexagons = agregacions.comptar_zones_per_classe(
    dict_valors=densitat_superficie_industrial_hexagons,
    breaks=breaks_densitat_superficie_industrial
)

## Nombre d'edificis industrials
recompte_classes_districtes_2 = agregacions.comptar_zones_per_classe(
    dict_valors=edificis_per_districte,
    breaks=breaks_nombre_edificis_industrial
)

recompte_classes_barris_2 = agregacions.comptar_zones_per_classe(
    dict_valors=edificis_per_barri,
    breaks=breaks_nombre_edificis_industrial
)

recompte_classes_hexagons_2 = agregacions.comptar_zones_per_classe(
    dict_valors=edificis_per_hexagon,
    breaks=breaks_nombre_edificis_industrial
)

## Densitat d'edificis industrials
recompte_classes_districtes_3 = agregacions.comptar_zones_per_classe(
    dict_valors=densitat_edificis_industrials_districtes,
    breaks=breaks_densitat_edificis_industrial
)

recompte_classes_barris_3 = agregacions.comptar_zones_per_classe(
    dict_valors=densitat_edificis_industrials_barris,
    breaks=breaks_densitat_edificis_industrial
)

recompte_classes_hexagons_3 = agregacions.comptar_zones_per_classe(
    dict_valors=densitat_edificis_industrials_hexagons,
    breaks=breaks_densitat_edificis_industrial
)

## Superfície industrial
recompte_classes_districtes_4 = agregacions.comptar_zones_per_classe(
    dict_valors=superficie_industrial_per_districte,
    breaks=breaks_superficie_industrial
)

recompte_classes_barris_4 = agregacions.comptar_zones_per_classe(
    dict_valors=superficie_industrial_per_barri,
    breaks=breaks_superficie_industrial
)

recompte_classes_hexagons_4 = agregacions.comptar_zones_per_classe(
    dict_valors=superficie_industrial_per_hexagon,
    breaks=breaks_superficie_industrial
)

# ------------------------------------------------------------------------------
# 5.5.2. Anàlisi temporal - Antiguitat relativa de la indústria
# ------------------------------------------------------------------------------

anys_industrial_barris = agregacions.agrupar_valors_per_zona(
    edificis=edificis_industrial_net,
    camp_valor="any_construccio",
    zones=barris_base,
    camp_id_zona="NOM"
)

anys_resta_usos_barris = agregacions.agrupar_valors_per_zona(
    edificis=edificis_no_industrial_net,
    camp_valor="any_construccio",
    zones=barris_base,
    camp_id_zona="NOM"
)

diferencia_anys_industrial_barris = agregacions.calcular_diferencia_mediana_per_zona(
    valors_industrial=anys_industrial_barris,
    valors_resta=anys_resta_usos_barris
)

# TODO: valorar la integració de les dues agregacions dins
# de calcular_diferencia_mediana_per_zona().

# Escriptura dels resultats
barris_diferencia_mediana = agregacions.escriure_valors_zonals_a_capa(
    zones=barris_base,
    dict_valors=diferencia_anys_industrial_barris,
    camp_id_zona="NOM",
    nom_camp_resultat="diferencia_mediana_any_industria"
)

# Càlcul de la diferència mediana de cada edifici industrial respecte el barri 
mediana_resta_per_zona = {
    id_zona: statistics.median(valors)
    for id_zona, valors in anys_resta_usos_barris.items()
    if valors
}

edificis_diferencia_mediana = temporal.assignar_diferencia_any_a_edificis(
    edificis_industrial=edificis_industrial_net,
    camp_any="any_construccio",
    zones=barris_base,
    camp_id_zona="NOM",
    mediana_resta_per_zona=mediana_resta_per_zona
)

# Identificació de les zones de major concentració industrial (clústers)
# per a la seva representació enlloc de tots els edificis industrials

# ------------------------------------------------------------------------------
# 5.6. Agrupacions espacials - clústers industrials
# ------------------------------------------------------------------------------

distancies_industrial = clusters.distancia_veins_propers(
    layer=edificis_industrial_net
)

# Resultats distàncies
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


# Extent ajustat manualment per cobrir tota l'àrea de Sant Martí, fragmentada en 3 clústers DBSCAN
coordenades_clusters = {
    "Sant Martí": (430453.5797, 4581873.7943, 434732.6889, 4585961.1227),
    "Zona Franca": (424808.0322, 4574897.7675, 427127.3813, 4577043.3153),
    "Sant Andreu": (431328.5796, 4585673.4515, 434624.8122, 4588861.8073)
}

# Extensió de cada clúster i uniformització en una única extensió
extents_clusters = layout_common.extents_manuals_a_dict(
    coordenades=coordenades_clusters
)

extents_clusters_uniformes = layout_common.uniformitzar_extents(
    extents_dict=extents_clusters
)



###########################################

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

layers_simbologia_comparacio_industrial = simbologia_general.simbologia_comparacio_agregacions(
    capa_edificis=hexagons_edificis_industrials,
    capa_superficie=hexagons_superficie_industrial
)

# ------------------------------------------------------------------------------
# 6.3.2. Agregacions - Densitat superfície industrial MAUP
# ------------------------------------------------------------------------------

layers_simbologia_densitat_industrial = simbologia_general.simbologia_densitat_agregacions(
    capa_districtes=districtes_densitat_superficie_industrial,
    capa_barris=barris_densitat_superficie_industrial,
    capa_hexagons=hexagons_densitat_superficie_industrial
)

# ------------------------------------------------------------------------------
# 6.4.1. Anàlisi temporal - Visió general
# ------------------------------------------------------------------------------

layers_simbologia_parc_edificis = simbologia_general.simbologia_temporal_general(
    edificis_industrials=edificis_industrial_net,
    edificis_no_industrials=edificis_no_industrial_net
)

# ------------------------------------------------------------------------------
# 6.4.2. Anàlisi temporal - Antiguitat relativa
# ------------------------------------------------------------------------------

layers_simbologia_antiguitat_relativa_barris = simbologia_general.simbologia_temporal_barris(
    barris=barris_diferencia_mediana
)

layers_simbologia_antiguitat_relativa_edificis = simbologia_general.simbologia_temporal_edificis(
    edificis_industrials=edificis_diferencia_mediana,
    edificis_no_industrials=edificis_no_industrial_net
)

# ------------------------------------------------------------------------------
# 6.5. Addició de capes al projecte
# ------------------------------------------------------------------------------

totes_les_capes = {
    **layers_simbologia_base,
    "base_map": basemap_layer,
    **layers_simbologia_atles,
    **layers_simbologia_comparacio_industrial,
    **layers_simbologia_densitat_industrial,
    **layers_simbologia_parc_edificis,
    **layers_simbologia_antiguitat_relativa_barris,
    **layers_simbologia_antiguitat_relativa_edificis
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
# 7.3. Composició comparativa agregacions
# ------------------------------------------------------------------------------

layout_comparacio_agregacions.composicio_agregacio_comparacio_unitat(
    capes=layers_simbologia_comparacio_industrial,
    capa_terme=layers_simbologia_base["TermeMunicipal"],
    capa_extent=layers_simbologia_base["TermeMunicipal"],
)

# ------------------------------------------------------------------------------
# 7.4. Composició densitat superfície industrials MAUP
# ------------------------------------------------------------------------------

layout_maup.composicio_maup_densitat_superficie_industrial(
    capes=layers_simbologia_densitat_industrial,
    capa_terme=layers_simbologia_base["TermeMunicipal"],
    capa_extent=layers_simbologia_base["TermeMunicipal"]
)

# ------------------------------------------------------------------------------
# 7.5. Composició densitat d'edificis industrials MAUP
# ------------------------------------------------------------------------------

layout_maup.composicio_maup_densitat_edificis_industrials(
    capes=layers_simbologia_densitat_industrial,
    capa_terme=layers_simbologia_base["TermeMunicipal"],
    capa_extent=layers_simbologia_base["TermeMunicipal"],
)

# ------------------------------------------------------------------------------
# 7.6. Composició antiguitat edificis
# ------------------------------------------------------------------------------

layout_temporal.composicio_antiguitat_parc_edificis(
    capes=layers_simbologia_parc_edificis,
    capa_extent=layers_simbologia_base["TermeMunicipal"],
    capa_terme=layers_simbologia_base["TermeMunicipal"],
    capes_llegenda=layers_simbologia_parc_edificis,
)

# ------------------------------------------------------------------------------
# 7.7. Composició antiguitat relativa parc industrial
# ------------------------------------------------------------------------------

layout_temporal.composicio_antiguitat_relativa_clusters(
    capes=layers_simbologia_antiguitat_relativa_edificis,
    capa_barris=layers_simbologia_base["Barris"],
    extensions=extents_clusters_uniformes,
    capa_general_barris=layers_simbologia_antiguitat_relativa_barris,
    capa_terme=layers_simbologia_base["TermeMunicipal"]
)

# ------------------------------------------------------------------------------
# 7.7. Composició final
# ------------------------------------------------------------------------------

# Unió de les composicions que es mantenen al projecte
fusionar_layouts.fusionar_pdf(
    pdfs=[
        config.LAYOUTS["GENERAL"]["Exportacio"]["output_path"],
        config.LAYOUTS["ATLES"]["Exportacio_atles"]["output_path"],
        #config.LAYOUTS["CLUSTERS"]["Exportacio"]["output_path"]
    ],
    output_path=str(config.PATH_RESULTATS / "Informe_final.pdf")
)

