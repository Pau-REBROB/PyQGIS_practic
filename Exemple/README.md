### Execució del projecte

El projecte està dissenyat per executar-se des de la consola Python de QGIS.

Per iniciar l'anàlisi:

1. Obriu QGIS i accediu a la consola Python.
2. Obriu el fitxer `Exemple/main.py` des de l'editor de scripts de la consola.
3. Executeu el fitxer des de l'editor.

**Important:** no s'ha de copiar i enganxar el contingut de `main.py` directament a la consola Python. El projecte utilitza la variable `__file__` per identificar automàticament la ubicació dels scripts i construir les rutes relatives. Aquesta variable està disponible quan s'executa el fitxer com a script, però no necessàriament quan se n'enganxa el contingut a la consola.

Cal executar el projecte en un entorn QGIS amb les dependències necessàries disponibles.

### Configuració de les dades

El projecte utilitza dades externes que no s'inclouen al repositori.

Per executar-lo, cal disposar de la carpeta `Dades` amb l'estructura de directoris esperada pel projecte.

La ubicació de les dades es configura mitjançant el fitxer `Exemple/config_local.py`:

1. Copieu el fitxer `Exemple/config_local.example.py` i anomeneu la còpia `config_local.py`.
2. Editeu el valor de `PATH_DADES` perquè apunti a la ubicació de la vostra carpeta `Dades`.
3. Deseu el fitxer.

Per exemple:

```python
from pathlib import Path

PATH_DADES = Path(r"D:/GIS/Dades")
```

Si no es crea aquest fitxer, el projecte assumeix que la carpeta `Dades` es troba al mateix nivell que el repositori.

El fitxer `config_local.py` és personal i està exclòs del control de versions mitjançant `.gitignore`.
