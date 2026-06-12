"""CONFIGURACIÓ"""

# Arxiu de configuració

LLISTA_MODULS = [
    inicialitzar_projecte,
    recarregar_moduls,
    carregar_capes,
    netejar_capa,
    desar_carregar_capa,
    netejar_grup,
    seleccio_atribut,
    clusters_dbscan,
    envolvent_clusters,
    generacio_centroides,
    isoarees_qneat3,
    generar_layout,
    afegir_mapa,
    afegir_titol,
    afegir_llegenda,
    afegir_escala,
    afegir_nord,
    exportar_layout
]

PATH_DADES = "C:/projectes_git/Dades/PyQGIS_Repo"

LAYERS = {
"Limits_administratius": {
    "Barris": f"{PATH_DADES}/Limits_administratius_BCN/0301040100_Barris_UNITATS_ADM.shp",
    "Districtes": f"{PATH_DADES}/Limits_administratius_BCN/0301040100_Districtes_UNITATS_ADM.shp",
    "TermeMunicipal": f"{PATH_DADES}/Limits_administratius_BCN/0301040100_TermeMunicipal_UNITATS_ADM.shp"
},
"Cadastre": {
    "Edificis": f"{PATH_DADES}/Cadastre/08900/A.ES.SDGC.BU.08900.building.gml",
    "Edificis_part": f"{PATH_DADES}/Cadastre/08900/A.ES.SDGC.BU.08900.buildingpart.gml",
    "Parcelles": f"{PATH_DADES}/Cadastre/08900/A.ES.SDGC.CP.08900.cadastralparcel.gml",
    "Illes": f"{PATH_DADES}/Cadastre/08900/A.ES.SDGC.CP.08900.cadastralzoning.gml"
},
"Graf": {
    "Graf_trams": f"{PATH_DADES}/Graf_viari/BCN_GrafVial_Trams_ETRS89_SHP.shp",
    #"Graf_nodes": f"{PATH_DADES}/Graf_viari/BCN_GrafVial_Nodes_ETRS89_SHP.shp"
}}

