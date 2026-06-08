"""SIMBOLITZACIÓ"""

"""SIMBOLOGIA GRADUADA"""

from qgis.core import (
    QgsProject,
    QgsFillSymbol,
    QgsGraduatedSymbolRenderer,
    QgsStyle,
)
from qgis.PyQt.QtGui import QColor
from qgis.utils import iface

project = QgsProject.instance()
root = project.layerTreeRoot()

def simbologia_graduada_QGIS(layer, atribut, num_classes, color_ramp, mode, stroke_color, stroke_width):
    """
    Aplica simbologia graduada a una capa poligonal existent
    Utilitza un mètode de classificació i una rampa de colors propis de QGIS
    Es modifica la simbologia dels polígons

    La funció:
        Clona la capa d'entrada
        Assigna un nom nou a la capa clonada
        Crea un grup de simbologia graduada 
        Genera simbologia especificant el mètode de classificació i la rampa de colors
        
    Paràmetres de la funció:
        layer : capa de tipus poligonal sobre la que aplicar la simbologia
        atribut : camp a representar
        num_classes : número de classes amb què es divideix el valor de l'atribut
        color_ramp : rampa de color d'estil QGIS
        mode : mètode de classificació de QGIS
        stroke_color : color de la línia de contorn, passat com a string
        stroke_width : gruix de la línia de contorn (0.26 per defecte)
    """
    # Clonació de la capa d'entrada
    layer_clone = layer.clone()
    
    # Assignació d'un nou nom
    layer_clone.setName(f"{layer_clone.name()}_simbGradQGIS")
    
    # Addició de la capa al projecte
    project.addMapLayer(layer_clone, False)
    
    # Creació d'un grup de capes de simbologia única, si no existeix
    group = root.findGroup("Simbologia_graduada_QGIS")
    if not group:
        group = root.addGroup("Simbologia_graduada_QGIS")
    # Addició de la capa al grup
    group.addLayer(layer_clone)

    # Mètodes de classificació possibles
    mode_map = {
        "EqualInterval": QgsGraduatedSymbolRenderer.EqualInterval,
        "Quantile": QgsGraduatedSymbolRenderer.Quantile,
        "Jenks": QgsGraduatedSymbolRenderer.Jenks,
        "StdDev": QgsGraduatedSymbolRenderer.StdDev,
        "Pretty": QgsGraduatedSymbolRenderer.Pretty
    }

    # Es defineix la simbologia, amb el color i el gruix del contorn
    symbol = QgsFillSymbol()
    symbol.symbolLayer(0).setStrokeColor(QColor(stroke_color))
    symbol.symbolLayer(0).setStrokeWidth(stroke_width)

    # S'estableix el renderer graduat de la capa, amb els paràmetres entrats en la crida de la funció
    renderer = QgsGraduatedSymbolRenderer.createRenderer(
        layer_clone,
        atribut,
        num_classes,
        mode_map[mode],
        symbol,
        QgsStyle().defaultStyle().colorRamp(color_ramp)
    )
    
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

    # Aplicació de la funció a les capes
    ## La variable graduada serà l'àrea de l'element
    params_limAdm_grad = {
        'Barris': {"atribut": 'AREA', "num_classes": 6, "color_ramp": "Mako", "mode": "Pretty",
                   "stroke_color": "white", "stroke_width": 0.25},
        'Districtes': {"atribut": 'AREA', "num_classes": 6, "color_ramp": "Cividis", "mode": "Pretty",
                       "stroke_color": "white", "stroke_width": 0.45},
    }

    for layer in dict_layers["Limits_administratius"].values():
        # Comprovació que la capa existeix en el diccionari de paràmetres
        if layer.name() in params_limAdm_grad:
            # Assingació del conjunt de paràmetres de la capa a una nova variable més manejable
            p_layer = params_limAdm_grad[layer.name()]

            # Crida de la funció amb la nova variable de paràmetres
            simbologia_graduada_QGIS(layer, p_layer["atribut"], p_layer["num_classes"], p_layer["color_ramp"], p_layer["mode"],
                                     p_layer["stroke_color"], p_layer["stroke_width"])
        else:
            print(f"El diccionari de paràmetres no recull la capa {layer.name()}!")


    # Aplicació de la simbologia graduada a les capes
    ## La variable graduada serà el número de plantes per sobre el terra de l'element
    params_cadastre_grad_man = {
        'Edificis': {"atribut": 'numberOfFloorsAboveGround', "num_classes": 6, "color_ramp": "Spectral", "mode": 'Jenks',
                     "stroke_color": "white", "stroke_width": 0.1}
    }

    for layer in dict_layers["Cadastre"].values():
        # Comprovació que la capa existeix en el diccionari de paràmetres
        if layer.name() in params_cadastre_grad_man:
            # Assingació del conjunt de paràmetres de la capa a una nova variable més manejable
            p_layer = params_cadastre_grad_man[layer.name()]

            # Crida de la funció amb la nova variable de paràmetres
            simbologia_graduada_QGIS(layer, p_layer["atribut"], p_layer["num_classes"], p_layer["color_ramp"],
                                     p_layer["mode"], p_layer["stroke_color"], p_layer["stroke_width"])
        else:
            print(f"El diccionari de paràmetres no recull la capa {layer.name()}!")
      