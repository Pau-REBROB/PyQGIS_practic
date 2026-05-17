"""Caixa d'eines de QGIS"""

# Totes les funcions i algoritmes presents a la caixa d'eines de QGIS son accessibles des de PyQGIS a través del mòdul `processing`
from qgis import processing

# Per utilitzar alguna de les funcions de la caixa d'eines, cal cridar el mètode `.run()` sobre *processing*
processing.run("native:algorithm_name", {dict_of_parameters})
## El primer argument és el nom ORIGINAL de la funció
### Les funcions pròpies de QGIS comencen totes amb "native:"
## El segon argument és un diccionari de paràmetres, propis de la funció que es vol utilitzar
### Els paràmetres concrets d'una funció específica poden no ser coneguts a priori. El mètode `.algorithmHelp()` retorna informació sobre la funció, incloent els paràmetres
processing.algorithmHelp("native:algorithm_name")

## Els paràmetres que segur que existiran en totes les funcions son 'INPUT' i 'OUTPUT'
### 'INPUT' fa referència a la capa - o elements d'una capa - sobre la que vol aplicar-se la funció
### 'OUTPUT' fa referència a el resultat de la funció, que serà "memory:" si es desitja que sigui un arxiu temporal, o la ruta completa de l'arxiu si es desitja guardar en local

# La manera habitual de treballar és guardar el resultat de la funció en una variable, i utilitzar el seu 'OUTPUT' per a afegir-la al canvas de QGIS
result = processing.run("algorithm_id", {params})
project.addMapLayer(result['OUTPUT'])
# Això implica que el resultat de *processing* és sempre un diccionari



"""Noves eines de processament"""

# Un mateix pot crear noves eines de processament de la classe `processing` i afegir-les a la caixa d'eines de QGIS
# El procediment comença declarant una nova classe d'un algoritme dins de processing
class new_algorithm(QgsProcessingAlgorithm):
  # Declaració dels paràmetres i constants
  # PyQGIS treballa amb claus de text internes
  entry_param_name = "entry_param_name"
  exit_param_name = "exit_param_name"

  # Declaració de l'identificador de l'algoritme utilitzat per cridar la funció (en minúscules)
  def name(self):
    return "new_algorithm"

  # Declaració del nom llegible per humans de l'algoritme, que es veu a la GUI
  def displayName(self):
    return "new_algorithm_display_name"

  # Declaració del nom de la carpeta d'algoritmes on estarà el nou algoritme
  def group(self):
    return "group_name"

  # Declaració de l'identificador de la carpeta d'algoritmes  
  def groupId(self):
    return "group_name_id"

  # Declaració de la nova instància de la classe de l'algoritme
  def createInstance(self):
    return type(self)()

  # Configuració de les definicions dels paràmetres d'entrada i de sortida
  ## Aquells definits al principi de tot
  # Es defineix la interfície de l'algoritme, que construeix automàticament el formulari UI, la validació i l'ajuda
  def initAlgorithm(self, config=None):
    self.addParameter(
      # Si es demana una capa vectorial o ràster d'entrada
      QgsProcessingParameterFeatureSource(self.entry_param_name, "Description")),
    sefl.addParameter(
      # Si es demana un nombre d'entrada
      QgsProcessingParameterNumber(self.entry_param_name, "Description", QgsProcessingParameterNumber.Double)),
    self.addParameter(
      ## Si el nombre demanat tingués un valor per defecte, només cal especificar-lo
      QgsProcessingParameterNumber(self.entry_param_name, "Description", QgsProcessingParameterNumber.Double, 2)),
    self.addParameter(
      # Si es defineix una capa vectorial o ràster de sortida
      ## És un element abstracte, que posteriorment s'utilitzarà per a generar la capa de sortida
      QgsProcessingParameterFeatureSink(self.exit_param_name, "Description"))

  # Definició de les operacions pròpiament dites
  def processAlgorithm(self, parameters, context, feedback):
    # El *context* recull el context del projecte: capes carregades, SRC, gestió de la memòria, etc.
    # És un objecte de la classe `QgsProcessingContext`

    # El *feedback* permet comunicar-se amb l'usuari
    # Permet mostrar el progrés (`feedback.setProgress()`), la cancel·lació o els missatges (`feedback.pushInfo()`, `feedback.pushWarning()`, `feedback.reportError()`) 
    # És un objecte de la classe `QgsProcessingFeedback`

    # Els *helpers* gestionen el context permeten validar els paràmetres d'entrada - definits al principi
    # Converteixen els paràmetres en objectes manipulables dins del codi a través de `self.parameterAsX()`
    layer = self.parameterAsVectorLayer(parameters, self.entry_param_name, context)
    sink, dest_id = self.parameterAsSink(parameters, self.exit_param_name, context)
    ## Altres helpers útils son `parameterAsSource`, `parameterAsString`, `parameterAsColor`, `parameterAsEnum` o `parameterAsExtent`

    # Amb els paràmetres ja en format usable, es procedeix a realitzar les operacions de l'algoritme
    # El flux idoni de treball és
    ## Llegir els paràmetres d'input
    ### Utilitzar `AsSource` quan només es vulgui fer una lectura de les dades, sense edició ni renderització
    ### No carrega tota la capa a la memòria, pel que és més eficient i segur
    ### Utilitzar `AsVectorLayer` quan es vulgui la capa completa de QGIS
    ## Aplicar les funcions de `processing` - idoni quan la funció es troba a la caixa d'eines de QGIS
    ## Preparar els paràmetres d'output
    ## Processar les dades de sortida
    for feat in layer.getFeatures():
      # modificació dels features
      # al final, però, s'ha d'incloure:
      sink.addFeature(feat)
    ## Aplicar funcions de post-processat: simbologia, etiquetes, afegir capes al canvas...
    ## Retorn de resultats
    return {self.exit_param_name: dest_id}



