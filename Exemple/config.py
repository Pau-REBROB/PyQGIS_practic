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

COLORS_CLUSTERS = {
    "1_residential": (255, 235, 175, 150),
    "2_agriculture": (170, 255, 115, 150),
    "3_industrial": (178, 178, 178, 150),
    "4_1_office": (255, 170, 0, 150),
    "4_2_retail": (255, 127, 0, 150),
    "4_3_publicServices": (200, 170, 220, 150)
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

COLORS_BIVARIANT = {
    # Diversitat baixa / # Dominància variant
    "Baixa_Baixa": (247, 244, 235, 255),
    "Mitjana_Baixa": (255, 198, 150, 255),
    "Alta_Baixa": (255, 127, 39, 255),

    # Diversitat mitjana / # Dominància variant
    "Baixa_Mitjana": (150, 205, 228, 255),
    "Mitjana_Mitjana": (206, 186, 170, 255),
    "Alta_Mitjana": (215, 134, 74, 255),

    # Diversitat alta / # Dominància variant
    "Baixa_Alta": (48, 165, 214, 255),
    "Mitjana_Alta": (94, 142, 166, 255),
    "Alta_Alta": (145, 110, 82, 255),

    # Valors no vàlids
    "No_valid": (200,200,200,80)
}

MIDA_HEXAGON = 150

MIN_EDIFICIS = 3

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

CLASSIFICACIO_DOMINANCIA = {
    "Molt baixa": 5,
    "Baixa": 15,
    "Mitjana": 30,
    "Alta": 50
}

CLASSIFICACIO_SHANNON = {
    "Molt baixa": 0.40,
    "Baixa": 0.55,
    "Mitjana": 0.70,
    "Alta": 0.85
}

CLASSIFICACIO_ACCESSIBILITAT = {
    "Alta": 500,
    "Mitjana": 2000,
    "Alta": 5000
}

INTERVALS_DOMINANCIA = [
    0.0,
    14.3,
    37.5,
    57.1,
    83.3,
    100.0
]

INTERVALS_SHANNON = [
    0.00,
    0.65,
    0.82,
    0.95,
    1.00
]

INTERVALS_ACCESSIBILITAT = [
    0,
    250,
    500,
    1000,
    2000,
    3000,
    5000
]

# =============================================================================
# SIMBOLOGIA
# =============================================================================

SIMBOLOGIA = {
    "Barris": {
        "nom": "Barris",
        "fill_color": (255,255,255,0),
        "outline_width": 0.15,
        "stroke_color": (180,220,230,255)
    },
    "Districtes": {
        "nom": "Districtes",
        "fill_color": (255,255,255,0),
        "outline_width": 0.5,
        "stroke_color": (255,200,50,255)
    },
    "TermeMunicipal": {
        "nom": "Terme municipal",
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
        "colors_categories": COLORS_USOS,
        "outline_width": 0.1,
        "stroke_color": (255,255,255,255) 
    },
    "Clusters": {
        "nom": "clusters",
        "outline_width": 0.2,
    },
    "Zones": {
        "nom": "zones",
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
    "Us_predominant": {
        "Districtes": {
            "atribut": 'us_predominant',
            #"nom": "Ús predominant districtes",
            "colors_categories": COLORS_USOS,
            "outline_width": 0.5,
            "stroke_color": (120,120,120,255)
        },
        "Barris": {
            "atribut": 'us_predominant',
            #"nom": "Ús predominant barris",
            "colors_categories": COLORS_USOS,
            "outline_width": 0.35,
            "stroke_color": (120,120,120,255)
        },
    },
    "Dominancia": {
        "Districtes": {
            "atribut": 'dominancia',
            "num_classes": 5,
            "color_ramp": "YlOrRd",
            "mode": "Jenks",
            "stroke_color": (120,120,120,255),
            "stroke_width": 0.50
        },
        "Barris": {
            "atribut": 'dominancia',
            "num_classes": 5,
            "color_ramp": "YlOrRd",
            "mode": "Jenks",
            "stroke_color": (120,120,120,255),
            "stroke_width": 0.35
        },
    },
    "Shannon": {
        "Districtes": {
            "atribut": 'shannon_norm',
            "num_classes": 5,
            "color_ramp": "Blues",
            "mode": "Jenks",
            "stroke_color": (120,120,120,255),
            "stroke_width": 0.50
        },
        "Barris": {
            "atribut": 'shannon_norm',
            "num_classes": 5,
            "color_ramp": "Blues",
            "mode": "Jenks",
            "stroke_color": (120,120,120,255),
            "stroke_width": 0.35
        },
    },
    "Bivariant": {
        "Districtes": {
            "atribut": 'classe_bivariant',
            "colors_categories": COLORS_BIVARIANT,
            "outline_width": 0.50,
            "stroke_color": (120,120,120,255)    
        },
        "Barris": {
            "atribut": 'classe_bivariant',
            "colors_categories": COLORS_BIVARIANT,
            "outline_width": 0.35,
            "stroke_color": (120,120,120,255)    
        }
    },
    "Hexagons_us_predominant": {
        "atribut": 'us_predominant',
        "colors_categories": COLORS_USOS,
        "outline_width": 0.25,
        "stroke_color": (120,120,120,255)
    },
    "Hexagons_dominancia": {
        "color_ramp": "YlOrRd",
        "intervals": INTERVALS_DOMINANCIA,
        "atribut": 'dominancia',
        "stroke_color": (120,120,120,255),
        "stroke_width": 0.25
    },
    "Hexagons_shannon": {
        "color_ramp": "Blues",
        "intervals": INTERVALS_SHANNON,
        "atribut": 'shannon_norm',
        "stroke_color": (120,120,120,255),
        "stroke_width": 0.25
    },
    "Hexagons_bivariant": {
        "atribut": 'classe_bivariant_access',
        "colors_categories": COLORS_BIVARIANT,
        "outline_width": 0.25,
        "stroke_color": (255,255,255,100)
    },
    "Hexagons_no_valids": {
        "nom": "sense dades",
        "fill_color": COLORS_BIVARIANT["No_valid"],
        "outline_width": 0.2,
        "stroke_color": (255,255,255,200)
    },
    "Accessibilitat": {
        "Edificis_accessibilitat": {
            "color_ramp": "RdBu",
            "intervals": INTERVALS_ACCESSIBILITAT,
            "atribut": 'accessibilitat',
            "stroke_color": (255,255,255,255),
            "stroke_width": 0.01,
            "invert_ramp": True
        } ,
        "Graf_accessibilitat": {
            "nom": "Graf viari",
            "fill_color": (255,255,255,255),
            "width": 0.1,
            "outline_color": (50,50,50,255),
            "outline_width": 0.2
        },
        "Clusters_accessibilitat": {
            "nom": "Agrupacions comercials",
            "fill_color": (255, 127, 0, 50),
            "outline_width": 0.25,
            "stroke_color": (255, 127, 0, 200)
        },
        "Terme_accessibilitat": {
            "nom": "terme municipal",
            "fill_color": (0,0,0,0),
            "outline_width": 0.2,
            "stroke_color": (255,255,255,255)
        }
    }
}

# =============================================================================
# EXPORTACIÓ
# =============================================================================

# EXPORTACIO_GRAFICS = {
#     "Grafic_usos_districtes": f"{PATH_RESULTATS}/Grafic_nombreEdificis_districte.png",
#     "Grafic_usos_percentatges_districtes": f"{PATH_RESULTATS}/Grafic_percentatgeEdificis_districte.png",
#     "Grafic_nombre_clusters": f"{PATH_RESULTATS}/Grafic_nombreClusters.png",
#     "Grafic_mida_clusters": f"{PATH_RESULTATS}/Grafic_midaClusters.png"
# }

EXPORTACIO_ISOAREES = {
    "interpolation": f"{PATH_RESULTATS}/output_interpolation.tif",
    "polygons": f"{PATH_RESULTATS}/output_polygons.shp"
}

# =============================================================================
# COMPOSICIONS
# =============================================================================

LAYOUTS = {
    "ESTRUCTURA": {
        "Mapa": {
            "factor_escala": 0.65,
            "size": (290, 200),
            "position": (3.5, 5),
            "rotacio": 45,
            "offset_x": 1000,
            "offset_y": 0
        },
        "Capçalera": {
            "text_size": (280, 5),
            "text_position": (10, 10),
            "backg_size": (280, 2),
            "backg_position": (10, 20)
        },
        "Titol": {
            "size": (280, 5),
            "position": (10, 10)
        },
        "Llegenda": {
            "position": (10, 30)
        },
        "Escala": {
            "position": (10, 120)
        },
        "Nord": {
            "size": (10, 10),
            "position": (10, 110)
        }
    },

    "ESTRUCTURA_ATLES": {
        "Mapa": {
            "factor_escala": 0.60,
            "size": (290, 200),
            "position": (3.5, 5),
            "rotacio": 45,
            "offset_x": 0,
            "offset_y": 0
        },
        "Localitzador": {
            "size": (50, 50),
            "position": (240, 140)
        },
        "Capçalera": {
            "text_size": (280, 5),
            "text_position": (10, 10),
            "backg_size": (280, 2),
            "backg_position": (10, 20)
        },
        "Titol": {
            "size": (280, 5),
            "position": (10, 10)
        },
        "Llegenda": {
            "position": (10, 30)
        },
        "Escala": {
            "position": (10, 120)
        },
        "Nord": {
            "size": (10, 10),
            "position": (10, 110)
        }
    },

    "ESTRUCTURA_CLUSTERS": {
        "Mapa": {
            "factor_escala": 0.65,
            "size": (290, 200),
            "position": (3.5, 5),
            "rotacio": 45,
            "offset_x": 1000,
            "offset_y": 750
        },
        "Capçalera": {
            "text_size": (280, 5),
            "text_position": (10, 10),
            "backg_size": (280, 2),
            "backg_position": (10, 20)
        },
        # "Titol": {
        #     "size": (280, 5),
        #     "position": (10, 10)
        # },
        "Llegenda": {
            "position": (10, 30)
        },
        "Escala": {
            "position": (260, 190)
        },
        "Nord": {
            "size": (10, 10),
            "position": (260, 180)
        }
    },

    "ESTRUCTURA_ESPECIALITZACIO": {
        "Mapa_us": {
            "factor_escala": 1.00,
            "size": (90, 90),
            "position": (10, 25)
        },
        "Mapa_dominancia": {
            "factor_escala": 1.00,
            "size": (90, 90),
            "position": (105, 25)
        },
        "Mapa_shannon": {
            "factor_escala": 1.00,
            "size": (90, 90),
            "position": (200, 25)
        },
        "Fons": {
            "size": (280, 180),
            "position": (10, 20)
        },
        "Titol": {
            "size": (280, 10),
            "position": (10, 5)
        },
        "Titol_us": {
            "size": (90, 10),
            "position": (10, 120)
        },
        "Subtitol_us": {
            "size": (90, 12),
            "position": (10, 130)
        },
        "Titol_dominancia": {
            "size": (90, 10),
            "position": (105, 120)
        },
        "Subtitol_dominancia": {
            "size": (90, 12),
            "position": (105, 130)
        },
        "Titol_shannon": {
            "size": (90, 10),
            "position": (200, 120)
        },
        "Subtitol_shannon": {
            "size": (90, 12),
            "position": (200, 130)
        },
        "Llegenda_us": {
            "titol": "Ús majoritari dels edificis",
            "position": (10, 145)
        },
        "Llegenda_dominancia": {
            "titol": "Diferència (%) entre usos",
            "position": (106, 145)
        },
        "Llegenda_shannon": {
            "titol": "Índex de Shannon normalitzat",
            "position": (202, 145)
        }
    },

    "ESTRUCTURA_BIVARIANT": {
        "Districtes": {
            "Mapa": {
                "factor_escala": 0.75,
                "size": (280, 190),
                "position": (10, 20),
                "rotacio": 45,
                "offset_x": 3000,
                "offset_y": 300
            },
            "Capçalera": {
                "text_size": (280, 5),
                "text_position": (10, 10),
                "backg_size": (280, 2),
                "backg_position": (10, 20)
            },
            "Llegenda": {
                "position": (238, 143)
            },
            "Eix_dominancia_llegenda": {
                "position": (238, 131),
                "size": (50, 10),
                "alineacio": "left",
                "rotacio": 0
            },
            "Eix_diversitat_llegenda": {
                "position": (221, 175),
                "size": (50, 10),
                "alineacio": "left",
                "rotacio": -90
            },
            "Labels_superiors_llegenda": {
                "position": (240, 137),
                "size": (26, 6)
            },
            "Labels_laterals_llegenda": {
                "position": (228, 145),
                "size": (6, 26)
            },
            "Escala": {
                "position": (221, 180),
            },
            "Nord": {
                "size": (10, 10),
                "position": (221, 192)
            }
        },
        "Barris": {
            "Mapa": {
                "factor_escala": 0.75,
                "size": (280, 190),
                "position": (10, 20),
                "rotacio": 45,
                "offset_x": 3000,
                "offset_y": 300
            },
            "Capçalera": {
                "text_size": (280, 5),
                "text_position": (10, 10),
                "backg_size": (280, 2),
                "backg_position": (10, 20)
            },
            "Llegenda": {
                "position": (238, 143)
            },
            "Eix_dominancia_llegenda": {
                "position": (238, 131),
                "size": (50, 10),
                "alineacio": "left",
                "rotacio": 0
            },
            "Eix_diversitat_llegenda": {
                "position": (221, 175),
                "size": (50, 10),
                "alineacio": "left",
                "rotacio": -90
            },
            "Labels_superiors_llegenda": {
                "position": (240, 137),
                "size": (26, 6)
            },
            "Labels_laterals_llegenda": {
                "position": (228, 145),
                "size": (6, 26)
            },
            "Escala": {
                "position": (221, 180),
            },
            "Nord": {
                "size": (10, 10),
                "position": (221, 192)
            }
        },
        "Hexagons": {
            "Mapa": {
                "factor_escala": 0.75,
                "size": (280, 190),
                "position": (10, 20),
                "rotacio": 45,
                "offset_x": 3000,
                "offset_y": 300
            },
            "Text_titol": {
                "size": (280, 5),
                "position": (10, 7.5)
            },
            "Subtitol": {
                "text_size": (280, 5),
                "text_position": (10, 17.5),
                "backg_size": (280, 2),
                "backg_position": (10, 27.5)
            },
            "Llegenda": {
                "position": (243, 132)
            },
            "Eix_dominancia_llegenda": {
                "position": (243, 120),
                "size": (50, 10),
                "alineacio": "left",
                "rotacio": 0
            },
            "Eix_diversitat_llegenda": {
                "position": (226, 164),
                "size": (50, 10),
                "alineacio": "left",
                "rotacio": -90
            },
            "Labels_superiors_llegenda": {
                "position": (245, 126),
                "size": (26, 6)
            },
            "Labels_laterals_llegenda": {
                "position": (233, 134),
                "size": (6, 26)
            },
            "Llegenda_no_valids": {
                "position": (226, 166)
            },
            "Escala": {
                "position": (226, 185),
            },
            "Nord": {
                "size": (10, 10),
                "position": (226, 197)
            }
        }
    },

    # "ESTRUCTURA_HEXAGONS": {
    #     "Mapa": {
    #         "factor_escala": 0.75,
    #         "size": (280, 190),
    #         "position": (10, 20),
    #         "rotacio": 45,
    #         "offset_x": 3000,
    #         "offset_y": 300
    #     },
    #     "Text_titol": {
    #         "size": (280, 5),
    #         "position": (10, 7.5)
    #     },
    #     "Subtitol": {
    #         "text_size": (280, 5),
    #         "text_position": (10, 17.5),
    #         "backg_size": (280, 2),
    #         "backg_position": (10, 27.5)
    #     },
    #     "Llegenda": {
    #         "position": (243, 132)
    #     },
    #     "Eix_dominancia_llegenda": {
    #         "position": (243, 120),
    #         "size": (50, 10),
    #         "alineacio": "left",
    #         "rotacio": 0
    #     },
    #     "Eix_diversitat_llegenda": {
    #         "position": (226, 164),
    #         "size": (50, 10),
    #         "alineacio": "left",
    #         "rotacio": -90
    #     },
    #     "Labels_superiors_llegenda": {
    #         "position": (245, 126),
    #         "size": (26, 6)
    #     },
    #     "Labels_laterals_llegenda": {
    #         "position": (233, 134),
    #         "size": (6, 26)
    #     },
    #     "Llegenda_no_valids": {
    #         "position": (226, 166)
    #     },
    #     "Escala": {
    #         "position": (226, 185),
    #     },
    #     "Nord": {
    #         "size": (10, 10),
    #         "position": (226, 197)
    #     }
    # },

    "ESTRUCTURA_ACCESS": {
        "Mapa": {
            "factor_escala": 0.70,
            "size": (290, 200),
            "position": (3.5, 5),
            "rotacio": 45,
            "offset_x": 0,
            "offset_y": 0
        },
        "Capçalera": {
            "text_size": (280, 5),
            "text_position": (10, 10),
            "backg_size": (280, 2),
            "backg_position": (10, 20)
        },
        "Llegenda": {
            "position": (240, 115) #(15, 60)
        },
        "Escala": {
            "position": (240, 190) #(15, 190)
        },
        "Nord": {
            "size": (10, 10),
            "position": (240, 180) #(15, 180)
        }
    },
    

    "GENERAL":{
        "Capçalera": {
            "color": (100,100,100,180),
            "outline_color": (85,85,85,255),
            "outline_width": 0.40,
            "text": "Ús dels edificis de Barcelona - font: Cadastre",
            "font": "Calibri",
            "font_size": 20,
            "font_color": (0,0,0,255)
        },
        "Llegenda": {
            "titol": "Classificació dels edificis",
            "font": "Calibri",
            "font_size": 10,
            "font_color": (0,0,0,255),
            "backg_color": (150,150,150,180)
        },
        "Escala": {
            "tipus": "Single Box",
            "font": "Calibri",
            "font_size": 10,
            "font_color": (0,0,0,255)
        },
        "Nord": {
            "image_path": "C:/projectes_git/Dades/nord2.png"
        },
        "Exportacio": {
            "output_path": f"{PATH_RESULTATS}/Classificacio_edificis.pdf",
            "dpi": 500
        }
    },

    "ATLES": {
        "Capçalera": {
            "color": (100,100,100,180),
            "outline_color": (85,85,85,255),
            "outline_width": 0.40,
            "text": "Ús dels edificis de la ciutat de Barcelona - Districte: [% \"NOM\" %]",
            "font": "Calibri",
            "font_size": 20,
            "font_color": (0,0,0,255)
        },
        # "Titol": {
        #     "titol": "Ús dels edificis de la ciutat de Barcelona - Districte: [% \"NOM\" %]",
        #     "font": "Calibri",
        #     "font_size": 20,
        #     "font_color": (0,0,0,255),
        #     "alineacio": "left",
        #     "backg_color": (100,100,100,180),
        #     "frame_color": (255, 255, 255, 200)
        # },
        "Llegenda": {
            "titol": "Classificació dels edificis",
            "font": "Calibri",
            "font_size": 10,
            "font_color": (0,0,0,255),
            "backg_color": (100,100,100,180)
        },
        "Escala": {
            "tipus": "Single Box",
            "font": "Calibri",
            "font_size": 10,
            "font_color": (0,0,0,255)
        },
        "Nord": {
            "image_path": "C:/projectes_git/Dades/nord2.png"
        },
        "Generacio": {
            "camp": '"NOM"'
        },
        "Exportacio": {
            "output_path": f"{PATH_RESULTATS}/AtlesDistrictes.pdf",
            "dpi": 300
        }
    },

    # "ANALISI":{
    #     "Titol": {
    #         "titol": "Anàlisi dels usos dels edificis de la ciutat de Barcelona - font: Cadastre",
    #         "font": "Calibri",
    #         "font_size": 20,
    #         "font_color": (0,0,0,255),
    #         "alineacio": "left",
    #         "backg_color": (100,100,100,180),
    #         "frame_color": (255, 255, 255, 200)
    #     },
    #     "Llegenda": {
    #         "titol": "Classificació dels edificis",
    #         "font": "Calibri",
    #         "font_size": 10,
    #         "font_color": (0,0,0,255),
    #         "backg_color": (100,100,100,180)
    #     },
    #     "Escala": {
    #         "tipus": "Single Box",
    #         "font": "Calibri",
    #         "font_size": 10,
    #         "font_color": (0,0,0,255)
    #     },
    #     "Nord": {
    #         "image_path": "C:/projectes_git/Dades/nord2.png"
    #     },
    #     "Grafic_total": {
    #         "path": f"{PATH_RESULTATS}/Grafic_nombreEdificis_districte.png",
    #         "size": (120, 60),
    #         "position": (15, 145)
    #     },
    #     "Grafic_percentatge": {
    #         "path": f"{PATH_RESULTATS}/Grafic_percentatgeEdificis_districte.png",
    #         "size": (120, 60),
    #         "position": (145, 145)
    #     },
    #     "Exportacio": {
    #         "output_path": f"{PATH_RESULTATS}/Analisi_edificis.pdf",
    #         "dpi": 300
    #     }
    # },

    "CLUSTERS": {
        # "Titol": {
        #     "titol": "Concentracions espacials dels usos dels edificis de la ciutat de Barcelona - font: Cadastre",
        #     "font": "Calibri",
        #     "font_size": 20,
        #     "font_color": (0,0,0,255),
        #     "alineacio": "left",
        #     "backg_color": (100,100,100,180),
        #     "frame_color": (255, 255, 255, 200)
        # },
        "Capçalera": {
            "color": (100,100,100,180),
            "outline_color": (85,85,85,255),
            "outline_width": 0.40,
            "text": "Concentració espacial dels usos dels edificis de la ciutat de Barcelona",
            "font": "Calibri",
            "font_size": 20,
            "font_color": (0,0,0,255)
        },
        "Llegenda": {
            "titol": "Agrupacions espacials",
            "font": "Calibri",
            "font_size": 10,
            "font_color": (0,0,0,255),
            "backg_color": (100,100,100,180)
        },
        "Escala": {
            "tipus": "Single Box",
            "font": "Calibri",
            "font_size": 10,
            "font_color": (0,0,0,255)
        },
        "Nord": {
            "image_path": "C:/projectes_git/Dades/nord2.png"
        },
        "Exportacio": {
            "output_path": f"{PATH_RESULTATS}/Analisi_clusters.pdf",
            "dpi": 500
        }
    },

    "ESPECIALITZACIO":{
        "Fons": {
            "color": (240,240,240,255)
        },
        "Titol": {
            "titol": "Especialització funcional de Barcelona",
            "font": "Calibri",
            "font_size": 20,
            "font_color": (0,0,0,255),
            "alineacio": "center",
            "backg_color": (100,100,100,180),
            "frame_color": (255, 255, 255, 200)
        },
        "Titol_us": {
            "titol": "Us predominant",
            "font": "Calibri Bold",
            "font_size": 16,
            "font_color": (0,0,0,255),
            "alineacio": "left",
            "backg_color": (100,100,100,180),
            "frame_color": (255, 255, 255, 200)
        },
        "Subtitol_us": {
            "subtitol": "Ús majoritari dels edificis del districte",
            "font": "Calibri Bold",
            "font_size": 12,
            "font_color": (10,10,10,255),
            "alineacio": "left",
            "backg_color": (100,100,100,180),
            "frame_color": (255, 255, 255, 200)
        },
        "Titol_dominancia": {
            "titol": "Dominancia funcional",
            "font": "Calibri Bold",
            "font_size": 16,
            "font_color": (0,0,0,255),
            "alineacio": "left",
            "backg_color": (100,100,100,180),
            "frame_color": (255, 255, 255, 200)
        },
        "Subtitol_dominancia": {
            "subtitol": "Diferència percentual entre el primer i el segon ús",
            "font": "Calibri Bold",
            "font_size": 12,
            "font_color": (10,10,10,255),
            "alineacio": "left",
            "backg_color": (100,100,100,180),
            "frame_color": (255, 255, 255, 200)
        },
        "Titol_shannon": {
            "titol": "Diversitat funcional",
            "font": "Calibri Bold",
            "font_size": 16,
            "font_color": (0,0,0,255),
            "alineacio": "left",
            "backg_color": (100,100,100,180),
            "frame_color": (255, 255, 255, 200)
        },
        "Subtitol_shannon": {
            "subtitol": "Índex de Shannon normalitzat",
            "font": "Calibri Bold",
            "font_size": 12,
            "font_color": (10,10,10,255),
            "alineacio": "left",
            "backg_color": (100,100,100,180),
            "frame_color": (255, 255, 255, 200)
        },
        "Llegenda": {
            "font": "Calibri",
            "font_size": 10,
            "font_color": (0,0,0,255),
            "backg_color": (100,100,100,180)
        },
        "Exportacio": {
            "output_path": f"{PATH_RESULTATS}/Especialitzacio_districtes.pdf",
            "dpi": 500
        }
    },

    "BIVARIANT": {
        "Districtes": {
            "Capçalera": {
                "color": (100,100,100,180),
                "outline_color": (85,85,85,255),
                "outline_width": 0.40,
                "text": "Especialització funcional bivariant dels districtes de Barcelona",
                "font": "Calibri",
                "font_size": 20,
                "font_color": (0,0,0,255)
            },
            "Llegenda": {
                "cell": 10,
                "gap": 0.5,
                "colors": COLORS_BIVARIANT
            },
            "Eix_dominancia_llegenda": {
                "text": "Dominància funcional",
                "font": "Calibri",
                "font_size": 12,
                "font_color": (0,0,0,255)
            },
            "Eix_diversitat_llegenda": {
                "text": "Diversitat funcional",
                "font": "Calibri",
                "font_size": 12,
                "font_color": (0,0,0,255)
            },
            "Labels_superiors_llegenda": {
                "cell": 10,
                "gap": 0.5,
                "font": "Calibri",
                "font_size": 8,
                "font_color": (0,0,0,255)
            },
            "Labels_laterals_llegenda": {
                "cell": 10,
                "gap": 0.5,
                "font": "Calibri",
                "font_size": 8,
                "font_color": (0,0,0,255)
            },
            "Escala": {
                "tipus": "Single Box",
                "font": "Calibri",
                "font_size": 10,
                "font_color": (0,0,0,255)
            },
            "Nord": {
                "image_path": "C:/projectes_git/Dades/nord2.png"
            },
            "Exportacio": {
                "output_path": f"{PATH_RESULTATS}/Analisi_bivariant_districtes.pdf",
                "dpi": 500
            }
        },
        "Barris": {
            "Capçalera": {
                "color": (100,100,100,180),
                "outline_color": (85,85,85,255),
                "outline_width": 0.40,
                "text": "Especialització funcional bivariant dels barris de Barcelona",
                "font": "Calibri",
                "font_size": 20,
                "font_color": (0,0,0,255)
            },
            "Llegenda": {
                "cell": 10,
                "gap": 0.5,
                "colors": COLORS_BIVARIANT
            },
            "Eix_dominancia_llegenda": {
                "text": "Dominància funcional",
                "font": "Calibri",
                "font_size": 12,
                "font_color": (0,0,0,255)
            },
            "Eix_diversitat_llegenda": {
                "text": "Diversitat funcional",
                "font": "Calibri",
                "font_size": 12,
                "font_color": (0,0,0,255)
            },
            "Labels_superiors_llegenda": {
                "cell": 10,
                "gap": 0.5,
                "font": "Calibri",
                "font_size": 8,
                "font_color": (0,0,0,255)
            },
            "Labels_laterals_llegenda": {
                "cell": 10,
                "gap": 0.5,
                "font": "Calibri",
                "font_size": 8,
                "font_color": (0,0,0,255)
            },
            "Escala": {
                "tipus": "Single Box",
                "font": "Calibri",
                "font_size": 10,
                "font_color": (0,0,0,255)
            },
            "Nord": {
                "image_path": "C:/projectes_git/Dades/nord2.png"
            },
            "Exportacio": {
                "output_path": f"{PATH_RESULTATS}/Analisi_bivariant_barris.pdf",
                "dpi": 500
            }
        },
        "Hexagons": {
            "Text_titol": {
                #"color": (100,100,100,180),
                #"outline_color": (85,85,85,255),
                #"outline_width": 0.40,
                "text": "Especialització funcional bivariant dels usos dels edificis Barcelona",
                "font": "Calibri",
                "font_size": 20,
                "font_color": (0,0,0,255),
            },
            "Subtitol": {
                "color": (100,100,100,180),
                "outline_color": (85,85,85,255),
                "outline_width": 0.40,
                "text": "Malla hexagonal de 150 m. L'anàlisi bivariant només s'aplica als hexàgons amb un mínim de 3 edificis",
                "font": "Calibri",
                "font_size": 14,
                "font_color": (0,0,0,255),
            },
            "Llegenda": {
                "cell": 10,
                "gap": 0.5,
                "colors": COLORS_BIVARIANT
            },
            "Eix_dominancia_llegenda": {
                "text": "Dominància funcional",
                "font": "Calibri",
                "font_size": 12,
                "font_color": (0,0,0,255)
            },
            "Eix_diversitat_llegenda": {
                "text": "Diversitat funcional",
                "font": "Calibri",
                "font_size": 12,
                "font_color": (0,0,0,255)
            },
            "Labels_superiors_llegenda": {
                "cell": 10,
                "gap": 0.5,
                "font": "Calibri",
                "font_size": 8,
                "font_color": (0,0,0,255)
            },
            "Labels_laterals_llegenda": {
                "cell": 10,
                "gap": 0.5,
                "font": "Calibri",
                "font_size": 8,
                "font_color": (0,0,0,255)
            },
            "Llegenda_no_valids": {
                "titol": "Hexàgons amb menys de 3 edificis",
                "font": "Calibri",
                "font_size": 12,
                "font_color": (0,0,0,255),
                "backg_color": (0,0,0,0)
            },
            "Escala": {
                "tipus": "Single Box",
                "font": "Calibri",
                "font_size": 10,
                "font_color": (0,0,0,255)
            },
            "Nord": {
                "image_path": "C:/projectes_git/Dades/nord2.png"
            },
            "Exportacio": {
                "output_path": f"{PATH_RESULTATS}/Analisi_bivariant_hexagons.pdf",
                "dpi": 300
            }
        }
    },

    # "HEXAGONS": {
    #     "Text_titol": {
    #         #"color": (100,100,100,180),
    #         #"outline_color": (85,85,85,255),
    #         #"outline_width": 0.40,
    #         "text": "Especialització funcional bivariant dels usos dels edificis Barcelona",
    #         "font": "Calibri",
    #         "font_size": 20,
    #         "font_color": (0,0,0,255),
    #     },
    #     "Subtitol": {
    #         "color": (100,100,100,180),
    #         "outline_color": (85,85,85,255),
    #         "outline_width": 0.40,
    #         "text": "Malla hexagonal de 150 m. L'anàlisi bivariant només s'aplica als hexàgons amb un mínim de 3 edificis",
    #         "font": "Calibri",
    #         "font_size": 14,
    #         "font_color": (0,0,0,255),
    #     },
    #     "Llegenda": {
    #         "cell": 10,
    #         "gap": 0.5,
    #         "colors": COLORS_BIVARIANT
    #     },
    #     "Eix_dominancia_llegenda": {
    #         "text": "Dominància funcional",
    #         "font": "Calibri",
    #         "font_size": 12,
    #         "font_color": (0,0,0,255)
    #     },
    #     "Eix_diversitat_llegenda": {
    #         "text": "Diversitat funcional",
    #         "font": "Calibri",
    #         "font_size": 12,
    #         "font_color": (0,0,0,255)
    #     },
    #     "Labels_superiors_llegenda": {
    #         "cell": 10,
    #         "gap": 0.5,
    #         "font": "Calibri",
    #         "font_size": 8,
    #         "font_color": (0,0,0,255)
    #     },
    #     "Labels_laterals_llegenda": {
    #         "cell": 10,
    #         "gap": 0.5,
    #         "font": "Calibri",
    #         "font_size": 8,
    #         "font_color": (0,0,0,255)
    #     },
    #     "Llegenda_no_valids": {
    #         "titol": "Hexàgons amb menys de 3 edificis",
    #         "font": "Calibri",
    #         "font_size": 12,
    #         "font_color": (0,0,0,255),
    #         "backg_color": (0,0,0,0)
    #     },
    #     "Escala": {
    #         "tipus": "Single Box",
    #         "font": "Calibri",
    #         "font_size": 10,
    #         "font_color": (0,0,0,255)
    #     },
    #     "Nord": {
    #         "image_path": "C:/projectes_git/Dades/nord2.png"
    #     },
    #     "Exportacio": {
    #         "output_path": f"{PATH_RESULTATS}/Analisi_bivariant_hexagons.pdf",
    #         "dpi": 300
    #     }
    # },
    "ACCESSIBILITAT":{
        "Mapa": {
            "color_fons": (60,60,60,255)
        },
        "Capçalera": {
            "text": "Accessibilitat als nuclis comercials de Barcelona",
            "font": "Calibri",
            "font_size": 20,
            "font_color": (255,255,255,255), #(0,0,0,255),
            "color": (100,100,100,180),
            "outline_color": (255, 255, 255, 200),
            "outline_width": 0.5
        },
        "Llegenda": {
            "titol": "Distància mínima",
            "font": "Calibri",
            "font_size": 10,
            "font_color": (255,255,255,255), #(0,0,0,255),
            "backg_color": (100,100,100,180)
        },
        "Escala": {
            "tipus": "Single Box",
            "font": "Calibri",
            "font_size": 10,
            "font_color": (255,255,255,255) #(0,0,0,255)
        },
        "Nord": {
            "image_path": "C:/projectes_git/Dades/nord2.png"
        },
        "Exportacio": {
            "output_path": f"{PATH_RESULTATS}/Accessibilitat.pdf",
            "dpi": 600
        }
    }
}
