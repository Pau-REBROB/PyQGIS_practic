# Fluxos descartats

Aquesta carpeta conserva mòduls i anàlisis desenvolupats durant versions anteriors del projecte que actualment no formen part del flux principal d'execució.

El codi es manté com a referència per poder recuperar funcionalitats o aprofitar-ne parts en futures ampliacions. No s'ha d'importar ni executar des de `main.py` sense una revisió prèvia.

## 1. Anàlisi dels usos dels edificis

**Fitxer:** `analisi_usos_zones.py`

### Objectiu

Analitzar la distribució dels usos cadastrals dels edificis per unitat administrativa, obtenint tant els recomptes absoluts com els percentatges de cada ús.

### Funcionalitats

- `agregar_usos_zones()`: compta els edificis de cada ús dins de cada zona, assignant-los mitjançant el centroide i un índex espacial.
- `calcular_percentatges_usos()`: calcula la proporció de cada ús respecte del total d'edificis de la zona.
- `analisi_usos_zones()`: executa les dues operacions i retorna els resultats en un diccionari.

### Dependències

- `config.py`, per obtenir la classificació dels usos cadastrals (`config.USOS`).
- API de PyQGIS, per treballar amb les capes vectorials, les geometries i els índexs espacials.

### Estat

Flux aparcat. Les funcions no s'utilitzen actualment en el procés principal d'anàlisi.

---

## 2. Anàlisi d'accessibilitat

**Fitxer:** `accessibilitat.py`

### Objectiu

Calcular l'accessibilitat territorial a través de la xarxa viària, mitjançant isoàrees de distància o temps, i incorporar-ne els resultats a les capes d'edificis i d'hexàgons.

### Funcionalitats

**Generació d'isoàrees**

- `generar_centroides_clusters()`: genera els centroides de les geometries dels clústers.
- `generar_isoarees()`: calcula les isoàrees sobre el graf viari mitjançant QNEAT3.
- `analisi_accessibilitat()`: executa el flux general de generació d'isoàrees.
- `analisi_accessibilitat_individual()`: calcula les isoàrees de manera independent per a cada clúster.

**Anàlisi i assignació**

- `area_coberta_per_llindar()`: calcula la superfície acumulada coberta per diferents llindars de distància o temps.
- `assignar_isoarees_a_edificis()`: assigna a cada edifici el primer nivell d'accessibilitat que conté el seu centroide.
- `assignar_accessibilitat_per_hexagons()`: agrega els valors d'accessibilitat dels edificis a cada hexàgon mitjançant la mediana.

**Consulta de resultats**

- `distribucio_distancia()`: calcula la distribució dels valors d'accessibilitat per intervals.
- `frequencies()`: mostra per consola les freqüències dels valors d'accessibilitat.

### Dependències

- PyQGIS i PyQt5.
- Processing de QGIS.
- Complement QNEAT3, per al càlcul de les isoàrees.
- `analisi.clusters`, concretament la funció `filtrar_capa()`, per seleccionar els clústers individualment.
- Llibreria estàndard de Python (`statistics`).

### Aspectes pendents de revisió

Abans de recuperar aquest flux, caldria revisar:

- La coherència entre les unitats del graf viari, els llindars i l'estratègia de càlcul (distància o temps).
- La tolerància utilitzada per connectar els punts d'origen a la xarxa viària.
- Els camps necessaris a les capes d'entrada (`CLUSTER_ID`, `cost_level`, `hex_id`, entre d'altres).
- El tractament dels edificis o hexàgons sense valors d'accessibilitat.
- La gestió dels casos sense valors vàlids a `distribucio_distancia()`.
- La vigència de les dependències i la compatibilitat amb la versió actual de QGIS i QNEAT3.

### Estat

Flux aparcat. No forma part del procés principal actual. Es conserva com a referència d'una línia d'anàlisi d'accessibilitat desenvolupada anteriorment.

---
