"""
Generació de gràfics
====================

Mòdul que agrupa les funcions de representació gràfica dels resultats
obtinguts durant les diferents anàlisis del projecte.

Organització
------------

- Gràfics dels usos dels edificis per districtes.
- Gràfics de les agrupacions espacials (clústers).

Les funcions s'organitzen en dos nivells:

    - funcions de generació d'un gràfic individual;
    - funcions d'alt nivell que generen tots els gràfics d'una anàlisi.
"""

import matplotlib.pyplot as plt

import config


def grafic_usos_districtes(df, output_path):
    """
    Genera un gràfic de barres del nombre d'edificis de cada ús per districtes.

    Paràmetres
    ----------
    df: pandas.DataFrame
        Taula amb el nombre d'edificis de cada ús per districte.
    output_path: str
        Ruta on es desarà la imatge.

    Retorna
    -------
    matplotlib.figure.Figure
        Figura generada.
    """

    fig, ax = plt.subplots(figsize=(10,6))

    df.plot.bar(
        ax=ax,
        # Assignació de colors
        color=[config.colors_mpl(c) for c in df.columns]
    )

    # Personalització de l'aspecte del gràfic
    ax.set_title("Usos dels edificis per districte")
    ax.set_xlabel("Usos")
    ax.set_ylabel("Nombre d'edificis")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig(output_path, dpi=300)

    plt.close(fig)

    return fig


def grafic_percentatge_usos_districtes(df, output_path):
    """
    Genera un gràfic de barres apilades amb el percentatge d'edificis 
    de cada ús per districtes.

    Paràmetres
    ----------
    df: pandas.DataFrame
        Taula amb el percentatge d'edificis de cada ús per districte.
    output_path: str
        Ruta on es desarà la imatge.

    Retorna
    -------
    matplotlib.figure.Figure
        Figura generada.
    """

    fig, ax = plt.subplots(figsize=(10,6))

    df.plot.bar(
        ax=ax,
        stacked=True,
        color=[config.colors_mpl(c) for c in df.columns]
    )

    # Personalització de l'aspecte del gràfic
    ax.set_title("Usos dels edificis per districte")
    ax.set_xlabel("Usos")
    ax.set_ylabel("Percentatge d'edificis")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig(output_path, dpi=300)

    plt.close(fig)

    return fig


def grafic_k_distance(distancies_k, k, output_path, eps_candidat=None):
    """
    Genera el gràfic de colze (k-distance plot) per ajudar a triar el
    paràmetre eps de DBSCAN.

    Representa les distàncies al k-èsim veí més proper, ordenades de
    petita a gran. El punt d'inflexió de la corba (colze) indica la
    transició entre distàncies típiques dins d'un clúster i distàncies
    típiques entre clústers o soroll.

    Paràmetres
    ----------
    distancies_k : list[float]
        Distàncies ordenades, sortida de distancia_k_vei().
    k : int
        Nombre de veïns considerat (per a l'etiqueta de l'eix i el títol).
    output_path : str
        Ruta on es desarà la imatge.
    eps_candidat : float, opcional
        Si s'indica, dibuixa una línia horitzontal de referència en
        aquest valor, per visualitzar un eps candidat sobre la corba.

    Retorna
    -------
    matplotlib.figure.Figure
        Figura generada.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(range(len(distancies_k)), distancies_k, linewidth=1.5)

    if eps_candidat is not None:
        ax.axhline(eps_candidat, color="gray", linestyle="--", linewidth=1)
        ax.text(0, eps_candidat, f" eps = {eps_candidat}", va="bottom", color="gray")

    # Personalització de l'aspecte del gràfic
    ax.set_title(f"K-distance plot (k={k})")
    ax.set_xlabel("Edificis ordenats per distància")
    ax.set_ylabel(f"Distància al {k}è veí (m)")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    plt.savefig(output_path, dpi=300)

    plt.close(fig)

    return fig


def grafic_area_accessibilitat(resultats_per_cluster, output_path, noms_clusters=None):
    """
    Genera un gràfic de línies comparant l'àrea acumulada coberta per
    les isoàrees de diversos clústers, a mesura que augmenta la
    distància/temps de referència.

    Permet comparar l'accessibilitat de diferents zones industrials de
    manera objectiva: com més ràpid creix la línia d'un clúster, més
    connectat està a la xarxa viària respecte als altres.

    Paràmetres
    ----------
    resultats_per_cluster: dict
        Diccionari { cluster_id: { llindar: area_m2 } }, sortida de
        area_coberta_per_llindar() per a cada clúster.
    output_path: str
        Ruta on es desarà la imatge.
    noms_clusters: dict, opcional
        Diccionari { cluster_id: nom } per mostrar noms descriptius
        (p. ex. "Sant Andreu") a la llegenda, en comptes de l'ID numèric.

    Retorna
    -------
    matplotlib.figure.Figure
        Figura generada.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    for cluster_id, resultats in resultats_per_cluster.items():
        llindars = sorted(resultats.keys())
        arees_km2 = [resultats[l] / 1_000_000 for l in llindars]  # m² -> km²

        etiqueta = noms_clusters.get(cluster_id, f"Clúster {cluster_id}") if noms_clusters else f"Clúster {cluster_id}"

        ax.plot(llindars, arees_km2, marker="o", linewidth=1.5, label=etiqueta)

    ax.set_title("Àrea coberta per accessibilitat, per clúster industrial")
    ax.set_xlabel("Distància (m)")
    ax.set_ylabel("Àrea coberta (km²)")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3)
    ax.legend()
    plt.tight_layout()

    plt.savefig(output_path, dpi=300)

    plt.close(fig)

    return fig



