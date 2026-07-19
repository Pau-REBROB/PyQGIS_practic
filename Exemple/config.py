"""Arxiu de configuració"""

# =============================================================================
# RUTES
# =============================================================================

PATH_PROJECTE = "C:/projectes_git/PyQGIS_practic"

PATH_DADES = "C:/projectes_git/Dades"
PATH_DADES_NETES = "C:/projectes_git/Dades/PyQGIS_Repo/Dades_netes"
PATH_RESULTATS = f"{PATH_PROJECTE}/Resultats"

PATH_DADES_LIMITS = f"{PATH_DADES}/PyQGIS_Repo/Limits_administratius_BCN"
PATH_DADES_CADASTRE = f"{PATH_DADES}/PyQGIS_Repo/Cadastre"
PATH_DADES_GRAF = f"{PATH_DADES}/PyQGIS_Repo/Graf_viari"

# =============================================================================
# DADES D'ENTRADA
# =============================================================================

LAYERS = {
    "Limits_administratius": {
        "Barris": f"{PATH_DADES_LIMITS}/0301040100_Barris_UNITATS_ADM.shp",
        "Districtes": f"{PATH_DADES_LIMITS}/0301040100_Districtes_UNITATS_ADM.shp",
        "TermeMunicipal": f"{PATH_DADES_LIMITS}/0301040100_TermeMunicipal_UNITATS_ADM.shp"
    },
    "Cadastre": {
        "Edificis": f"{PATH_DADES_CADASTRE}/08900/A.ES.SDGC.BU.08900.building.gml",
        "Edificis_part": f"{PATH_DADES_CADASTRE}/08900/A.ES.SDGC.BU.08900.buildingpart.gml",
        "Parcelles": f"{PATH_DADES_CADASTRE}/08900/A.ES.SDGC.CP.08900.cadastralparcel.gml",
        "Illes": f"{PATH_DADES_CADASTRE}/08900/A.ES.SDGC.CP.08900.cadastralzoning.gml"
    },
    "Graf": {
        "Graf_trams": f"{PATH_DADES_GRAF}/BCN_GrafVial_Trams_ETRS89_SHP.shp"
    }
}

# =============================================================================
# PREPARACIÓ DE LES CAPES
# =============================================================================

CAMPS_CAPES = {
    "Limits_administratius": {
        "*": ['DISTRICTE', 'BARRI', 'PERIMETRE', 'AREA', 'TIPUS_UA', 'NOM']
                # 'DISTRICTE' codi del districte
                # 'BARRI' codi del barri
                # 'PERIMETRE' perímetre de la geometria
                # 'AREA' superfície de la geometria
                # 'TIPUS_UA' tipus d'unitat administrativa - indica si es tracta d'un barri, un districte o un terme municipal
                # 'NOM' nom de la unitat administrativa
    },
    "Cadastre": {
        'Edificis': ['gml_id', 'end', 'reference', 'localId', 'currentUse', 'numberOfDwellings', 'value'],
                # 'gml_id' codi de l'arxiu de cadastre
                # 'end' any de finalització de construcció
                # 'reference' referència del codi gml_id
                # 'localId' codi local
                # 'currentUse' ús actual
                # 'numberOfDwellings' número d'habitacions
                # 'value' valor del metre quadrat
        'Edificis_part': ['gml_id', 'localId', 'numberOfFloorsAboveGround', 'numberOfFloorsBelowGround'],
                # 'gml_id' codi de l'arxiu de cadastre
                # 'localId' codi local
                # 'numberOfFloorsAboveGround' número de pisos per sobre nivell de terra
                # 'numberOfFloorsBelowGround' número de pisos per sota terra
        'Parcelles': ['gml_id', 'areaValue', 'localId', 'nationalCadastralReference', 'pos'],
                # 'gml_id' codi de l'arxiu de cadastre
                # 'areaValue' valor del metre quadrat
                # 'localId' codi local
                # 'nationalCadastralReference' número de referència cadastral
                # 'pos' coordenades UTM
        'Illes': ['gml_id', 'areaValue', 'localId', 'nationalCadastralReference', 'pos']
    },
    "Graf": {
        "*": ['COORD_X', 'COORD_Y', 'LONGITUD', 'ANGLE', 'C_Tram', 'Distric_D', 'NDistric_D', 'TVia_D', 'NVia_D', 'Distric_E', 'NDistric_E', 'TVia_E', 'NVia_E']
                # 'COORD_X' coordenada UTM X
                # 'COORD_Y' coordenada UTM Y
                # 'LONGITUD' longitud de la via
                # 'ANGLE' angle de la via
                # 'C_Tram' codi del tram de via
                # 'Distric_D' codi districte de la part dreta
                # 'NDistric_D' nom districte de la part dreta
                # 'TVia_D' tipus de via de la part dreta
                # 'NVia_D' nom de la via de la part dreta
                # 'Distric_E' codi districte de la part esquerra
                # 'NDistric_E' nom districte de la part esquerra
                # 'TVia_E' tipus de via de la part esquerra
                # 'NVia_E'  nom de la via de la part esquerra
    }
}

