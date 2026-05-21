"""NETEJA DE CAPES"""

# LÍMITS ADMINISTRATIUS
# Les capes contenen molts camps (fins a 46!) que resulten innecessaris
# Les tres capes del grup de Límits administratius contenen els mateixos 46 camps
# Número de camps
dict_layers["Limits_administratius"]['Barris'].fields().count()
# Nom dels camps
dict_layers["Limits_administratius"]['Barris'].fields().names()

# Camps a mantenir
camps_mantenir_limAdm = ['DISTRICTE', 'BARRI', 'PERIMETRE', 'AREA', 'TIPUS_UA', 'NOM']
  # 'DISTRICTE' codi del districte
  # 'BARRI' codi del barri
  # 'PERIMETRE' perímetre de la geometria
  # 'AREA' superfície de la geometria
  # 'TIPUS_UA' tipus d'unitat administrativa - indica si es tracta d'un barri, un districte o un terme municipal
  # 'NOM' nom de la unitat administrativa

# Camps a eliminar
for layer in dict_layers["Limits_administratius"].values():
    # Clonació de la capa per no modificar l'original
    layer.clone()

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
for layer in dict_layers["Limits_administratius"].values():
    print(f"Número de camps presents a la capa {layer.name()} després de la neteja: {layer.fields().count()}")
    print(f"Camps presents: {layer.fields().names()}")

# Addició de la capa al projecte
##################

# URBANISME
## Adreces
# Número de camps
dict_layers["Urbanisme"]['Adreces'].fields().count()
# Nom dels camps
dict_layers["Urbanisme"]['Adreces'].fields().names()

# Camps a mantenir
camps_mantenir_adreces = ['CODI_ILLA', 'CODI_PARC', 'CODICARRER', 'CODI_INE', 'NOM_VIA', 'DISTRICTE', 'BARRI']
    # 'CODI_ILLA' codi illa parcel·lària
    # 'CODI_PARC' codi parcel·la
    # 'CODICARRER' codi carrer
    # 'CODI_INE' codi INE carrer
    # 'NOM_VIA' nom carrer
    # 'DISTRICTE' codi districte
    # 'BARRI' codi barri

# Camps a eliminar
for layer in dict_layers["Urbanisme"]['Adreces'].values():
    # Clonació de la capa
    layer.clone()

    # Llista buida que contindrà els índex dels camps a eliminar
    index_eliminar = []
    
    # Per cada capa del grup de Límits administratius, es busquen els seus camps i el seu índex
    for i, field in enumerate(layer.fields()):
        # Si el nom del camp no es troba a la llista de camps a mantenir:
        # Afegir el seu índex a la llista buida a eliminar
        if field.name() not in camps_mantenir_adreces:
            index_eliminar.append(i)
        else:
            print(f"Camp {field.name()} conservat")

    # Edició de la capa i eliminació del camp i els seus atributs
    with edit(layer):
        layer.deleteAttributes(index_eliminar)

# Comprovació de l'eliminació
for layer in dict_layers["Urbanisme"]['Adreces'].values():
    print(f"Número de camps presents a la capa {layer.name()} després de la neteja: {layer.fields().count()}")
    print(f"Camps presents: {layer.fields().names()}")

## Parcel·les i Illes
# Número de camps
dict_layers["Urbanisme"]['Parcelles'].fields().count()
# Nom dels camps
dict_layers["Urbanisme"]['Parcelles'].fields().names()

# Camps a mantenir
camps_mantenir_parceles_illes = ['PERIMETRE', 'AREA', 'CODI_ILLA', 'CODI_PARC', 'SOLAR', 'REF_CADAST', 'DISTRICTE']
    # 'PERIMETRE'
    # 'AREA'
    # 'CODI_ILLA' codi illa parcel·lària
    # 'CODI_PARC' codi parcel·la
    # 'SOLAR' codi solar
    # 'REF_CADAST' referència cadastral de la parcel·la
    # 'DISTRICTE' codi districte

# Camps a eliminar
for layer in dict_layers["Urbanisme"][1:].values():
    # Clonació de la capa
    layer.clone()

    # Llista buida que contindrà els índex dels camps a eliminar
    index_eliminar = []
    
    # Per cada capa del grup de Límits administratius, es busquen els seus camps i el seu índex
    for i, field in enumerate(layer.fields()):
        # Si el nom del camp no es troba a la llista de camps a mantenir:
        # Afegir el seu índex a la llista buida a eliminar
        if field.name() not in camps_mantenir_parceles_illes:
            index_eliminar.append(i)
        else:
            print(f"Camp {field.name()} conservat")

    # Edició de la capa i eliminació del camp i els seus atributs
    with edit(layer):
        layer.deleteAttributes(index_eliminar)

# Comprovació de l'eliminació
for layer in dict_layers["Urbanisme"][1:].values():
    print(f"Número de camps presents a la capa {layer.name()} després de la neteja: {layer.fields().count()}")
    print(f"Camps presents: {layer.fields().names()}")

# GRAF VIARI
# Número de camps
dict_layers["Graf"]['Graf_trams'].fields().count()
# Nom dels camps
dict_layers["Graf"]['Graf_trams'].fields().names()

# Camps a mantenir
camps_mantenir_grafViari = ['COORD_X', 'COORD_Y', 'LONGITUD', 'ANGLE', 'C_Tram', 'Distric_D', 'NDistric_D', 'TVia_D', 'NVia_D', 'Distric_E', 'NDistric_E', 'TVia_E', 'NVia_E']
    # 'COORD_X' coordenada UTM X
    # 'COORD_Y' coordenada UTM Y
    # 'LONGITUD' longitud de la via
    # 'ANGLE' angle de la via
    # 'C_Tram' codi del tram de via
    # 'Distric_D' codi districte de la part dreta
    # 'NDistric_D' nom districte de la part dreta
    # 'TVia_D' tipus de via de la part dreta
    # 'NVia_D' nom de la via de la part dreta
    # 'Distric_E' codi districte de la part esquerra
    # 'NDistric_E' nom districte de la part esquerra
    # 'TVia_E' tipus de via de la part esquerra
    # 'NVia_E'  nom de la via de la part esquerra

# Camps a eliminar
for layer in dict_layers["Graf"].values():
    layer.clone()

    index_eliminar = []
    
    for i, field in enumerate(layer.fields()):
        if field.name() not in camps_mantenir_grafViari:
            index_eliminar.append(i)
        else:
            print(f"Camp {field.name()} conservat")
    
    with edit(layer):
        layer.deleteAttributes(index_eliminar)

# Comprovació de l'eliminació
for layer in dict_layers["Graf"].values():
    print(f"Número de camps presents a la capa {layer.name()} després de la neteja: {layer.fields().count()}")
    print(f"Camps presents: {layer.fields().names()}")


# Addició de les capes al projecte
# Les capes han estat creades en ordre
for cat in dict_layers.values():
    # Creació d'un grup de capes per cada categoria, si no existeix
    group = root.findGroup(cat)
    if not group:
        group = root.addGroup(cat)
    
    # Addició de la capa al grup
    for layer in group:
        group.addLayer(layer)