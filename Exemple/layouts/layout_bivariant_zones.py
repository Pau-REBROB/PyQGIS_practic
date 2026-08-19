import layouts.layout_common as layout_common
import simbologia.simbologies as simbologies
import config

# ------------------------------------------------------------------
# MAPA
# ------------------------------------------------------------------

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
        nom="Districtes",
        fill_color=(0,0,0,0),
        outline_width=0.50,
        stroke_color=(80,80,80,255)
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
# COMPOSICIÓ
# ------------------------------------------------------------------

def composicio_bivariant_zones(zona, capes, capa_extent, districtes=None, amb_capçalera=True):
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
    zona: str
        Unitat administrativa a representar.
    capes: list[QgsMapLayer]
        Llista ordenada de capes que es mostraran a la composició.
    capa_extent: QgsVectorLayer
        Capa utilitzada per a calcular l'extensió inicial del mapa.
    districtes: QgsVectorLayer, optional
        Capa vectorial de districtes.
    amb_capçalera: bool
        Especifica si la composició tindrà capçalera o un títol simple.
        Per defecte, True. 

    Retorna
    -------
    None
        La composició s'exporta directament en local.
    """

    # ------------------------------------------------------------------
    # CONFIGURACIÓ
    # ------------------------------------------------------------------

    cfg_layout = config.LAYOUTS["BIVARIANT"][f"{zona}"]
    cfg_estructura = config.LAYOUTS["ESTRUCTURA_BIVARIANT"][f"{zona}"]

    # Normalitzar capes a llista
    if not isinstance(capes, list):
        capes = [capes]

    # Afegir Districtes al principi si existeixen
    if districtes:
        districtes_layout = crear_capa_districtes_layout(districtes)
        capes = [districtes_layout] + capes

    layout = layout_common.generar_layout(nom_layout="Anàlisi bivariant per UA")

    # ------------------------------------------------------------------
    # MAPA
    # ------------------------------------------------------------------
    
    mapa = layout_common.afegir_mapa(
        layout=layout,
        capes=capes,
        capa_extent=capa_extent,
        **cfg_estructura["Mapa"]
    )

    # ------------------------------------------------------------------
    # CAPÇALERA I TÍTOLS
    # ------------------------------------------------------------------

    if amb_capçalera:
        layout_common.afegir_capçalera(
            layout=layout,
            **cfg_layout["Capçalera"],
            **cfg_estructura["Capçalera"]
        )

    else:
        layout_common.afegir_text(
            layout=layout,
            **cfg_layout["Text_titol"],
            **cfg_estructura["Text_titol"]
        )
        
        layout_common.afegir_capçalera(
            layout=layout,
            **cfg_layout["Subtitol"],
            **cfg_estructura["Subtitol"]
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
        **cfg_layout["Eix_accessibilitat_llegenda"],
        **cfg_estructura["Eix_accessibilitat_llegenda"]
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

    layout_common.exportar_layout(
        layout=layout,
        **cfg_layout["Exportacio"]
    )
