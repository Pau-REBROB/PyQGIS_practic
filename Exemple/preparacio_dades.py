"""NETEJA DE CAPES"""

from qgis.core import (
    QgsFeatureRequest,
    QgsProject,
    QgsVectorFileWriter,
    QgsVectorLayer, 
    edit
)

def netejar_capa(layer, camps):
    """
    Funció que elimina els camps especificats de la capa
    """

    # Clonació de la capa original per no modificar-la
    layer_clone = layer.materialize(QgsFeatureRequest())

    # Llista buida que contindrà els índex dels camps a eliminar
    index_eliminar = []

    # Cerca dels índexs dels camps a eliminar
    for i, field in enumerate(layer_clone.fields()):
        # Si el nom del camp no es troba a la llista de camps a mantenir passada com a paràmetre
        # Afegir el seu índex a la llista buida
        if field.name() not in camps:
            index_eliminar.append(i)
    
    # Edició de la capa i eliminació dels camps
    with edit(layer_clone):
        layer_clone.deleteAttributes(index_eliminar)
   
   
    return layer_clone


def desar_carregar_capa(layer_clone):
    """
    Funció que desa la capa neta per la funció `netejar_capa()` en un arxiu GPKG i carrega la capa al projecte
    """

    # Desat de la capa neta
    transform_context = QgsProject.instance().transformContext()
    
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.driverName = "GPKG"
    
    QgsVectorFileWriter.writeAsVectorFormatV3(layer_clone, 
                                              f"C:/projectes_git/Dades/PyQGIS_Repo/Dades_netes/{layer_clone.name()}_clean.gpkg", 
                                              transform_context, 
                                              save_options)

    # Importació de la capa al projecte
    layer_clean = QgsVectorLayer(f"C:/projectes_git/Dades/PyQGIS_Repo/Dades_netes/{layer_clone.name()}_clean.gpkg",
                                 layer_clone.name(),
                                 "ogr")

    return layer_clean 
    

def netejar_grup(dict_layers, configuracio):
    """
    Funció d'alt nivell que genera un nou diccionari de capes a partir de les funcions `netejar_capa()` i `desar_carregar_capa()`
    La funció 
        Agafa el diccionari de diccionaris de capes generat al mòdul d'importació.py
        Itera sobre cada capa QgsVectorLayer present
            Neteja la capa dels camps no desitjats
            Desa la capa neta en un arxiu nou
            Carrega la nova capa
        Agafa la nova capa neta carregada i l'utilitza per suplir una nova QgsVectorLayer en el diccionari de diccionaris de capes
    """

    for grup, capes in dict_layers.items():
        
        for nom, layer in capes.items():
            
            if nom in configuracio[grup]:
                camps = configuracio[grup][nom]
            else:
                camps = configuracio[grup]["*"]
            
            layer_clone = netejar_capa(layer, camps)

            layer_clean = desar_carregar_capa(layer_clone)
            
            dict_layers[grup][nom] = layer_clean 

    return dict_layers
