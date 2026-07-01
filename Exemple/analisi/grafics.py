"""ANÀLISI ESPACIAL - GRÀFICS"""

import pandas as pd
import matplotlib.pyplot as plt

import config


def grafic_usos_districtes(df, output_path):
    """
    Funció per a generar un gràfic de barres a partir d'un DataFrame del nombre d'edificis per ús per districtes
    """

    # Creació de la figura
    fig, ax = plt.subplots(figsize=(10,6))

    # Generació del gràfic
    df.plot.bar(
        ax=ax,
        # Assignació de colors
        color=[config.colors_mpl(c) for c in df.columns]
    )

    # Addició d'elements
    ax.set_title("Usos dels edificis per districte")
    ax.set_xlabel("Usos")
    ax.set_ylabel("Nombre d'edificis")

    # Ajustos
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # Desat com a imatge
    plt.savefig(output_path, dpi=200)

    plt.close(fig)

    return fig


def grafic_percentatge_usos_districtes(df, output_path):
    """
    Funció per a generar un gràfic de barres apilades a partir d'un DataFrame de percentatges d'usos per districtes
    """

    # Creació de la figura
    fig, ax = plt.subplots(figsize=(10,6))

    # Generació del gràfic
    df.plot.bar(
        ax=ax,
        stacked='True',
        color=[config.colors_mpl(c) for c in df.columns]
    )

    # Addició d'elements
    ax.set_title("Usos dels edificis per districte")
    ax.set_xlabel("Usos")
    ax.set_ylabel("Percentatge d'edificis")

    # Ajustos
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # Desat com a imatge
    plt.savefig(output_path, dpi=200)

    plt.close(fig)

    return fig


def grafic_clusters_n(df, output_path):
    """
    Funció per a generar un gràfic de barres a partir d'un DataFrame de la informació dels clústers
    """

    # Creació de la figura
    fig, ax = plt.subplots(figsize=(10,6))

    # Generació del gràfic
    df.plot.barh(
        ax=ax,
        # Assignació de colors
        color=[config.colors_mpl(c) for c in df.index]
    )

    # Addició d'elements
    ax.set_title("Nombre d'agrupacions espacials per ús")
    ax.set_xlabel("Nombre d'agrupacions")
    ax.set_ylabel("Usos")

    # Ajustos
    ax.set_yticklabels([config.ETIQUETES_USOS[us] for us in df.index])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.3)
    plt.yticks(rotation=45, ha="right")
    plt.tight_layout()

    # Desat com a imatge
    plt.savefig(output_path, dpi=200)

    plt.close(fig)

    return fig


def grafic_clusters_mida(df, output_path):
    """
    Funció per a generar un gràfic de barres a partir d'un DataFrame de la informació dels clústers
    """

    # Creació de la figura
    fig, ax = plt.subplots(figsize=(10,6))

    # Generació del gràfic
    df.plot.barh(
        ax=ax,
        # Assignació de colors
        color=[config.colors_mpl(c) for c in df.index]
    )

    # Addició d'elements
    ax.set_title("Mida de les agrupacions espacials per ús")
    ax.set_xlabel("Nombre d'edificis de les agrupacions (mitjana)")
    ax.set_ylabel("Usos")

    # Ajustos
    ax.set_yticklabels([config.ETIQUETES_USOS[us] for us in df.index])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.3)
    plt.yticks(rotation=45, ha="right")
    plt.tight_layout()

    # Desat com a imatge
    plt.savefig(output_path, dpi=200)

    plt.close(fig)

    return fig