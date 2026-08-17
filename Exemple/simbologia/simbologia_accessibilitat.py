import config
import simbologia.simbologies as simbologies

def simbologia_edificis(edificis):
    """
    Aplica una simbologia graduada a la capa d'edificis
    amb els valors d'accessibilitat.
    """

    layer = simbologies.simbologia_graduada_manual(
        layer=edificis,
        **config.SIMBOLOGIA["Edificis_accessibilitat"]
    )

    layer.setName("Distància mínima accessible")

    return layer


def simbologia_graf(graf):
    """
    Aplica una simbologia única a la capa del graf viari.
    """

    layer = simbologies.simbologia_unica_linia(
        layer=graf,
        **config.SIMBOLOGIA["Graf_accessibilitat"]
    )

    layer.setName("Graf viari")

    return layer


def simbologia_clusters(clusters):
    """
    Aplica una simbologia única a la capa d'agrupacions espacials
    comercials.
    """

    layer = simbologies.simbologia_unica(
        layer=clusters,
        **config.SIMBOLOGIA["Clusters_accessibilitat"]
    )

    layer.setName("Agrupacions comercials")

    return layer


def simbologia_terme_municipal(terme):
    """
    Aplica una simbologia única a la capa del terme municipal.
    """

    layer = simbologies.simbologia_unica(
        layer=terme,
        **config.SIMBOLOGIA["Terme_accessibilitat"]
    )

    layer.setName("Terme municipal")

    return layer