"""Creació d'un plugin"""

# La manera de distribuir i integrar un algoritme nou de manera permanent a QGIS és a través de la creació d'un plugin
# D'aquesta manera, s'estalvia haver d'executar-lo manualment cada vegada des de la consola

# L'estructura bàsica mínima d'un plugin de QGIS és
# my_plugin/
  # __init__.py          # punt d'entrada
  # my_plugin.py         # classe principal del plugin
  # metadata.txt         # informació del plugin
  # provider.py          # registra els algoritmes al processing
  # algorithm.py         # el QgsProcessingAlgorithm ja documentat


# __init__.py

# És el punt d'entrada del plugin, i el primer arxiu que QGIS llegeix en carregar-lo
# Ha de contenir obligatòriament una funció `classFactory()` que retorni una instància de la classe principal - MyPlugin
# Els seus arguments son `iface`, l'objecte que permet interactuar amb la GUI
def classFactory(iface):
    from .my_plugin import MyPlugin
    return MyPlugin(iface)

# La importació es fa de manera relativa - amb el punt davant
# Això vol dir que la importació es fa des del mateix directori on es troba el fitxer


# metadata.txt"""

# És un fitxer de text pla en format INI - conté la informació en format clau=valor - que conté la informació del plugin
# És obligatori per a que QGIS reconegui el plugin i el pugui carregar
# Tota la informació es troba sota la secció [general]
[general]

# Informació bàsica - tots obligatoris
name=My Plugin
version=0.1
qgisMinimumVersion=3.0
description=Descripció del plugin
author=Nom de l'autor
email=correu@exemple.com

# Informació opcional però recomanable
about=Descripció llarga del plugin  
tracker=https://github.com/...      # URL per a reportar errors
repository=https://github.com/...   
tags=vector, analysis, processing   
category=Vector                     # Categoria del plugin: Vector, Raster, Database, Web...
icon=icon.png                       
hasProcessingProvider=yes           # Indica que el plugin afegeix algoritmes a la caixa d'eines

# Informació de compatibilitat
qgisMaximumVersion=3.99             # Versió màxima de QGIS compatible - opcional
experimental=False                  
deprecated=False                    


# provider.py
# El proveïdor és la classe que registra els algoritmes al processing de QGIS
# Ha d'heretar de la classe `QgsProcessingProvider`
class MyProvider(QgsProcessingProvider):
    # Identificador únic del proveïdor
    def id(self):
        return "my_provider"
    # Nom llegible per humans del proveïdor, que es veu a la caixa d'eines
    def name(self):
        return "My Provider"
    # Càrrega dels algoritmes del proveïdor
    # És aquí on es registren tots els algoritmes que contindrà el plugin
    def loadAlgorithms(self):
        self.addAlgorithm(MyAlgorithm())


# my_plugin.py
# És la classe principal del plugin
# Ha d'heretar de la classe `QgsProcessingAlgorithm`
class MyPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.provider = None
    # S'executa en carregar el plugin
    def initGui(self):
        self.provider = MyProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)
    # S'executa en descarregar el plugin
    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)


# algorithm.py
# Es correspon amb l'algoritme de la nova eina de processament descrit anteriorment, exactament igual