def generar_grafics_districtes(resultats):
    """
    Genera tots els gràfics associats a l'anàlisi dels usos per districtes.

    A partir dels resultats retornats per `analisi_districtes()`, genera:
        - el gràfic del nombre d'edificis per ús i districte,
        - el gràfic del percentatge d'edificis per ús i districte

    Paràmetres
    ----------
    resultats: dict
        Diccionari de les dades d'anàlisi d'usos per districtes.
        {
            "dades": dict,
            "taula": pandas.DataFrame,
            "percentatges": pandas.DataFrame
        }
    
    Retorna
    -------
    None
    """

    grafic_usos_districtes(
        df=resultats["taula"],
        output_path=config.EXPORTACIO_GRAFICS["Grafic_usos_districtes"]
    )

    grafic_percentatge_usos_districtes(
        df=resultats["percentatges"],
        output_path=config.EXPORTACIO_GRAFICS["Grafic_usos_percentatges_districtes"]
    )


def grafic_nombre_clusters(df, output_path):
    """
    Generar un gràfic de barres horitzontals amb el nombre de clústers
    identificats per a cada ús.

    Paràmetres
    ----------
    df: pandas.Series
        Sèrie amb el nombre de clústers per ús.
        L'índex de la sèrie correspon a l'identificador de l'ús.
    output_path: str
        Ruta on es desarà la imatge.
    
    Retorna
    -------
    matplotlib.figure.Figure
        Figura generada.
    """

    fig, ax = plt.subplots(figsize=(10,6))

    df.plot.barh(
        ax=ax,
        # Assignació de colors
        color=[config.colors_mpl(c) for c in df.index]
    )

    # Personalització de l'aspecte del gràfic
    ax.set_title("Nombre d'agrupacions espacials d'edificis per ús")
    ax.set_xlabel("Nombre d'agrupacions")
    ax.set_ylabel("Usos")

    ax.set_yticklabels([config.ETIQUETES_USOS[us] for us in df.index])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.3)
    plt.yticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig(output_path, dpi=300)

    plt.close(fig)

    return fig


def grafic_mida_clusters(df, output_path):
    """
    Generar un gràfic de barres horitzontals amb la mida mitja dels clústers
    identificats per a cada ús.

    Paràmetres
    ----------
    df: pandas.Series
        Sèrie amb la mida mitjana dels clústers per ús.
        L'índex de la sèrie correspon a l'identificador de l'ús. 
    output_path: str
        Ruta on es desarà la imatge.

    Retorna
    -------
    matplotlib.figure.Figure
        Figura generada.
    """

    fig, ax = plt.subplots(figsize=(10,6))

    df.plot.barh(
        ax=ax,
        # Assignació de colors
        color=[config.colors_mpl(c) for c in df.index]
    )

    # Personalització de l'aspecte del gràfic
    ax.set_title("Mida de les agrupacions espacials d'edificis per ús")
    ax.set_xlabel("Nombre mitjà d'edificis per agrupació")
    ax.set_ylabel("Usos")

    ax.set_yticklabels([config.ETIQUETES_USOS[us] for us in df.index])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.3)
    plt.yticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig(output_path, dpi=300)

    plt.close(fig)

    return fig


def generar_grafics_clusters(df):
    """
    Genera tots els gràfics associats a l'anàlisi de clústers.

    A partir de la taula resum dels clústers, genera:
        - el gràfic del nombre de clústers per ús,
        - el gràfic de la mida mitjana dels clústers per ús.

    Paràmetres
    ----------
    df: pandas.DataFrame
        Taula resum dels clústers, amb l'estructura:
            Índex
                Identificador dels usos.
            Columnes
            - n_clusters
            - n_edificis_totals
            - max_edificis_cluster
            - min_edificis_cluster
            - mitjana_edificis_cluster

    Retorna
    -------
    None
    """

    grafic_nombre_clusters(
        df=df["n_clusters"],
        output_path=config.EXPORTACIO_GRAFICS["Grafic_nombre_clusters"]
    )

    grafic_mida_clusters(
        df=df["mitjana_edificis_cluster"],
        output_path=config.EXPORTACIO_GRAFICS["Grafic_mida_clusters"]
    )