# =============================================================================
# CONSTANTS DEL PROJECTE
# =============================================================================

USOS = [
    "1_residential",
    "2_agriculture",
    "3_industrial",
    "4_1_office",
    "4_2_retail",
    "4_3_publicServices"
]

ETIQUETES_USOS = {
    "1_residential": "Residencial",
    "2_agriculture": "Agricultura",
    "3_industrial": "Industrial",
    "4_1_office": "Oficines",
    "4_2_retail": "Comerç",
    "4_3_publicServices": "Serveis públics"
}

COLORS_USOS = {
    "1_residential": (255, 235, 175, 255),
    "2_agriculture": (170, 255, 115, 255),
    "3_industrial": (178, 178, 178, 255),
    "4_1_office": (255, 170, 0, 255),
    "4_2_retail": (255, 127, 0, 255),
    "4_3_publicServices": (200, 170, 220, 255)
}

def colors_mpl(us):
    """
    Funció per convertir colors en format (RGBA) de PyQGIS en format acceptat per matplotlib
    """
    r,g,b,a = COLORS_USOS[us]
    
    return (
        r/255,
        g/255,
        b/255,
        a/255
    )

# =============================================================================
# ANÀLISI
# =============================================================================

CONFIG_ANALISI = {
    "Clusters": {
        "eps": 100,
        "min_size": 5
    },

    "Isoarees": {
        "distancia": 5000,
        "interval": 250
    }
}

# =============================================================================
# SIMBOLOGIA
# =============================================================================

SIMBOLOGIA = {
    "Barris": {
        "fill_color": (255,255,255,0),
        "outline_width": 0.15,
        "stroke_color": (180,220,230,255)
    },
    "Districtes": {
        "fill_color": (255,255,255,0),
        "outline_width": 0.5,
        "stroke_color": (255,200,50,255)
    },
    "TermeMunicipal": {
        "fill_color": (255,255,255,0),
        "outline_width": 0.75,
        "stroke_color": (255,200,50,255)
    },
    "Graf": {
        "fill_color": (0,0,0,255),
        "width": 0.1,
        "outline_color": (255,255,255,255),
        "outline_width": 0.2
    },
    "Edificis": {
        "atribut": 'currentUse',
        "colors": COLORS_USOS,
        "outline_width": 0.1,
        "stroke_color": "white" 
    },
    "Clusters": {
        "outline_width": 0.2,
    },
    "Isoarees": {
        "atribut": 'cost_level',
        "num_classes": 7,
        "color_ramp": "Spectral",
        "mode": "Jenks",
        "stroke_color": (255,255,255,100),
        "stroke_width": 0.2
    },
    "Districtes_us_predominant": {
        "atribut": 'us_predominant',
        "colors_categories": COLORS_USOS,
        "outline_width": 0.5,
        "stroke_color": (120,120,120,255)
    },
    "Districtes_dominancia": {
        "atribut": 'dominancia',
        "num_classes": 5,
        "color_ramp": "YlOrRd",
        "mode": "Jenks",
        "stroke_color": (120,120,120,255),
        "stroke_width": 0.5
    },
    "Districtes_shannon": {
        "atribut": 'shannon_normalitzat',
        "num_classes": 5,
        "color_ramp": "GrYlRd",
        "mode": "Jenks",
        "stroke_color": (120,120,120,255),
        "stroke_width": 0.5
    }
}

# =============================================================================
# EXPORTACIÓ
# =============================================================================

EXPORTACIO_GRAFICS = {
    "Grafic_usos_districtes": f"{PATH_RESULTATS}/Grafic_nombreEdificis_districte.png",
    "Grafic_usos_percentatges_districtes": f"{PATH_RESULTATS}/Grafic_percentatgeEdificis_districte.png",
    "Grafic_nombre_clusters": f"{PATH_RESULTATS}/Grafic_nombreClusters.png",
    "Grafic_mida_clusters": f"{PATH_RESULTATS}/Grafic_midaClusters.png"
}

# =============================================================================
# COMPOSICIONS
# =============================================================================

