"""Funcions de PyQGIS sobre Barcelona"""


# Generar instància del projecte
project = QgsProject.instance()
# Generar instància del panell de capes
root = project.layerTreeRoot()


# Carregar capes al projecte
# Generar índex espacial sobre les geometries de cada capa
## Límits administratius: Barris
BcnBarris = QgsVectorLayer("C:/PyQGIS_practic/Limits_administratius_BCN/0301040100_Barris_UNITATS_ADM.shp", 'BCN_Barris', "ogr")
if BcnBarris.isValid():
    root.insertLayer(0, BcnBarris)
    BcnBarrisIndex = QgsSpatialIndex(BcnBarris.getFeatures())
else:
    print("Error al carregar la capa!")

## Límits administratius: Districtes
BcnDistrictes = QgsVectorLayer("C:/PyQGIS_practic/Limits_administratius_BCN/0301040100_Districtes_UNITATS_ADM.shp", 'BCN_Districtes', "ogr")
if BcnDistrictes.isValid():
    root.insertLayer(1, BcnDistrictes)
    BcnDistrictesIndex = QgsSpatialIndex(BcnDistrictes.getFeatures())
else:
    print("Error al carregar la capa!")

## Límits administratius: Terme municipal
BcnTerme = QgsVectorLayer("C:/PyQGIS_practic/Limits_administratius_BCN/0301040100_TermeMunicipal_UNITATS_ADM.shp", 'BCN_Terme_Municipal', "ogr")
if BcnTerme.isValid():
    root.insertLayer(2, BcnTerme)
    BcnTermeIndex = QgsSpatialIndex(BcnTerme.getFeatures())
else:
    print("Error al carregar la capa!")


# Comprovar el sistema de referència de coordenades de les capes i el projecte
print("SRC de la capa Barris:", BcnBarris.crs().authid())
print("SRC de la capa Districtes:", BcnDistrictes.crs().authid())
print("SRC de la capa Terme municipal:", BcnTerme.crs().authid())
print("SRC del projecte:", project.crs().authid())


# Modificació de la simbologia ÚNICA de les capes
## Capa de barris
symbolBarris = QgsFillSymbol.createSimple({"color":"transparent", "outline_width":"0.2"})
BcnBarris.renderer().setSymbol(symbolBarris)
BcnBarris.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(BcnBarris.id())

## Capa de districtes
symbolDistrictes = QgsFillSymbol.createSimple({"color":"transparent", "outline_width":"0.4"})
BcnDistrictes.renderer().setSymbol(symbolDistrictes)
BcnDistrictes.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(BcnDistrictes.id())

## Capa del terme municipal
symbolTerme = QgsFillSymbol.createSimple({"color":"lightyellow", "outline_width":"0.6"})
BcnTerme.renderer().setSymbol(symbolTerme)
BcnTerme.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(BcnTerme.id())


