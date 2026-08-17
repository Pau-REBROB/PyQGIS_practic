import config
import simbologia.simbologies as simbologies

cfg_simbologa = config.SIMBOLOGIA["Accessibilitat"] 

def simbologia_edificis(edificis):
    """
    Aplica una simbologia graduada a la capa d'edificis
    amb els valors d'accessibilitat.
    """

    layer = simbologies.simbologia_graduada_manual(
        layer=edificis,
        **cfg_simbologa["Edificis_accessibilitat"]
    )

    layer.setName("Distància mínima accessible")

    return layer


def simbologia_graf(graf):
    """
    Aplica una simbologia única a la capa del graf viari.
    """

    layer = simbologies.simbologia_unica_linia(
        layer=graf,
        **cfg_simbologa["Graf_accessibilitat"]
    )

    layer.setName("Graf viari")

    return layer


def simbologia_clusters(clusters):
    """
    Aplica una simbologia única a la capa d'agrupacions espacials.
    """

    layer = simbologies.simbologia_unica(
        layer=clusters,
        **cfg_simbologa["Clusters_accessibilitat"]
    )

    layer.setName("Agrupacions comercials")

    return layer


def simbologia_terme_municipal(terme):
    """
    Aplica una simbologia única a la capa del terme municipal.
    """

    layer = simbologies.simbologia_unica(
        layer=terme,
        **cfg_simbologa["Terme_accessibilitat"]
    )

    layer.setName("Terme municipal")

    return layer

