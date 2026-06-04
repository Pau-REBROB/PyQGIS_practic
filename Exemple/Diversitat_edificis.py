# DIVERSITAT D'EDIFICIS PER DISTRICTE - ÍNDEX DE SHANNON

# Cal conèixer la proporció de cada ús

# Sobre la capa d'edificis, crear els camps:
## Número d'edificis
## Índex de Shannon (H)
## Ús dominant

# Còpia capa de districtes
districtes = dict_layers["Districtes"].materialize(QgsFeatureRequest())
edificis = dict_layers["Edificis"].materialize(QgsFeatureRequest())


# Afegir camps nous
provider = districtes.dataProvider()

provider.addAttributes([
    QgsField("Num_Edificis", QVariant.Int),
    QgsField("H_Shannon", QVariant.Double),
    QgsField("Us_Dominant", QVariant.String)
])

districtes.updateFields()


# Índex dels edificis 
index_edificis = dict_indexs["Edificis"]


# Edició de la capa de districtes per omplir els nous camps
districtes.startEditing()

for feat in districtes.getFeatures():
    geom_d = feat.geometry()
    
    # Índex dels edificis que es troben al bbox cada districte
    ids = index_edificis.intersects(geom_d.boundingBox())

    # Filtratge de falsos positius d'edificis
    # La bbox engloba més enllà dels límits administratius
    # Recompte d'usos i edificis per cada districte
    comptador_usos = {}
    total_edificis = 0
    for id in ids:
        # Recuperar feature de cada edifici dins la bbox del districte
        feat_e = edificis.getFeature(id)

        # Filtratge segons si el centroide cau dins la geometria del districte
        # Si la geom del districte no conté el centroide, seguir la iteració
        if not geom_d.contains(feat_e.geometry().centroid()):
            continue
        # Si el centroide cau dins, recuperar el seu ús
        us = feat_e["currentUse"]
        # Afegir l'ús al diccionari de comptador d'usos
        if us in comptador_usos:
            comptador_usos[us] += 1
        else:
            comptador_usos[us] = 1
        # Comptabilitzar l'edifici
        total_edificis += 1


    # Càlcul índex Shannon
    import math

    # Índex
    H = 0

    # Per cada ús dels edificis - pel seu recompte
    for n in comptador_usos.values():
        # Càlcul proporció
        p = n / total_edificis
           
        # Càlcul índex
        H -= p * math.log(p)

    
    # Ús dominant
    us_dominant = max(comptador_usos, key=comptador_usos.get)

    # Actualització dels nous camps
    feat["Num_Edificis"] = total_edificis
    feat["H_Shannon"] = round(H,3)
    feat["Us_Dominant"] = us_dominant

    districtes.updateFeature(feat)

districtes.commitChanges()

#==============================

# DIVERSITAT D'EDIFICIS PER BARRI - ÍNDEX DE SHANNON

# Cal conèixer la proporció de cada ús

# Sobre la capa d'edificis, crear els camps:
## Número d'edificis
## Índex de Shannon (H)
## Ús dominant

# Còpia capa de barris
barris = dict_layers["Barris"].materialize(QgsFeatureRequest())

# Afegir camps nous
provider = barris.dataProvider()

provider.addAttributes([
    QgsField("Num_Edificis", QVariant.Int),
    QgsField("H_Shannon", QVariant.Double),
    QgsField("Us_Dominant", QVariant.String)
])

barris.updateFields()


# Índex dels edificis 
index_edificis = dict_indexs["Edificis"]


# Edició de la capa de districtes per omplir els nous camps
barris.startEditing()

for feat in barris.getFeatures():
    geom_b = feat.geometry()
    
    # Índex dels edificis que es troben al bbox cada districte
    ids = index_edificis.intersects(geom_b.boundingBox())

    # Filtratge de falsos positius d'edificis
    # La bbox engloba més enllà dels límits administratius
    # Recompte d'usos i edificis per cada districte
    comptador_usos = {}
    total_edificis = 0
    for eid in ids:
        # Recuperar feature de cada edifici dins la bbox del districte
        feat_e = edificis.getFeature(eid)

        # Filtratge segons si el centroide cau dins la geometria del districte
        # Si la geom del districte no conté el centroide, seguir la iteració
        if not geom_b.contains(feat_e.geometry().centroid()):
            continue
        # Si el centroide cau dins, recuperar el seu ús
        us = feat_e["currentUse"]
        # Afegir l'ús al diccionari de comptador d'usos
        if us in comptador_usos:
            comptador_usos[us] += 1
        else:
            comptador_usos[us] = 1
        # Comptabilitzar l'edifici
        total_edificis += 1


    # Càlcul índex Shannon
    import math

    # Índex
    H = 0

    # Per cada ús dels edificis - pel seu recompte
    for n in comptador_usos.values():
        # Càlcul proporció
        p = n / total_edificis
           
        # Càlcul índex
        H -= p * math.log(p)

    
    # Ús dominant
    us_dominant = max(comptador_usos, key=comptador_usos.get)

    # Actualització dels nous camps
    feat["Num_Edificis"] = total_edificis
    feat["H_Shannon"] = round(H,3)
    feat["Us_Dominant"] = us_dominant

    barris.updateFeature(feat)

barris.commitChanges()
