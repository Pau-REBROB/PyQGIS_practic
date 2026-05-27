"""SIMBOLOGIA BASADA EN REGLES"""

# Desactivar la visibilitat de totes les capes importades
for layer in project.mapLayers().values():
    root.findLayer(layer).setItemVisibilityChecked(False)


# En aquest cas, no es crea una funció
# Es decideix aplicar la simbologia sobre la capa de barris

# Definició el constructor del símbol
symbol = QgsSymbol.defaultSymbol(dict_layer["Limits_administratius"]["Barris"].geometryType())
base_layer = symbol.symbolLayer(0)
base_layer.setStrokeWidth(0.75)
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
  filterExp = '"AREA" > 15000000',
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
dict_layer["Limits_administratius"]["Barris"].setRenderer(rule_renderer)

# Actualització del llenç
dict_layer["Limits_administratius"]["Barris"].triggerRepaint()
iface.mapCanvas().refresh()
# Actualització del panell de capes
iface.layerTreeView().refreshLayerSymbology(dict_layer["Limits_administratius"]["Barris"].id())
