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
import simbologia.simbologia_accessibilitat as simbologia_accessibilitat 

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
        Diccionari amb les capes simbolitzades.
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
            nom="clusters",
            fill_color=config.COLORS_CLUSTERS[us],
            outline_width=config.SIMBOLOGIA["Clusters"]["outline_width"],
            stroke_color=config.COLORS_USOS[us]
        )

        # Es recupera el nom original de la capa
        layer_simb.setName(f"Cluster {config.ETIQUETES_USOS[us]}")

        layers_clusters[us] = layer_simb
    
    return layers_clusters


def simbologia_especialitzacio_funcional(zones, ua):
    """
    Aplica les diferents simbologies d'especialització
    a la capa de districtes.

    Paràmetres
    ----------
    zones: QgsVectorLayer
        Capa vectorial de les unitats administratives.
    ua: str
        Nom de la unitat administrativa.
    
    Retorna
    -------
    dict
        Diccionari amb les capes simbolitzades, amb l'estructura:
        {
            "us_predominant": QgsVectorLayer,
            "dominancia": QgsVectorLayer,
            "index_shannon": QgsVectorLayer,
            "bivariant: QgsVectorLayer
        }
    """

    layers_especialitzacio = {}

    zona_us_pred = simbologia_especialitzacio.simbologia_us_predominant(
        zones=zones,
        ua=ua
    )
    layers_especialitzacio["us_predominant"] = zona_us_pred

    zona_domin = simbologia_especialitzacio.simbologia_dominancia(
        zones=zones,
        ua=ua
    )
    layers_especialitzacio["dominancia"] = zona_domin

    zona_shan = simbologia_especialitzacio.simbologia_shannon(
        zones=zones,
        ua=ua
    )

    layers_especialitzacio["index_shannon"] = zona_shan

    zona_bivariant = simbologia_especialitzacio.simbologia_bivariant(
        zones=zones,
        ua=ua
    )
    layers_especialitzacio["bivariant"] = zona_bivariant
    
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
            "bivariant: QgsVectorLayer
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


def simbologia_edificis_accessibilitat(edificis, graf, clusters, terme):
    """
    Aplica les diferents simbologies d'accessibilitat a la
    capa d'edificis i del graf viari.

    Paràmetres
    ----------
    edificis: QgsVectorLayer
        Capa vectorial dels edificis amb el camp d'accessibilitat.
    graf: QgsVectorLayer
        Capa vectorial del graf viari.
    clusters: QgsVectorLayer
        Capa vectorial de les zones dels clústers comercials.
    terme: QgsVectorLayer
        Capa vectorial del terme municipal.

    Retorna
    -------
    dict
        Diccionari amb les capes simbolitzades, amb l'estructura:
        {
            "accessibilitat": QgsVectorLayer,
            "graf": QgsVectorLayer,
            "clusters": QgsVectorLayer,
            "terme": QgsVectorLayer
        }
    """

    layers_access = {}

    accessibilitat = simbologia_accessibilitat.simbologia_edificis(
        edificis=edificis
    )

    layers_access["accessibilitat"] = accessibilitat

    graf_viari = simbologia_accessibilitat.simbologia_graf(
        graf=graf
    )

    layers_access["graf"] = graf_viari

    clusters_access = simbologia_accessibilitat.simbologia_clusters(
        clusters=clusters
    )

    layers_access["clusters"] = clusters_access

    terme_access = simbologia_accessibilitat.simbologia_terme_municipal(
        terme=terme
    )

    layers_access["terme"] = terme_access

    return layers_access 