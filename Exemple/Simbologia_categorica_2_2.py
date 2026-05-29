"""SIMBOLITZACIÓ"""

"""SIMBOLOGIA CATEGÒRICA"""

from qgis.core import ( 
    QgsProject,
    QgsFillSymbol,
    QgsRendererCategory,
    QgsCategorizedSymbolRenderer
)
from qgis.utils import iface
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtCore import Qt, QPointF

project = QgsProject.instance()
root = project.layerTreeRoot()

def simbologia_categorica(layer, atribut, colors, outline_width, stroke_color):
    """
    Aplica una simbologia categòrica a una capa poligonal existent

    La funció:
        Clona la capa d'entrada
        Assigna un nom nou a la capa clonada
        Crea un grup de simbologia categòrica 
        Genera simbologia
    
    Paràmetres de la funció:
        layer : capa vectorial de tipus poligonal sobre la que aplicar la simbologia
        atribut : camp a representar
        colors : llista de colors - passats com a string - que tindran les categories ## Es podria establir com a aleatori
        outline_width : gruix de la línia de contorn (0.26 per defecte)
        stroke_color : color de la línia de contorn, passat com a string
    """
    # Clonació de la capa d'entrada
    layer_clone = layer.clone()
    
    # Assignació d'un nou nom
    layer_clone.setName(f"{layer_clone.name()}_simbCat")
    
    # Addició de la capa al projecte
    project.addMapLayer(layer_clone, False)
    
    # Creació d'un grup de capes de simbologia única, si no existeix
    group = root.findGroup("Simbologia_categorica")
    if not group:
        group = root.addGroup("Simbologia_categorica")
    # Addició de la capa al grup
    group.addLayer(layer_clone)
    
    # Obtenció dels valors únics de l'atribut categòric, ordenats
    # Filtratge dels elements no nuls
    valors_atribut = sorted(set([feat[atribut] for feat in layer_clone.getFeatures() if feat[atribut] is not None]))

    # Llistat de cada categoria de la classe QgsRendererCategory, com a (value, symbol, label)
    categories = []

    # Creació de la categoria per cada valor d'atribut
    for valor, color in zip(valors_atribut, colors):
        # Creació d'una variable tipus QColor a partir del nom del color introduït com a argument
        col = QColor(color)
        
        # Creació del constructor del símbol
        symbol = QgsFillSymbol()
        
        # S'estableix el color del farcit
        symbol.setColor(QColor(col))
        
        # Accés a la capa interna del símbol
        symbol_layer_0 = symbol.symbolLayer(0)
        # S'estableix el gruix i el color de la línia de contorn
        symbol_layer_0.setStrokeWidth(outline_width)
        symbol_layer_0.setStrokeColor(QColor(stroke_color))

        # Creació de la categoria
        cat = QgsRendererCategory(valor, symbol, str(valor))
        
        # Inserció de l'objecte de categoria a la llista de categories
        categories.append(cat)

    # S'estableix el renderer categòric de la capa i se li assinga l'atribut categòric i el llistat de categories 
    renderer = QgsCategorizedSymbolRenderer(atribut, categories)
   
    # S'aplica a la capa el renderer creat
    layer_clone.setRenderer(renderer)
    
    # Actualització del llenç
    layer_clone.triggerRepaint()
    iface.mapCanvas().refresh()
    # Actualització del panell de capes
    iface.layerTreeView().refreshLayerSymbology(layer_clone.id())

    # Retorn de la capa amb la simbologia
    return layer_clone



if __name__ == '__main__':
    # Codi a executar quan es cridi des d'aquest mateix script

    # Desactivar la visibilitat de totes les capes importades
    for layer in project.mapLayers().values():
        node = root.findLayer(layer)
        if node:
            node.setItemVisibilityChecked(False)

    # Aplicació de la simbologia categòrica a les capes dels límits administratius
    ## La variable categòrica serà el districte
    params_limAdm_cat = {
        'Barris': {"atribut": 'DISTRICTE', 
                   "colors": ["lightsalmon", "lightpink", "lightcoral", "lightblue", "lightsteelblue", "limegreen", "lightyellow", "lightgoldenrodyellow", "lightgrey", "whitesmoke"],
                   "outline_width": 0.2, 
                   "stroke_color": "black"},
        'Districtes': {"atribut": 'DISTRICTE', 
                       "colors": ['palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue'],
                       "outline_width": 0.4, 
                       "stroke_color": "black"},
    }

    for layer in dict_layers["Limits_administratius"].values():
        # Comprovació que la capa existeix en el diccionari de paràmetres
        if layer.name() in params_limAdm_cat:
            # Assingació del conjunt de paràmetres de la capa a una nova variable més manejable
            p_layer = params_limAdm_cat[layer.name()]

            # Crida de la funció amb la nova variable de paràmetres
            simbologia_categorica(layer, p_layer["atribut"], p_layer["colors"], p_layer["outline_width"], p_layer["stroke_color"])
        else:
            print(f"El diccionari de paràmetres no recull la capa {layer.name()}!")
