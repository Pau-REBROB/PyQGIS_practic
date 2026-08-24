"""
Composició tipus atles
======================

Funcions per generar una composició en format atles.

Cada entitat de la capa de cobertura genera una pàgina
independent de l'atles.

La composició inclou:

- mapa principal
- mapa localitzador
- títol
- llegenda
- escala gràfica
- fletxa del nord
- configuració de l'atles
- exportació a PDF

Organització
------------

- afegir_mapa()
- afegir_mapa_localitzador()
- generar_atles()
- exportar_atles()
- composicio_atles()
"""

from qgis.core import (
    QgsLayoutItemMap,
    QgsLayoutSize,
    QgsLayoutPoint,
    QgsUnitTypes,
    QgsLayoutMeasurement,
    QgsLayoutItemPage,
    QgsLayoutExporter
)

import os
from pathlib import Path

import config
import layouts.layout_common as layout_common
import layouts.fusionar_layouts as fusionar_layouts

def afegir_mapa_localitzador(layout, capa_localitzador, capa_extensio, mapa, size, position):
    """
    Afegeix un mapa localitzador a la composició de l'atles.

    El mapa localitzador mostra una vista general del municipi i 
    ressalta, mitjançant un "overview", l'extensió que representa 
    el mapa principal de cada pàgina de l'atles.

    Paràmetres
    ----------
    layout: QgsPrintLayout
        Composició sobre la qual s'afegeix el mapa localitzador.
    capa_localitzador: QgsVectorLayer
        Capa utilitzada per a representar el mapa localitzador.
    capa_extensio: QgsVectorLayer
        Capa utilitzada per a definir l'extensió fixa del mapa localitzador.
    mapa: QgsLayoutItemMap
        Mapa principal de la composició, que servirà de referència per a
        generar l'overview.
    size: tuple[int,int]
        Amplada i alçada de la imatge, en mil·límetres.
    position: tuple[int,int]
        Coordenada X i Y de la imatge - cantonada superior esquerra - en mil·límetres.

    Retorna
    -------
    QgsLayoutItemMap
        Element de mapa corresponent al localitzador.
    """

    # Crear del mapa
    locator = QgsLayoutItemMap(layout)
    layout.addLayoutItem(locator)

    # Afegir la capa que farà de localitzador
    locator.setLayers([capa_localitzador])
    locator.setKeepLayerSet(True)

    locator.attemptResize(QgsLayoutSize(*size, QgsUnitTypes.LayoutMillimeters))
    locator.attemptMove(QgsLayoutPoint(*position, QgsUnitTypes.LayoutMillimeters))

    # Extensió fixa del mapa localitzador
    locator.zoomToExtent(capa_extensio.extent())

    # L'overview representa sobre el mapa localitzador
    # l'extensió visible del mapa principal
    overview = locator.overview()
    overview.setLinkedMap(mapa)
    overview.setEnabled(True)
    
    # Afegir un marc per diferenciar visualment el mapa localitzador
    locator.setFrameEnabled(True)
    locator.setFrameStrokeWidth(QgsLayoutMeasurement(0.5, QgsUnitTypes.LayoutMillimeters))


    return locator


def generar_atles(layout, capa_cobertura, camp, mapa):
    """
    Configura l'atles d'una composició.

    La funció activa el mode Atles del layout, defineix la capa de
    cobertura i el camp que identifica cada pàgina, i configura
    el mapa principal perquè s'ajusti automàticament a cada entitat
    de la capa de cobertura.

    Paràmetres
    ----------
    layout: QgsPrintLayout
        Composició sobre la qual es configura l'atles.
    capa_cobertura: QgsVectorLayer
        Capa utilitzada per a generar les diferents pàgines de
        l'atles.
    camp: str
        Camp utilitzat tant per al nom de les pàgines com per al
        nom dels fitxers exportats.
    mapa: QgsLayoutItemMap
        Element mapa que es controlarà automàticament
        durant la generació de l'atles.

    Retorna
    -------
    QgsLayoutAtlas
        Objecte atles preparat i configurat per a exportar.
    """

    # Obtenir el gestor de l'atlas de la composició
    atlas = layout.atlas()
    atlas.setEnabled(True)

    # Definir la capa de cobertura
    # Cada entitat d'aquesta capa generarà una pàgina de l'atles
    atlas.setCoverageLayer(capa_cobertura)

    # El valor del camp s'utilitzarà com a nom de la pàgina i com
    # a nom de fitxer exportat
    atlas.setPageNameExpression(camp) 
    atlas.setFilenameExpression(camp) 

    # El mapa principal passa a ser controlat per l'atles
    mapa.setAtlasDriven(True)

    # Cada pàgina ajustarà automàticament el nivell de zoom a la 
    # geometria de l'entitat corresponent
    mapa.setAtlasScalingMode(QgsLayoutItemMap.Auto)
    
    # S'estableix un marge del 5% al voltant de cada entitat
    mapa.setAtlasMargin(0.05)

    # Actualitzar la llista d'entitats que formaran l'Atlas
    atlas.updateFeatures()

    return atlas


