"""
Fusió de composicions
=====================

Generació d'un únic document PDF a partir de les diferents
composicions cartogràfiques exportades.

Organització
------------
- fusionar_pdf()
"""

from pypdf import PdfWriter
from pathlib import Path

def fusionar_pdf(pdfs, output_path):
    """
    Fusiona diversos documents PDF en un únic arxiu.

    Paràmetres
    ----------
    pdfs: list[str]
        Llista ordenada de rutes dels documents PDF que es volen unir.
    output_path: str
        Ruta del document PDF de sortida.

    Retorna
    -------
    None
    """

    merger = PdfWriter()

    # Afegir els documents pdf per ordre
    for pdf in pdfs:
        merger.append(pdf)

    # Escriure el document final
    merger.write(output_path)

    merger.close()

    if not Path(output_path).exists():
        raise RuntimeError(f"No s'ha pogut generar el document '{output_path}")
