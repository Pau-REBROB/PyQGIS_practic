from qgis.core import (
    QgsLayoutExporter,
    QgsLayoutItemMap,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsRectangle,
    QgsUnitTypes,
)

import os

import layouts.layout_common as layout_common
import simbologia.simbologies as simbologies
import config

# ------------------------------------------------------------------
# MAPA
# ------------------------------------------------------------------

def afegir_mapa(layout, capes, capa_extent, factor_escala, size, position, rotacio, offset_x, offset_y):
    """
    Afegeix l'element mapa principal a una composició.

    La funció crea un element `QgsLayoutItemMap`, hi assocïa les capes
    indicades, ajusta l'extensió inicial a partir de la capa de 
    referència i configura la seva posició, mida i rotació.

    L'ordre de les operacions:
        1. Definir la mida i posició del mapa,
        2. Ajustar l'extensió al conjunt de dades,
        3. Aplicar la rotació,
        4. Modificar l'escala,
        5. Aplicar un desplaçament manual del centre,
    evita modificacions inesperades de l'escala o l'extensió quan el
    mapa està rotat.

    Observacions
    ------------
    Els desplaçaments `offset_x` i `offset_y` s'apliquen després
    de la rotació mitjançant una funció auxiliar `transformar_offset()`
    per mantenir la direcció visual del desplaçament de manera
    independent a l'orientació del mapa.

    Paràmetres
    ----------
    layout: QgsPrintLayout
        Composició sobre la qual s'afegeix el mapa.
    capes: list[QgsMapLayer]
        Capes que es mostraran al mapa, en ordre de representació.
    capa_extent: QgsVectorLayer
        Capa utilitzada per a definir l'extensió inicial del mapa.
    factor_escala: float
        Factor escala per apropar o allunyar el mapa.
    size: tuple[int,int]
        Amplada i alçada de la imatge, en mil·límetres.
    position: tuple[int,int]
        Coordenada X i Y de la imatge - cantonada superior esquerra - en mil·límetres.
    rotacio: int
        ###
    offset_x: int
        ##
    offset_y: int
        ##

    Retorna
    -------
    QgsLayoutItemMap
        Element mapa.
    """

    # Configuració inicial del mapa
    layout_map = QgsLayoutItemMap(layout)
    
    layout.addLayoutItem(layout_map)

    layout_map.setLayers(capes)

    layout_map.setKeepLayerSet(True)

    # Ajust d'escala i rotació
    layout_map.attemptMove(QgsLayoutPoint(*position, QgsUnitTypes.LayoutMillimeters))
    layout_map.attemptResize(QgsLayoutSize(*size, QgsUnitTypes.LayoutMillimeters))

    layout_map.zoomToExtent(capa_extent.extent())
    layout_map.setMapRotation(rotacio)
    layout_map.setScale(layout_map.scale() * factor_escala)

    # Desplaçament manual del centre del mapa
    extent = layout_map.extent()
    dx, dy = layout_common.transformar_offset(
        offset_x=offset_x,
        offset_y=offset_y,
        rotacio=rotacio
    )
    extent = QgsRectangle(
        extent.xMinimum() + dx,
        extent.yMinimum() + dy,
        extent.xMaximum() + dx,
        extent.yMaximum() + dy
    )
    layout_map.setExtent(extent)
        
    return layout_map


def crear_capa_districtes_layout(districtes):
    """
    Crea una còpia de la capa de districtes específica pel layout.

    La funció clona la capa original per evitar modificar-ne la
    simbologia dins del projecte, i aplica una representació pròpia
    per a la composició cartogràfica.

    La capa resultant només s'utilitza durant la generació del layout.

    Paràmetres
    ----------
    districtes: QgsVectorLayer
        Capa vectorial dels districtes.
    
    Retorna
    -------
    QgsVectorLayer
        Capa vectorial dels districtes simbolitzada.
    """

    districtes_clone = districtes.clone()

    districtes_simbologia = simbologies.simbologia_unica(
        layer=districtes_clone,
        fill_color=(0,0,0,0),
        outline_width=0.45,
        stroke_color=(100,100,100,255)
    )
    # TODO
    # El color i el gruix del contorn haurien de convertir-se en constants globals d'estil. 

    return districtes_simbologia 