def exportar_atles(atlas, output_path, dpi):
    """
    Exporta un atles a un únic document PDF.

    Paràmetres
    ----------
    atlas: QgsLayoutAtlas
        Atles prèviament configurat.
    output_path: str
        Ruta del fitxer PDF de sortida.
    dpi: int
        Resolució d'exportació.
    
    Retorna
    -------
    None
    """

    # Configuració dels paràmetres d'exportació    
    pdf_settings = QgsLayoutExporter.PdfExportSettings()
    pdf_settings.dpi = dpi
    pdf_settings.forceVectorOutput = True
    pdf_settings.rasterizeWholeImage = False
    
    result, missatge_error = QgsLayoutExporter.exportToPdf(
        atlas,
        output_path,
        pdf_settings)
    
    if result != QgsLayoutExporter.Success:
        raise RuntimeError(f"No s'ha pogut exportar l'atles.\n{missatge_error}")


def exportar_com_a_atles(layout, output_folder, nom, dpi):
    """
    Exporta una composició QGIS en format PDF.
    
    Si ja existeix un fitxer amb el mateix nom, s'elimina abans
    de generar la nova exportació.

    Paràmetres
    ----------
    layout: QgsPrintLayout
        Composició que es vol exportar.
    output_path: str
        Ruta completa de l'arxiu PDF de sortida.
    dpi: int
        Resolució de l'exportació.

    Retorna
    -------
    RuntimeError
        Si no s'ha pogut exportar el layout.
    """

    output_path = str(Path(output_folder) / f"{nom}.pdf")

    # Si ja existeix una composició amb el mateix nom, s'elimina
    if os.path.exists(output_path):
        os.remove(output_path) 

    exporter = QgsLayoutExporter(layout)
    
    # Configurar els paràmetres d'exportació
    pdf_settings = QgsLayoutExporter.PdfExportSettings()
    pdf_settings.dpi = dpi
    pdf_settings.forceVectorOutput = True
    pdf_settings.rasterizeWholeImage = False
    
    resultat = exporter.exportToPdf(output_path, pdf_settings)

    if resultat != QgsLayoutExporter.Success:
        raise RuntimeError(f"No s'ha pogut exportar el layout a '{output_path}'")


    return output_path


def exportar_atles_orientacio_automatica(layout, atlas, output_folder, dpi):
    """
    Exporta cada pàgina de l'atles com un PDF independent
    amb orientació adaptada a la forma del districte.

    Paràmetres
    ----------
    layout: QgsPrintLayout
        ###
    atlas: QgsLayoutAtlas
        Atles prèviament configurat.
    output_path: str
        Ruta del fitxer PDF de sortida.
    dpi: int
        Resolució d'exportació.
    
    Retorna
    -------
    None
    """

    pdfs_generats = []

    atlas.beginRender()

    features = list(atlas.coverageLayer().getFeatures())

    while atlas.next():
        feature = features[atlas.currentFeatureNumber()]
        nom = feature["NOM"]

        orientacio = config.ORIENTACIO_DISTRICTES[nom]

        adaptar_layout_orientacio(
            layout=layout,
            orientacio=orientacio
        )

        # Exportar
        output_path = str(Path(output_folder) / f"{nom}.pdf")
        exporter = QgsLayoutExporter(layout)

        pdf_settings = QgsLayoutExporter.PdfExportSettings()
        pdf_settings.dpi = dpi
        exporter.exportToPdf(output_path, pdf_settings)

        pdfs_generats.append(output_path)
        print(f"Exportat: {nom}")

    atlas.endRender()

    # Fusionar tots els PDFs en un únic document
    fusionar_layouts.fusionar_pdf(
        pdfs=pdfs_generats,
        output_path=str(Path(output_folder) / "atles_districtes.pdf")
    )

    return pdfs_generats


