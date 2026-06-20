"""COMPOSICIONS - LAYOUTS"""

# Fusió de les diferents composicions en un únic arxiu PDF

from pypdf import PdfWriter

def fusionar_pdf(pdfs, output_path):
    """
    Funció per a generar un únic arxiu PDF a partir de les diferents composicions en format PDF

    Paràmetres
        pdfs: llistat dels pdfs a unir
        output_path: ruta de sortida dels arxius units
    """

    merger = PdfWriter()

    for pdf in pdfs:
        merger.append(pdf)

    merger.write(output_path)

    merger.close()