"""
Simbologia
==========

Funcions d'alt nivell per aplicar la simbologia a les capes generades
durant el projecte.
"""

import config
import simbologia.simbologies as simbologies
import simbologia.simbologia_agregacions as simbologia_agregacions
import simbologia.simbologia_especialitzacio as simbologia_especialitzacio
import simbologia.simbologia_hexagons as simbologia_hexagons
import simbologia.simbologia_accessibilitat as simbologia_accessibilitat 

# ==============================================================================
# CAPES BASE
# ==============================================================================

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

    cfg_base = config.SIMBOLOGIA["Base"]

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
                **cfg_base["Edificis"]
            )

            # Actualitzar el nom de les etiquetes de la llegenda
            renderer = layer_simb.renderer()

            for i, categoria in enumerate(renderer.categories()):
                valor = categoria.value()
                etiqueta = config.ETIQUETES_USOS.get(valor, valor)

                renderer.updateCategoryLabel(i, etiqueta)

            layer_simb.triggerRepaint()

        else:
            layer_simb = simbologies.simbologia_unica(
                layer=layer,
                **cfg_base[nom]
            )
        
        # Es recupera el nom original de la capa
        layer_simb.setName(nom)

        layers_base[nom] = layer_simb

    return layers_base


# ==============================================================================
# ATLES EDIFICIS INDUSTRIALS
# ==============================================================================

def simbologia_atles(edificis, districtes):
    """
    Aplica la simbologia als edificis d'ús industrial i la simbologia a
    la resta d'edificis.

    Paràmetres
    ----------
    edificis: QgsVectorLayer
        Capa vectorial dels edificis.
    
    Retorna
    -------
    dict
        Diccionari de capes simbolitzades.
    """

    layers_atles = {}

    layers_atles["Edificis"] = simbologia_especialitzacio.simbologia_edificis_industrials(
        edificis=edificis
    )

    layers_atles["Districtes"] = simbologia_especialitzacio.simbologia_districtes_atles(
        districtes=districtes
    )

    return layers_atles


# ==============================================================================
# AGREGACIÓ INDUSTRIAL COMPARADA
# ==============================================================================

def simbologia_comparacio_agregacions(capa_edificis, capa_superficie):
    """
    """
    layers_comparacio = {}

    layers_comparacio["Edificis"] = simbologia_agregacions.simbologia_hexagons_industrials(
        capa_analisi=capa_edificis,
        breaks=config.BREAKS_NOMBRE_EDIFICIS_INDUSTRIAL,
        element_analisi="Edificis"
    )

    layers_comparacio["Superficie"] = simbologia_agregacions.simbologia_hexagons_industrials(
        capa_analisi=capa_superficie,
        breaks=config.BREAKS_SUPERFICIE_INDUSTRIAL,
        element_analisi="Superficie"
    )

    return layers_comparacio


# ==============================================================================
# DENSITAT SUPERFÍCIE INDUSTRIAL
# ==============================================================================

def simbologia_densitat_agregacions(capa_districtes, capa_barris, capa_hexagons):
    """
    """
    layers_densitat = {}

    layers_densitat["Districtes"] = simbologia_agregacions.simbologia_densitat_industrial(
        capa_zones=capa_districtes,
        breaks=config.BREAKS_DENSITAT_SUPERFICIE_INDUSTRIAL,
        tipus_zona="Districtes"
    )

    layers_densitat["Barris"] = simbologia_agregacions.simbologia_densitat_industrial(
        capa_zones=capa_barris,
        breaks=config.BREAKS_DENSITAT_SUPERFICIE_INDUSTRIAL,
        tipus_zona="Barris"
    )

    layers_densitat["Hexagons"] = simbologia_agregacions.simbologia_densitat_industrial(
        capa_zones=capa_hexagons,
        breaks=config.BREAKS_DENSITAT_SUPERFICIE_INDUSTRIAL,
        tipus_zona="Hexagons"
    )

    return layers_densitat


# ==============================================================================
# AGRUPACIONS ESPACIALS i ACCESSIBILITAT
# ==============================================================================

def simbologia_accessibilitat_clusters(capa_clusters, capa_edificis, capa_terme, capa_graf):
    """
    Aplica la simbologia als centroides dels clústers espacials.

    Cada agrupació espacial es representa amb el color associat al seu ús.

    Paràmetres
    ----------
    resultats: dict
        Diccionari retornat per `analisi_clusters()`, amb l'estructura:
        {
            us: {
                "clusters": QgsVectorLayer,
                "zones": QgsVectorLayer,
                "resum": dict
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

    layers_accessibilitat = {}

    layers_accessibilitat["clusters"] = simbologia_accessibilitat.simbologia_clusters(
        clusters=capa_clusters
    )

    layers_accessibilitat["edificis"] = simbologia_accessibilitat.simbologia_edificis(
        edificis=capa_edificis
    )

    layers_accessibilitat["terme"] = simbologia_accessibilitat.simbologia_terme_municipal(
        terme=capa_terme
    )

    layers_accessibilitat["graf"] = simbologia_accessibilitat.simbologia_graf(
        graf=capa_graf
    ) 
    
    return layers_accessibilitat






# ==============================================================================
# ESPECIALITZACIÓ FUNCIONAL 
# ==============================================================================

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


def simbologia_hexagons_especialitzacio_funcional(hexagons, terme):
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

    layers_hexagons = {
        "hexagons": {
            "dominancia": simbologia_hexagons.simbologia_dominancia(hexagons),
            "shannon": simbologia_hexagons.simbologia_shannon(hexagons),
            "bivariant": simbologia_hexagons.simbologia_bivariant(hexagons),
        },
        "terme_municipal": simbologia_hexagons.simbologia_terme_municipal(terme) 
    }
    
    return layers_hexagons


# ==============================================================================
# ACCESSIBILITAT
# ==============================================================================

def simbologia_composicio_accessibilitat(edificis, graf, clusters, terme):
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
 
    layers_access["accessibilitat"] = simbologia_accessibilitat.simbologia_edificis(
        edificis=edificis
    )

    layers_access["graf"] = simbologia_accessibilitat.simbologia_graf(
        graf=graf
    )

    layers_access["clusters"] = simbologia_accessibilitat.simbologia_clusters(
        clusters=clusters
    )

    layers_access["terme"] = simbologia_accessibilitat.simbologia_terme_municipal(
        terme=terme
    )

    return layers_access 