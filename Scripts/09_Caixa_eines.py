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
result = processing.run("algorith_id", {params})
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

  # Declaració de la nova instància de la classe de l'algoritme
  def createInstance(self):
    return type(self)()

  # Configuració de les definicions dels paràmetres d'entrada i de sortida
  ## Aquells definits al principi de tot
  # Es defineix la interfície de l'algoritme, que construeix automàticament el formulari UI, la validació i l'ajuda
  def initAlgorithm(self, config=None):
    self.addParameter(
      # Si es demana una capa vectorial o ràster d'entrada
      QgsProcessingParameterFeatureSource(self.entry_param_name, "Description"),
      # Si es demana un nombre d'entrada
      QgsProcessingParameterNumber(self.entry_param_name, "Description"),
      ## Si el nombre demanat tingués un valor per defecte
      QgsProcessingParameterNumber(self.entry_param_name, "Description", QgsProcessingParameterNumber.Double, 2),
      # Si es defineix una capa vectorial o ràster de sortida
      ## És un element abstracte, que posteriorment s'utilitzarà per a generar la capa de sortida
      QgsProcessingParameterFeatureSink(self.exit_param_name, "Description")
    )

  # Definició de les operacions pròpiament dites
  def processAlgorithm(self, parameters, context, feedback):
    #
    #

    # El *context* recull el context del projecte: capes carregades, SRC, gestió de la memòria, etc.
    # És un objecte de la classe `QgsProcessingContext`

    # El *feedback* permet comunicar-se amb l'usuari
    # Permet mostrar el progrés (`feedback.setProgress()`), la cancel·lació o els missatges (`feedback.pushInfo()`, `feedback.pushWarning()`, `feedback.reportError()`) 
    # És un objecte de la classe `QgsProcessingFeedback`

    # Els *helpers* 




