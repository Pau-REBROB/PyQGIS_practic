"""
Simbologia
==========

Funcions d'alt nivell per aplicar la simbologia a les capes generades
durant el projecte.
"""

import config
import simbologia.simbologies as simbologies
import simbologia.simbologia_especialitzacio as simbologia_especialitzacio
import simbologia.simbologia_hexagons as simbologia_hexagons

def simbologia_base(dict_layers):
    """
    Aplica la simbologia a les capes de cartografia base.

    La funció aplica la simbologia corresponent a cadascuna
    de les capes principals del projecte:
        - Terme municipal
        - Districtes
        - Barris
        - Edificis

    Paràmetres
    ----------
    dict_layers: dict
        Diccionari de capes del projecte, amb l'estructura:
        {
            "Nom_grup": {
                "Nom_capa": QgsVectorLayer,
                ...
            },
            ...
        }

    Retorna
    -------
    dict
        Diccionari amb la mateixa estructura que el d'entrada
        amb les capes simbolitzades.
    """

    layers_base_input = {
        "TermeMunicipal": dict_layers["Limits_administratius"]["TermeMunicipal"],
        "Districtes": dict_layers["Limits_administratius"]["Districtes"],
        "Barris": dict_layers["Limits_administratius"]["Barris"],
        "Edificis": dict_layers["Cadastre"]["Edificis"]
    }

    layers_base = {}

    for nom, layer in layers_base_input.items():
        if nom == "Edificis":
            layer_simb = simbologies.simbologia_categorica(
                layer=layer,
                **config.SIMBOLOGIA["Edificis"]
            )

        else:
            layer_simb = simbologies.simbologia_unica(
                layer=layer,
                **config.SIMBOLOGIA[nom]
            )
        
        # Es recupera el nom original de la capa
        layer_simb.setName(nom)

        layers_base[nom] = layer_simb

    return layers_base


def simbologia_clusters(resultats):
    """
    Aplica la simbologia als clústers espacials.

    Cada agrupació espacial es representa amb el color associat al seu ús.

    Paràmetres
    ----------
    resultats: dict
        Diccionari retornat per `analisi_clusters()`, amb l'estructura:
        {
            us: {
                "clusters": QgsVectorLayer,
                "zones": QgsVectorLayer,
                "resum": dict,
                "taula": pandas.DataFrame
            },
            ...
        }
    
    Retorna
    -------
    dict
        Diccionari amb les capes simbolitzades, amb l'estructura:
        {
            us: QgsVectorLayer,
            ...
        }
    """

    layers_clusters = {}

    for us, dades in resultats.items():
        layer_simb = simbologies.simbologia_unica(
            layer=dades["zones"],
            fill_color=config.COLORS_USOS[us],
            outline_width=config.SIMBOLOGIA["Clusters"]["outline_width"],
            stroke_color=config.COLORS_USOS[us]
        )

        # Es recupera el nom original de la capa
        layer_simb.setName(f"Cluster {config.ETIQUETES_USOS[us]}")

        layers_clusters[us] = layer_simb
    
    return layers_clusters


def simbologia_especialitzacio_funcional(districtes):
    """
    Aplica les diferents simbologies d'especialització
    a la capa de districtes.

    Paràmetres
    ----------
    districtes: QgsVectorLayer
        Capa vectorial de districtes.
    
    Retorna
    -------
    dict
        Diccionari amb les capes simbolitzades, amb l'estructura:
        {
            "us_predominant": QgsVectorLayer,
            "dominancia": QgsVectorLayer,
            "index_shannon": QgsVectorLayer,
            "classe_bivariant: QgsVectorLayer
        }
    """

    layers_especialitzacio = {}

    districtes_us_pred = simbologia_especialitzacio.simbologia_us_predominant(
        districtes=districtes
    )

    layers_especialitzacio["us_predominant"] = districtes_us_pred

    districtes_domin = simbologia_especialitzacio.simbologia_dominancia(
        districtes=districtes
    )

    layers_especialitzacio["dominancia"] = districtes_domin

    districtes_shan = simbologia_especialitzacio.simbologia_shannon(
        districtes=districtes
    )
    
    layers_especialitzacio["index_shannon"] = districtes_shan

    districtes_bivariant = simbologia_especialitzacio.simbologia_bivariant(
        districtes=districtes
    )

    layers_especialitzacio["bivariant"] = districtes_bivariant
    
    return layers_especialitzacio


def simbologia_hexagons_especialitzacio_funcional(hexagons):
    """
    Aplica les diferents simbologies d'especialització
    a la malla hexagonal amb els atributs d'especialització funcional.

    Paràmetres
    ----------
    hexagons: QgsVectorLayer
        Capa vectorial de districtes.
    
    Retorna
    -------
    dict
        Diccionari amb les capes simbolitzades, amb l'estructura:
        {
            "us_predominant": QgsVectorLayer,
            "dominancia": QgsVectorLayer,
            "index_shannon": QgsVectorLayer,
            "classe_bivariant: QgsVectorLayer
        }
    """

    layers_hexagons = {}

    hexagons_us_pred = simbologia_hexagons.simbologia_us_predominant(
        hexagons=hexagons
    )

    layers_hexagons["us_predominant"] = hexagons_us_pred

    hexagons_domin = simbologia_hexagons.simbologia_dominancia(
        hexagons=hexagons
    )

    layers_hexagons["dominancia"] = hexagons_domin

    hexagons_shan = simbologia_hexagons.simbologia_shannon(
        hexagons=hexagons
    )
    
    layers_hexagons["index_shannon"] = hexagons_shan

    hexagons_bivariant = simbologia_hexagons.simbologia_bivariant(
        hexagons=hexagons
    )

    layers_hexagons["bivariant"] = hexagons_bivariant
    
    return layers_hexagons