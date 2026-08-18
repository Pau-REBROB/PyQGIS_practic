"""
Simbologia
==========

Funcions per generar diferents tipus de simbologia per a capes vectorials.

Organització
------------

- Símbol únic
- Simbologia categòrica
- Simbologia graduada
- Funcions d'alt nivell
"""

from qgis.core import ( 
    QgsCategorizedSymbolRenderer,
    QgsFeatureRequest,
    QgsFillSymbol,
    QgsGraduatedSymbolRenderer,
    QgsLineSymbol,
    QgsMarkerSymbol,
    QgsRendererCategory,
    QgsRendererRange,
    QgsSimpleLineSymbolLayer,
    QgsSingleSymbolRenderer,
    QgsStyle
)

from qgis.PyQt.QtGui import QColor

# =============================================================================
# SÍMBOL ÚNIC
# =============================================================================

def simbologia_unica(layer, nom, fill_color, outline_width, stroke_color):
    """
    Aplica una simbologia de símbol únic a una capa poligonal.

    La funció clona la capa d'entrada, crea un símbol de farcit amb els
    paràmetres especificats i l'assigna a la capa clonada.
    
    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa poligonal sobre la que aplicar la simbologia.
    nom: str
        Nom de la capa.
    fill_color: tuple[int,int,int,int]
        Color del farcit, en format RGBA.
    outline_width: float
        Gruix del contorn.
    stroke_color: tuple[int,int,int,int]
        Color del contorn, en format RGBA.

    Retorna
    -------
    QgsVectorLayer
        Nova capa en memòria amb la simbologia aplicada.
    """

    layer_clone = layer.materialize(QgsFeatureRequest())
    
    layer_clone.setName(nom)
       
    symbol = QgsFillSymbol()
    
    symbol.setColor(QColor(*fill_color))
    symbol_layer_0 = symbol.symbolLayer(0)
    symbol_layer_0.setStrokeWidth(outline_width)
    symbol_layer_0.setStrokeColor(QColor(*stroke_color))

    renderer = QgsSingleSymbolRenderer(symbol)
    layer_clone.setRenderer(renderer)
        
    return layer_clone


def simbologia_unica_linia(layer, nom, fill_color, width, outline_color, outline_width):
    """
    Aplica una simbologia de símbol únic a una capa lineal.

    La funció clona la capa d'entrada, crea un símbol de farcit amb els
    paràmetres especificats i l'assigna a la capa clonada.
    
    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa lineal sobre la que aplicar la simbologia.
    nom: str
        Nom de la capa.
    fill_color: tuple[int,int,int,int]
        Color de la línia base, en format RGBA.
    outline_width: float
        Gruix del contorn.
    outline_color: tuple[int,int,int,int]
        Color del contorn, en format RGBA.

    Retorna
    -------
    QgsVectorLayer
        Nova capa en memòria amb la simbologia aplicada.
    """

    layer_clone = layer.materialize(QgsFeatureRequest())
    
    layer_clone.setName(nom)
    
    symbol = QgsLineSymbol()
    
    linia_base = QgsSimpleLineSymbolLayer()
    linia_base.setColor(QColor(*fill_color))
    linia_base.setWidth(width)
    
    linia_ext = QgsSimpleLineSymbolLayer()
    linia_ext.setColor(QColor(*outline_color))
    linia_ext.setWidth(outline_width)

    symbol.changeSymbolLayer(0, linia_ext)
    symbol.appendSymbolLayer(linia_base)

    renderer = QgsSingleSymbolRenderer(symbol)
    layer_clone.setRenderer(renderer)

    return layer_clone


