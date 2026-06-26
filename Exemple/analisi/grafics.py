"""ANÀLISI ESPACIAL - GRÀFICS"""

import pandas as pd
import matplotlib.pyplot as plt


def grafic_usos_districtes(df, output_path):
    """
    Funció per a generar un gràfic de barres a partir d'un DataFrame del nombre d'edificis per ús per districtes
    """

    # Creació de la figura
    fig, ax = plt.subplots(figsize=(10,6))

    # Generació del gràfic
    df.plot.bar(ax=ax)

    # Addició d'elements
    ax.set_title("Usos dels edificis per districte")
    ax.set_xlabel("Usos")
    ax.set_ylabel("Nombre d'edificis")

    # Ajustos
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
    df.plot(ax=ax, kind='bar', stacked='True')

    # Addició d'elements
    ax.set_title("Usos dels edificis per districte")
    ax.set_xlabel("Usos")
    ax.set_ylabel("Percentatge d'edificis")

    # Ajustos
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # Desat com a imatge
    plt.savefig(output_path, dpi=200)

    plt.close(fig)

    return fig