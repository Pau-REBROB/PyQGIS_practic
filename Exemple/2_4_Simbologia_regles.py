"""SIMBOLOGIA BASADA EN REGLES"""

# Desactivar la visibilitat de totes les capes importades
for layer in project.mapLayers().values():
    root.findLayer(layer).setItemVisibilityChecked(False)


# En aquest cas, no es crea una funció
# Es decideix aplicar la simbologia sobre la capa de barris
# Clonació de la capa d'entrada
layer_clone = dict_layers["Limits_administratius"]["Barris"].clone()
    
# Assignació d'un nou nom
layer_clone.setName(f"{layer_clone.name()}_simbRegles")
    
# Addició de la capa al projecte
project.addMapLayer(layer_clone, False)
    
# Creació d'un grup de capes de simbologia única, si no existeix
group = root.findGroup("Simbologia_regles")
if not group:
  group = root.addGroup("Simbologia_regles")
# Addició de la capa al grup
group.addLayer(layer_clone)

# Definició el constructor del símbol
symbol = QgsSymbol.defaultSymbol(layer_clone.geometryType())
base_layer = symbol.symbolLayer(0)
base_layer.setStrokeWidth(0.5)
base_layer.setStrokeColor(QColor("white"))

# Definició de les regles
rule_min = QgsRuleBasedRenderer.Rule(
  symbol.clone(),
  filterExp = '"AREA" < 150000',
  label = 'Area_min',
  description = 'Barris d\'àrea més petita'
)
rule_max = QgsRuleBasedRenderer.Rule(
  symbol.clone(),
  filterExp = '"AREA" > 1750000',
  label = 'Area_max',
  description = 'Barris d\'àrea més gran'
)

# Modificació de la simbologia segons les regles
rule_min.symbol().setColor(QColor("blue"))
rule_max.symbol().setColor(QColor("red"))

# Definició del renderitzador i l'arbre de decisions
rule_renderer = QgsRuleBasedRenderer(symbol)
root_rule = rule_renderer.rootRule()
# Eliminació de la "regla base"
root_rule.removeChildAt(0)
# Addició de les regles a l'arbre de decisions
root_rule.appendChild(rule_min)
root_rule.appendChild(rule_max)

# Assignació de les regles a la capa vectorial
layer_clone.setRenderer(rule_renderer)


# Etiquetatge
# Configuració de les etiquetes
label_settings = QgsPalLayerSettings()

# Camp a etiquetar
label_settings.fieldName = "NOM"

# Establiment del format de les etiquetes
text_format = QgsTextFormat()
text_format.setFont(QFont("Calibri", 8))
text_format.setSize(8)
text_format.setColor(QColor("grey"))

# Generació del buffer
buffer = QgsTextBufferSettings()
buffer.setEnabled(True)
buffer.setSize(0.5)
buffer.setColor(QColor("white"))
text_format.setBuffer(buffer)

# Assignació del format i activació de l'etiquetatge
label_settings.setFormat(text_format)
label_settings.enabled = True

# Creació del motor d'etiquetes i assignació a la capa de Barris
layer_labels = QgsVectorLayerSimpleLabeling(label_settings)
layer_clone.setLabeling(layer_labels)
layer_clone.setLabelsEnabled(True)


# Actualització del llenç
layer_clone.triggerRepaint()
iface.mapCanvas().refresh()
# Actualització del panell de capes
iface.layerTreeView().refreshLayerSymbology(layer_clone.id())
