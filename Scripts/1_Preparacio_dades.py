"""SISTEMES DE REFERÈNCIA"""

# Comprovació dels sistema de referència de coordenades del projecte i de les capes
print("SRC del projecte:", project.crs().authid())

for group in layers.values():
    for layer in group.values():
        # Impresió per pantalla del SRC de cada capa, en codi EPSG
        print(f"El SRC de la capa {layer.name()} és {layer.crs().authid()}")
        # Comparació amb el SRC del projecte
        if layer.crs().authid() == project.crs().authid():
            print(f"La capa {layer.name()} i el projecte estan en el mateix SRC")
        else:
            print(f"La capa {layer.name()} està en el SRC {layer.crs().authid()} i necessita ser reprojectada a EPSG:25831!")



"""NETEJA DE CAPES"""

# LÍMITS ADMINISTRATIUS
# Les capes contenen molts camps (fins a 46!) que resulten innecessaris
# Les tres capes del grup de Límits administratius contenen els mateixos 46 camps
# Número de camps
layers["Limits_administratius"]['Barris'].fields().count()
# Nom dels camps
layers["Limits_administratius"]['Barris'].fields().names()

# Camps a mantenir
camps_mantenir_limAdm = ['DISTRICTE', 'BARRI', 'PERIMETRE', 'AREA', 'TIPUS_UA', 'NOM']
  # 'DISTRICTE' codi del districte
  # 'BARRI' codi del barri
  # 'PERIMETRE' perímetre de la geometria
  # 'AREA' superfície de la geometria
  # 'TIPUS_UA' tipus d'unitat administrativa - indica si es tracta d'un barri, un districte o un terme municipal
  # 'NOM' nom de la unitat administrativa

# Camps a eliminar
for layer in layers["Limits_administratius"].values():
    # Llista buida que contindrà els índex dels camps a eliminar
    index_eliminar = []
    
    # Per cada capa del grup de Límits administratius, es busquen els seus camps i el seu índex
    for i, field in enumerate(layer.fields()):
        # Si el nom del camp no es troba a la llista de camps a mantenir:
        # Afegir el seu índex a la llista buida a eliminar
        if field.name() not in camps_mantenir_limAdm:
            index_eliminar.append(i)
        else:
            print(f"Camp {field.name()} conservat")

    # Edició de la capa i eliminació del camp i els seus atributs
    with edit(layer):
        layer.deleteAttributes(index_eliminar)

# Comprovació de l'eliminació
for layer in layers["Limits_administratius"].values():
    print(f"Número de camps presents a la capa {layer.name()} després de la neteja: {layer.fields().count()}")
    print(f"Camps presents: {layer.fields().names()}")

# GRAF VIARI
# Número de camps
layers["Graf"]['Graf_trams'].fields().count()
# Nom dels camps
layers["Graf"]['Graf_trams'].fields().names()

# Es segueix el mateix procediment que amb els límits administratius
# Camps a mantenir
camps_mantenir_grafViari = ['COORD_X', 'COORD_Y', 'LONGITUD', 'ANGLE', 'C_Tram', 'Distric_D', 'NDistric_D', 'TVia_D', 'NVia_D', 'Distric_E', 'NDistric_E', 'TVia_E', 'NVia_E']
# Camps a eliminar
for layer in layers["Graf"].values():
    
    index_eliminar = []
    
    for i, field in enumerate(layer.fields()):
        if field.name() not in camps_mantenir_grafViari:
            index_eliminar.append(i)
        else:
            print(f"Camp {field.name()} conservat")
    
    with edit(layer):
        layer.deleteAttributes(index_eliminar)

# Comprovació de l'eliminació
for layer in layers["Graf"].values():
    print(f"Número de camps presents a la capa {layer.name()} després de la neteja: {layer.fields().count()}")
    print(f"Camps presents: {layer.fields().names()}")

