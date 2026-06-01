# Posada en pràctica

Scripts on es posa en pràctica la teoria exposada amb dades reals de Barcelona

Els scripts es separen també per temàtica

## 0_Inicialització
Creació d'instàncies del projecte (*project*) i el panell de capes (*root*)

Importació de les diferents capes

Comprovació dels sistemes de referència

## 1_Preparació de les dades
Inspecció dels camps presents a les dades

Clonació de les capes i eliminació dels camps innecessaris

Addició de les capes al canvas

## Simbologia única
Creació de funcions de simbologia única per a elements poligonals i lineals, aptes per a ser usades com a mòduls

Test de les funcions amb dades de Barcelona, només executable en el propi script. Creació de simbologia única per a les unitats administratives, el graf viari i elements del cadastre

## Simbologia categòrica
Creació de funcions de simbologia categòrica per a elements poligonals, apta per a ser usada com a mòdul

Test de la funció amb dades de Barcelona, només executable en el propi script. Creació de simbologia categòrica per als barris i districtes

## Simbologia graduada
Creació de funcions de simbologia graduada utilitzant els mètodes de classificació propis de QGIS per a elements poligonals, apta per a ser usada com a mòdul

Test de la funció amb dades de Barcelona, només executable en el propi script. Creació de simbologia graduada per l'àrea dels barris i districtes, així com el nombre de pisos dels edificis

## Simbologia graduada manual
Creació de funcions de simbologia graduada creant manualment els rangs de dades per a elements poligonals, apta per a ser usada com a mòdul

Test de la funció amb dades de Barcelona, només executable en el propi script. Creació de simbologia graduada pel nombre de pisos dels edificis

## Simbologia basada en regles
Creació de cartografia dels barris basada en regles: àrea més petita i àrea més gran


## Ús edificis
Script individual que inicialitza QGIS, importa les dades i les funcions anteriors com a mòduls per a generar una composició

S'utilitza la funció de simbologia única per generar una base cartogràfica de referència dels barris i districtes, juntament amb un mapa base de fons en format WMS CartoDB Dark

S'utilitza la funció de simbologia categòrica per a representar els edificis en funció del seu ús

Es genera un atles, amb un full per districte
