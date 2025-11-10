# Sequías Históricas LLM
Evaluación de modelos LLM para la extracción de impactos climáticos en noticias históricas

Forma parte del Trabajo Fin de Estudios del Máster Universitario en Inteligencia Artificial de Daniel Vilas Perulan.

En este TFE se utiliza [CienaLLM](https://github.com/lcsc/ciena_llm) como herramienta para invocar los LLM y así extraer información de los impactos recogidos en las noticias históricas.

Se cuenta con una base de datos de noticias históricas y con el etiquetado manual de algunas de ellas. Pero no están en un formato entendible por CienaLLM ni procesable.

En este repositorio se encuentra el código para procesar las noticias, scripts para invocar CienaLLM con los parámetros necesarios y código para evaluar los resultados.

En la carpeta [fuente](src/sequias_historicas) se encuentra el código necesario y en la carpeta raíz los scripts que lanzan de forma automática los diferentes pasos necesarios para la evaluación de los modelos

## Instalación inicial

Ejecutar los siguientes comandos en un shell bash

```bash
git clone https://github.com/danielvilas/SequiasHistoricasLLM
cd SequiasHistoricasLLM
python3 -m venv --upgrade-deps .venv
. .venv/bin/activate
pip install poetry
poetry install
pip install -e . 
```
Se incluye la configuración de un DevContainer si se desea usar VS Code.

Una vez instalado, asegurarse que en la ruta `/media/data/news/pdf/` hay dos carpetas con los datos de:
| carpeta | ruta datos |
|-|-|
|`/media/data/news-historicas/raw/extremadura`|`g:/d.l/n/p/dv/news-historicas/raw/extremadura`|
|`/media/data/news-historicas/raw/hoy`|`g:/d.l/n/p/dv/news-historicas/raw/hoy`|
|`/media/data/news-historicas/clean`|`g:/d.l/n/p/dv/news-historicas/clean/`|

Ya sea copiandolos o montando la carpeta remota.

Los enlazaremos al data local
```bash
ln -s /media/data/news-historicas/raw/ ./data/datasets/raw
ln -s /media/data/news-historicas/clean/ ./data/datasets/clean
```


> La ruta ha sido codificada por privacidad, pero identificable si se tiene acceso.