def simbologia_unica_punt(layer, nom, mida, fill_color, outline_width, stroke_color):
    """
    Aplica una simbologia de símbol únic a una capa puntual.

    La funció clona la capa d'entrada, crea un símbol de farcit amb els
    paràmetres especificats i l'assigna a la capa clonada.
    
    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa poligonal sobre la que aplicar la simbologia.
    nom: str
        Nom de la capa.
    fill_color: tuple[int,int,int,int]
        Color del farcit, en format RGBA.
    mida: float
        Mida del marcador.
    outline_width: float
        Gruix del contorn.
    stroke_color: tuple[int,int,int,int]
        Color del contorn, en format RGBA.

    Retorna
    -------
    QgsVectorLayer
        Nova capa en memòria amb la simbologia aplicada.
    """

    layer_clone = layer.materialize(QgsFeatureRequest())
    
    layer_clone.setName(nom)
       
    symbol = QgsMarkerSymbol()
    symbol_layer_0 = symbol.symbolLayer(0)
    
    symbol_layer_0.setColor(QColor(*fill_color))
    symbol_layer_0.setSize(mida)
    symbol_layer_0.setStrokeWidth(outline_width)
    symbol_layer_0.setStrokeColor(QColor(*stroke_color))

    renderer = QgsSingleSymbolRenderer(symbol)
    layer_clone.setRenderer(renderer)
        
    return layer_clone


# =============================================================================
# SIMBOLOGIA CATEGÒRICA
# ==============================================================================

def simbologia_categorica(layer, atribut, colors_categories, outline_width, stroke_color):
    """
    Aplica simbologia categòrica a una capa vectorial.

    La funció clona la capa d'entrada i hi aplica un 
    renderer categòric a partir d'un atribut i un diccionari
    de colors.
    
    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa vectorial sobre la qual s'aplica la simbologia.
    atribut: str
        Camp utilitzat per classificar les categories.
    colors: dict
        Diccionari de colors, amb l'estructura
        {
            categoria: (R,G,B,A),
            ...
        }
    outline_width: float
        Gruix del contorn.
    stroke_color: tuple[int,int,int,int]
        Color del contorn, en format (RGBA).
    
    Retorna
    -------
    QgsVectorLayer
        Capa vectorial en memòria amb la simbologia aplicada.
    """

    layer_clone = layer.materialize(QgsFeatureRequest())
    
    layer_clone.setName(f"{layer_clone.name()}_simbCat")
          
    # Llistat de cada categoria de la classe QgsRendererCategory, com a (value, symbol, label)
    categories = []

    # Creació de la categoria per cada valor d'atribut
    for cat, color in colors_categories.items():     
        symbol = QgsFillSymbol()
        
        symbol.setColor(QColor(*color))
        
        symbol_layer_0 = symbol.symbolLayer(0)
        symbol_layer_0.setStrokeWidth(outline_width)
        symbol_layer_0.setStrokeColor(QColor(*stroke_color))

        categoria = QgsRendererCategory(cat, symbol, str(cat))
        
        categories.append(categoria)

    renderer = QgsCategorizedSymbolRenderer(atribut, categories)
   
    layer_clone.setRenderer(renderer)
        
    return layer_clone

# =============================================================================
# SIMBOLOGIA GRADUADA
# =============================================================================