LAYOUTS = {
    "ESTRUCTURA": {
        "Mapa": {
            "size": (280, 190),
            "position": (10, 10)
        },
        "Localitzador": {
            "size": (50, 50),
            "position": (240, 140)
        },
        "Titol": {
            "size": (10, 5),
            "position": (280, 10)
        },
        "Llegenda": {
            "position": (240, 60)
        },
        "Escala": {
            "position": (15, 190)
        },
        "Nord": {
            "size": (10, 10),
            "position": (15, 180)
        }
    },

    "GENERAL":{
        "Titol": {
            "titol": "Ús dels edificis de la ciutat de Barcelona - font: Cadastre",
            "font": "Calibri",
            "font_size": 20,
            "font_color": (0,0,0,255),
            "backg_color": (100,100,100,180),
            "frame_color": (255, 255, 255, 200)
        },
        "Llegenda": {
            "titol": "Classificació dels edificis",
            "font": "Calibri",
            "font_size": 10,
            "font_color": (0,0,0,255),
            "backg_color": (100,100,100,180)
        },
        "Escala": {
            "font": "Calibri",
            "font_color": (0,0,0,255)
        },
        "Nord": {
            "path": "C:/projectes_git/Dades/nord2.png"
        },
        "Exportacio": {
            "output_path": f"{PATH_RESULTATS}/Classificacio_edificis.pdf",
            "dpi": 300
        }
    },

    "ATLES": {
        "Titol": {
            "titol": "Ús dels edificis de la ciutat de Barcelona - Districte: [% \"NOM\" %]",
            "font": "Calibri",
            "font_size": 20,
            "font_color": (0,0,0,255),
            "backg_color": (100,100,100,180),
            "frame_color": (255, 255, 255, 200)
        },
        "Llegenda": {
            "titol": "Classificació dels edificis",
            "font": "Calibri",
            "font_size": 10,
            "font_color": (0,0,0,255),
            "backg_color": (100,100,100,180)
        },
        "Escala": {
            "font": "Calibri",
            "font_color": (0,0,0,255)
        },
        "Nord": {
            "path": "C:/projectes_git/Dades/nord2.png"
        },
        "Generacio": {
            "camp": '"NOM"'
        },
        "Exportacio": {
            "output_path": f"{PATH_RESULTATS}/AtlesDistrictes.pdf",
            "dpi": 300
        }
    },

    "ANALISI":{
        "Titol": {
            "titol": "Anàlisi dels usos dels edificis de la ciutat de Barcelona - font: Cadastre",
            "font": "Calibri",
            "font_size": 20,
            "font_color": (0,0,0,255),
            "backg_color": (100,100,100,180),
            "frame_color": (255, 255, 255, 200)
        },
        "Llegenda": {
            "titol": "Classificació dels edificis",
            "font": "Calibri",
            "font_size": 10,
            "font_color": (0,0,0,255),
            "backg_color": (100,100,100,180)
        },
        "Escala": {
            "font": "Calibri",
            "font_color": (0,0,0,255)
        },
        "Nord": {
            "path": "C:/projectes_git/Dades/nord2.png"
        },
        "Grafic_total": {
            "path": f"{PATH_RESULTATS}/Grafic_nombreEdificis_districte.png",
            "size": (120, 60),
            "position": (15, 145)
        },
        "Grafic_percentatge": {
            "path": f"{PATH_RESULTATS}/Grafic_percentatgeEdificis_districte.png",
            "size": (120, 60),
            "position": (145, 145)
        },
        "Exportacio": {
            "output_path": f"{PATH_RESULTATS}/Analisi_edificis.pdf",
            "dpi": 300
        }
    },

    "CLUSTERS": {
        "Titol": {
            "titol": "Concentracions espacials dels usos dels edificis de la ciutat de Barcelona - font: Cadastre",
            "font": "Calibri",
            "font_size": 20,
            "font_color": (0,0,0,255),
            "backg_color": (100,100,100,180),
            "frame_color": (255, 255, 255, 200)
        },
        "Llegenda": {
            "titol": "Agrupacions espacials",
            "font": "Calibri",
            "font_size": 10,
            "font_color": (0,0,0,255),
            "backg_color": (100,100,100,180)
        },
        "Escala": {
            "font": "Calibri",
            "font_color": (0,0,0,255)
        },
        "Nord": {
            "path": "C:/projectes_git/Dades/nord2.png"
        },
        "Grafic_clusters": {
            "path": f"{PATH_RESULTATS}/Grafic_nombreClusters.png",
            "size": (120, 60),
            "position": (15, 145)
        },
        "Grafic_mida": {
            "path": f"{PATH_RESULTATS}/Grafic_midaClusters.png",
            "size": (120, 60),
            "position": (145, 145)
        },
        "Exportacio": {
            "output_path": f"{PATH_RESULTATS}/Analisi_clusters.pdf",
            "dpi": 300
        }
    }
}