# ------------------------------------------------------------------
# LLEGENDA
# ------------------------------------------------------------------

def afegir_llegenda_bivariant(layout, cell, gap, position, colors):
    """
    Construeix la llegenda gràfica del mapa bivariant.

    La llegenda es genera a partir d'una matriu 3x3 de classes,
    on les files representen dominància funcional i les columnes
    representen diversitat funcional.

    Cada cel·la es dibuixa individualment mitjançant la funció
    `afegir_fons()`.

    Paràmetres
    ----------
    layout: QgsPrintLayout
        Composició que es vol exportar.
    cell: float
        Mida del costat de la cel·la, en mil·límetres.
    gap: float
        Separació entre cel·les, en mil·límetres.
    position: tuple[int,int]
        Coordenada X i Y de la llegenda - cantonada superior esquerra - en mil·límetres.
    colors: dict
        Diccionari de colors, en format RGBA, per a cada classe.

    Retorna
    -------
    ### 
    """

    matriu = [
        ["Baixa_Alta",   "Mitjana_Alta",   "Alta_Alta"],
        ["Baixa_Mitjana","Mitjana_Mitjana","Alta_Mitjana"],
        ["Baixa_Baixa",  "Mitjana_Baixa",  "Alta_Baixa"]
    ]

    x0, y0 = position

    for fila in range(3):
        for columna in range(3):

            classe = matriu[fila][columna]

            layout_common.afegir_fons(
                layout=layout,
                size=(cell,cell),
                position=(x0 + columna*(cell+gap), y0 + fila*(cell+gap)),
                color=colors[classe]
            )


def afegir_labels_superiors_llegenda(layout, position, cell, gap, **cfg):
    """
    Afegeix les etiquetes superiors de la llegenda bivariant.

    Observacions
    ------------
    Les etiquetes es distribueixen automàticament segons
    la mida de cada cel·la i la separació indicada.

    Paràmetres
    ----------
    layout: QgsPrintLayout
        Composició que es vol exportar.
    position: tuple[int,int]
        Coordenada X i Y de l'etiqueta superior esquerra, en mil·límetres.
    cell: float
        Mida del costat de la cel·la, en mil·límetres.
    gap: float
        Separació entre cel·les, en mil·límetres.
    **cfg: dict
        Diccionari de paràmetres de configuració.

    Retorna
    -------
    ###     
    """

    x0, y0 = position

    labels = ["Baixa", "Mitjana", "Alta"]

    for i, label in enumerate(labels):
        layout_common.afegir_text(
            layout=layout,
            text=label,
            position=(x0 + i*(cell + gap), y0),
            **cfg
        )


def afegir_labels_laterals_llegenda(layout, position, cell, gap, **cfg):
    """
    Afegeix les etiquetes laterals de la llegenda bivariant.

    Observacions
    ------------
    Les etiquetes es distribueixen automàticament segons
    la mida de cada cel·la i la separació indicada.

    Paràmetres
    ----------
    layout: QgsPrintLayout
        Composició que es vol exportar.
    position: tuple[int,int]
        Coordenada X i Y de l'etiqueta superior, en mil·límetres.
    cell: float
        Mida del costat de la cel·la, en mil·límetres.
    gap: float
        Separació entre cel·les, en mil·límetres.
    **cfg: dict
        Diccionari de paràmetres de configuració.

    Retorna
    -------
    ### 
    """

    x0, y0 = position

    labels = ["Baixa", "Mitjana", "Alta"]

    for i, label in enumerate(labels):
        layout_common.afegir_text(
            layout=layout,
            text=label,
            position=(x0, y0 + i*(cell + gap)),
            **cfg
        )