def simbologia_graduada(layer, atribut, num_classes, color_ramp, mode, stroke_color, stroke_width, invert_ramp=False):
    """
    Aplica simbologia graduada a una capa vectorial.
 
    La funció clona la capa d'entrada i hi aplica un renderer graduat
    a partir d'un atribut, un mètode de classificació i una rampa de 
    colors disponibles a QGIS.
        
    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa vectorial sobre la qual s'aplica la simbologia.
    atribut: str
        Camp utilitzat per a classificar els valors.
    num_classes: int
        Nombre de classes.
    color_ramp: str
        Nom d'una rampa de color d'estil de QGIS.
    mode: str
        Mètode de classificació de QGIS.
        Valors admesos:
        {
            "EqualInterval",
            "Quantile",
            "Jenks",
            "StdDev",
            "Pretty"
        }
    stroke_color: tuple[int,int,int,int]
        Color del contorn, en format (RGBA).
    stroke_width: float
        Gruix del contorn.
    invert_ramp: bool
        Inversió de la rampa de colors.
        Per defecte False.

    Retorna
    -------
    QgsVectorLayer
        Capa vectorial en memòria amb la simbologia aplicada.
    """

    layer_clone = layer.materialize(QgsFeatureRequest())
    
    layer_clone.setName(f"{layer_clone.name()}_simbGrad")
       
    # Mètodes de classificació possibles
    mode_map = {
        "EqualInterval": QgsGraduatedSymbolRenderer.EqualInterval,
        "Quantile": QgsGraduatedSymbolRenderer.Quantile,
        "Jenks": QgsGraduatedSymbolRenderer.Jenks,
        "StdDev": QgsGraduatedSymbolRenderer.StdDev,
        "Pretty": QgsGraduatedSymbolRenderer.Pretty
    }

    symbol = QgsFillSymbol()
    symbol.symbolLayer(0).setStrokeColor(QColor(*stroke_color))
    symbol.symbolLayer(0).setStrokeWidth(stroke_width)

    rampa = QgsStyle().defaultStyle().colorRamp(color_ramp)
    if invert_ramp:
        rampa.invert()

    # S'estableix el renderer graduat de la capa, amb els paràmetres entrats en la crida de la funció
    renderer = QgsGraduatedSymbolRenderer.createRenderer(
        layer_clone,
        atribut,
        num_classes,
        mode_map[mode],
        symbol,
        rampa
    )
   
    layer_clone.setRenderer(renderer)

    return layer_clone


def simbologia_graduada_manual(layer, color_ramp, intervals, atribut, stroke_color, stroke_width, invert_ramp=False):
    """
    Aplica simbologia graduada amb intervals definits manualment
    a una capa vectorial.

    La funció clona la capa d'entrada i hi aplica un renderer graduat
    a partir d'un atribut i una rampa de colors de QGIS.
    Els intervals de classificació es defineixen manualment,
    a diferència de `simbologia_graduada` que els calcula automàticament.
        
    Paràmetres
    ----------
    layer: QgsVectorLayer
        Capa vectorial sobre la qual s'aplica la simbologia.
    color_ramp: str
        Nom d'una rampa de color d'estil de QGIS.
    intervals: list[int]
        Llistat dels intervals de dades.
    atribut: str
        Camp utilitzat per a classificar els valors.
    stroke_color: tuple[int,int,int,int]
        Color del contorn, en format (RGBA).
    stroke_width: float
        Gruix del contorn.
    invert_ramp: bool
        Inversió de la rampa de colors.
        Per defecte False.

    Retorna
    -------
    QgsVectorLayer
        Capa vectorial en memòria amb la simbologia aplicada.
    """

    layer_clone = layer.materialize(QgsFeatureRequest())
    
    layer_clone.setName(f"{layer_clone.name()}_simbGradManual")
    
    # S'estableix una variable de la rampa de colors passada com a argument
    rampa = QgsStyle().defaultStyle().colorRamp(color_ramp)
    if invert_ramp:
        rampa.invert()

    # S'estableixen el nombre de salts de les dades, com al nombre d'intervals-1
    salts = len(intervals)-1

    rangs = []

    for i in range(salts):
        symbol = QgsFillSymbol()
        
        # S'estableix un color com el valor interpolat de la rampa de colors en funció del nombre d'intervals
        if salts == 1:
            fraccio = 0
        else:
            fraccio = float(i) / (salts-1)

        color = rampa.color(fraccio)
        
        symbol.setColor(color)
        symbol.symbolLayer(0).setStrokeColor(QColor(*stroke_color))
        symbol.symbolLayer(0).setStrokeWidth(stroke_width)
        
        range_i = QgsRendererRange(
            intervals[i],
            intervals[i+1],
            symbol,
            f"{intervals[i]:.2f}-{intervals[i+1]:.2f}"
        )
        
        rangs.append(range_i)

    # S'estableix el renderer graduat de la capa, amb l'atribut i el llistat de rangs
    renderer = QgsGraduatedSymbolRenderer(atribut, rangs)
    layer_clone.setRenderer(renderer)

    return layer_clone