def adaptar_layout_orientacio(layout, orientacio):
    """
    Adapta la composició de l'atles segons l'orientació de la pàgina.

    Els elements del layout ja han d'existir i estar identificats
    mitjançant el seu ID.
    """

    page = layout.pageCollection().page(0)

    cfg = config.LAYOUTS["ESTRUCTURA_ATLES"][orientacio]

    if orientacio == "Landscape":
        page.setPageSize("A4", QgsLayoutItemPage.Landscape)
    else:
        page.setPageSize("A4", QgsLayoutItemPage.Portrait)

    # ------------------------------------------------------------------
    # Elements
    # ------------------------------------------------------------------
    
    mapa = layout.itemById("mapa")
    llegenda = layout.itemById("llegenda")
    capçalera = layout.itemById("capçalera")
    escala = layout.itemById("escala")
    nord = layout.itemById("nord")
    localitzador = layout.itemById("localitzador")

    # ------------------------------------------------------------------
    # Mapa
    # ------------------------------------------------------------------

    mapa.attemptMove(
        QgsLayoutPoint(*cfg["Mapa"]["position"],
                       QgsUnitTypes.LayoutMillimeters
                       )
    )

    mapa.attemptResize(
        QgsLayoutPoint(*cfg["Mapa"]["size"],
                        QgsUnitTypes.LayoutMillimeters
                        )
    )

    # ------------------------------------------------------------------
    # Capçalera
    # ------------------------------------------------------------------

    capçalera.attemptMove(
        QgsLayoutPoint(*cfg["Capçalera"]["position"],
                        QgsUnitTypes.LayoutMillimeters
                        )
    )

    capçalera.attemptResize(
        QgsLayoutPoint(*cfg["Capçalera"]["size"],
                        QgsUnitTypes.LayoutMillimeters
                        )
    )

    # ------------------------------------------------------------------
    # Llegenda
    # ------------------------------------------------------------------

    llegenda.attemptMove(
        QgsLayoutPoint(*cfg["Llegenda"]["position"],
                        QgsUnitTypes.LayoutMillimeters
                        )
    )

    # ------------------------------------------------------------------
    # Escala
    # ------------------------------------------------------------------

    escala.attemptMove(
        QgsLayoutPoint(*cfg["Escala"]["position"],
                        QgsUnitTypes.LayoutMillimeters
                        )
    )

    # ------------------------------------------------------------------
    # Nord
    # ------------------------------------------------------------------

    nord.attemptMove(
        QgsLayoutPoint(*cfg["Nord"]["position"],
                        QgsUnitTypes.LayoutMillimeters
                        )
    )

    nord.attemptResize(
        QgsLayoutPoint(*cfg["Nord"]["size"],
                        QgsUnitTypes.LayoutMillimeters
                        )
    )

    # ------------------------------------------------------------------
    # Localitzador
    # ------------------------------------------------------------------

    localitzador.attemptMove(
        QgsLayoutPoint(*cfg["Localitzador"]["position"],
                        QgsUnitTypes.LayoutMillimeters
                        )
    )

    localitzador.attemptResize(
        QgsLayoutPoint(*cfg["Localitzador"]["size"],
                        QgsUnitTypes.LayoutMillimeters
                        )
    )


    

def composicio_atles(districtes, capes, capa_extent, capa_cobertura):
    """
    Genera la composició tipus atles del projecte.

    La funció crea una composició en format atles, incorpora
    els diferents elements cartogràfics, configura l'atles i 
    l'exporta a un document PDF.

    Paràmetres
    ----------
    districtes: QgsVectorLayer
        Capa de districtes que generarà l'atles.
    capes: list[QgsMapLayer]
        Capes que es mostraran al mapa principal.
    capa_extent: QgsVectorLayer
        Capa utilitzada per a definir l'extensió general del mapa
        principal i l'extensió fixa del mapa localitzador.
    capa_cobertura: QgsVectorLayer
        Capa de cobertura de l'atles.
        Cada entitat genera una pàgina independent.

    Retorna
    -------
    None
    """

    pdfs_generats = []

    cfg_layout = config.LAYOUTS["ATLES"]

    for districte in districtes.getFeatures():

        nom = districte["NOM"]

        orientacio = config.ORIENTACIO_DISTRICTES[nom]

        cfg_estructura = config.LAYOUTS["ESTRUCTURA_ATLES"][orientacio]

        layout = layout_common.generar_layout(
            nom_layout="Ús dels edificis a Barcelona per districte",
            orientacio=orientacio
        )

        mapa = layout_common.afegir_mapa(
            layout=layout,
            capes=capes,
            capa_extent=districte.geometry().boundingBox(),
            **cfg_estructura["Mapa"]
        )

        afegir_mapa_localitzador(
            layout=layout,
            capa_localitzador=capa_cobertura,
            capa_extensio=capa_extent,
            mapa=mapa,
            **cfg_estructura["Localitzador"]
        )

        layout_common.afegir_capçalera(
            layout=layout,
            **cfg_layout["Capçalera"],
            **cfg_estructura["Capçalera"]
        )

        # layout_common.afegir_llegenda(
        #     layout=layout,
        #     mapa=mapa,
        #     capes=capes,
        #     **cfg_layout["Llegenda"],
        #     **cfg_estructura["Llegenda"]
        # )
        
        # layout_common.afegir_escala(
        #     layout=layout,
        #     mapa=mapa,
        #     **cfg_layout["Escala"],
        #     **cfg_estructura["Escala"]
        # )

        # layout_common.afegir_nord(
        #     layout=layout,
        #     mapa=mapa,
        #     **cfg_layout["Nord"],
        #     **cfg_estructura["Nord"]
        # )

        pdf = exportar_com_a_atles(
            layout=layout,
            nom=nom,
            **cfg_layout["Exportacio_individual"]
        )

        pdfs_generats.append(pdf)

        # atles = generar_atles(
        #     layout=layout,
        #     capa_cobertura=capa_cobertura,
        #     mapa=mapa,
        #     **cfg_layout["Generacio"]
        # )

    # exportar_atles(
    #     atlas=atles,
    #     **cfg_layout["Exportacio"]
    # )

    # exportar_atles_orientacio_automatica(
    #     layout=layout,
    #     atlas=atles,
    #     **cfg_layout["Exportacio"]
    # )

    fusionar_layouts.fusionar_pdf(
        pdfs=pdfs_generats,
        **cfg_layout["Exportacio_atles"]
    )