# ------------------------------------------------------------------
# EXPORTACIÓ
# ------------------------------------------------------------------

def exportar_layout(layout, output_path, dpi):
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
    None
    """
   
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


# ------------------------------------------------------------------
# COMPOSICIÓ
# ------------------------------------------------------------------

def composicio_bivariant_barris(districtes, capes, capa_extent):
    """
    Genera la composició cartogràfica d'anàlisi bivariant per
    barris del projecte.

    La funció coordina totes les operacions necessàries per crear el
    layout:
        - crea la composició,
        - prepara les capes auxiliars,
        - afegeix el mapa principal,
        - afegeix la capçalera,
        - construeix la llegenda bivariant,
        - incorpora els eixos i etiquetes interpretatius de la llegenda,
        - incorpora l'escala gràfica,
        - incorpora la fletxa del nord,
        - i exporta el resultat a PDF.
    
    Paràmetres
    ----------
    districtes: QgsVectorLayer
        Capa vectorial de districtes.
    capes: list[QgsMapLayer]
        Llista ordenada de capes que es mostraran a la composició.
    capa_extent: QgsVectorLayer
        Capa utilitzada per a calcular l'extensió inicial del mapa.

    Retorna
    -------
    None
        La composició s'exporta directament en local.
    """

    # ------------------------------------------------------------------
    # CONFIGURACIÓ
    # ------------------------------------------------------------------

    cfg_layout = config.LAYOUTS["BIVARIANT"]
    cfg_estructura = config.LAYOUTS["ESTRUCTURA_BIVARIANT"]

    districtes_layout = crear_capa_districtes_layout(districtes)

    layout = layout_common.generar_layout(nom_layout="Anàlisi bivariant per barris")

    # ------------------------------------------------------------------
    # MAPA
    # ------------------------------------------------------------------
    
    mapa = afegir_mapa(
        layout=layout,
        capes=[districtes_layout, capes],
        capa_extent=capa_extent,
        **cfg_estructura["Mapa"]
    )

    # ------------------------------------------------------------------
    # CAPÇALERA
    # ------------------------------------------------------------------

    layout_common.afegir_capçalera(
        layout=layout,
        **cfg_layout["Capçalera"],
        **cfg_estructura["Capçalera"]
    )

    # ------------------------------------------------------------------
    # LLEGENDA
    # ------------------------------------------------------------------

    afegir_llegenda_bivariant(
        layout=layout,
        **cfg_layout["Llegenda"],
        **cfg_estructura["Llegenda"]
    )

    layout_common.afegir_text(
        layout=layout,
        **cfg_layout["Eix_dominancia_llegenda"],
        **cfg_estructura["Eix_dominancia_llegenda"]
    )

    layout_common.afegir_text(
        layout=layout,
        **cfg_layout["Eix_diversitat_llegenda"],
        **cfg_estructura["Eix_diversitat_llegenda"]
    )

    afegir_labels_superiors_llegenda(
        layout=layout,
        **cfg_layout["Labels_superiors_llegenda"],
        **cfg_estructura["Labels_superiors_llegenda"]
    )

    afegir_labels_laterals_llegenda(
        layout=layout,
        **cfg_layout["Labels_laterals_llegenda"],
        **cfg_estructura["Labels_laterals_llegenda"]
    )

    # ------------------------------------------------------------------
    # ESCALA I NORD
    # ------------------------------------------------------------------

    layout_common.afegir_escala(
        layout=layout,
        mapa=mapa,
        **cfg_layout["Escala"],
        **cfg_estructura["Escala"]
    )

    layout_common.afegir_nord(
        layout=layout,
        mapa=mapa,
        **cfg_layout["Nord"],
        **cfg_estructura["Nord"]
    )

    # ------------------------------------------------------------------
    # EXPORTACIÓ
    # ------------------------------------------------------------------

    exportar_layout(
        layout=layout,
        **cfg_layout["Exportacio"]
    )
