# FUNCIÓ DE SIMBOLOGIA GRADUADA SEGONS L'ÍNDEX SHANNON

from qgis.core import (
    QgsProject,
    QgsFillSymbol,
    QgsGraduatedSymbolRenderer,
    QgsStyle
)
from qgis.utils import iface
from qgis.PyQt.QtGui import QColor

def simbologia_shannon(layer, num_classes, color_ramp, mode, stroke_color, stroke_width, atribut = "H_Shannon"):
    """
    Aplica simbologia graduada segons l'índex de Shannon a una capa poligonal existent
    Utilitza un mètode de classificació i una rampa de colors propis de QGIS
    Es modifica la simbologia dels polígons

    La funció:
        Clona la capa d'entrada
        Assigna un nom nou a la capa clonada 
        Genera simbologia especificant el mètode de classificació i la rampa de colors
        
    Paràmetres de la funció:
        layer : capa de tipus poligonal sobre la que aplicar la simbologia
        atribut : Índex H de Shannon
        num_classes : número de classes amb què es divideix el valor de l'atribut
        color_ramp : rampa de color d'estil QGIS
        mode : mètode de classificació de QGIS
        stroke_color : color de la línia de contorn, passat com a string
        stroke_width : gruix de la línia de contorn (0.26 per defecte)
    """
    # Clonació de la capa d'entrada
    layer_clone = layer.clone()
    
    # Assignació d'un nou nom
    layer_clone.setName(f"{layer_clone.name()}_simbGrad_Shannon")
      
    # Mètodes de classificació possibles
    mode_map = {
        "EqualInterval": QgsGraduatedSymbolRenderer.EqualInterval,
        "Quantile": QgsGraduatedSymbolRenderer.Quantile,
        "Jenks": QgsGraduatedSymbolRenderer.Jenks,
        "StdDev": QgsGraduatedSymbolRenderer.StdDev,
        "Pretty": QgsGraduatedSymbolRenderer.Pretty
    }

    # Es defineix la simbologia, amb el color i el gruix del contorn
    symbol = QgsFillSymbol.createSimple({
    "outline_color": stroke_color,
    "outline_width": stroke_width
    })

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
    
    # Addició de la capa al projecte
    QgsProject.instance().addMapLayer(layer_clone)

    # Actualització del llenç
    layer_clone.triggerRepaint()
    iface.mapCanvas().refresh()
    # Actualització del panell de capes
    iface.layerTreeView().refreshLayerSymbology(layer_clone.id())

    # Retorn de la capa amb la simbologia
    return layer_clone