"""SIMBOLOGIA DE LES CAPES GENERADES"""

import config
import simbologia.simbologia_unica as simbologia_unica
import simbologia.simbologia_categorica as simbologia_categorica


def simbologia_base(dict_layers):
    """
    Funció d'alt nivell per a generar la simbologia de les capes de cartografia base
    i retorna un diccionari amb les capes simbolitzades
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
            layer = simbologia_categorica.simbologia_categorica(
                layer=layer,
                **config.SIMBOLOGIA["Edificis"]
            )

        else:
            layer = simbologia_unica.simbologia_unica(
                layer=layer,
                **config.SIMBOLOGIA[nom]
            )
        
        layer.setName(nom)

        layers_base[nom] = layer

    return layers_base


def simbologia_clusters(resultats):
    """
    Funció d'alt nivell per a generar la simbologia de les agrupacions espacials per cada ús
    i retorna un diccionari amb les capes simbolitzades
    """

    layers_clusters = {}

    for us, dades in resultats.items():
        layer = simbologia_unica.simbologia_unica(
            layer=dades["zones"],
            fill_color=config.COLORS_USOS[us],
            outline_width=config.SIMBOLOGIA["Clusters"]["outline_width"],
            stroke_color=config.COLORS_USOS[us]
        )

        layer.setName(f"Cluster {config.ETIQUETES_USOS[us]}")

        layers_clusters[us] = layer
    
    return layers_clusters