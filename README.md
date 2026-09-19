# Exploración revisada de Sleep-EDFx

Este repositorio contiene el notebook y los archivos utilizados para explorar la base Sleep-EDF Expanded (Sleep-EDFx).

El repositorio no incluye el entorno virtual `.venv`, el kernel de Jupyter, los archivos EDF del dataset ni los archivos de salida generados localmente. Cada integrante debe crear su propio entorno virtual e instalar las dependencias después de clonar el repositorio.

## Contenido

- `01_exploracion_sleep_edfx.ipynb`: notebook principal de exploración.
- `texto_datos_para_propuesta.md`: texto utilizado para la propuesta.
- `requirements.txt`: dependencias necesarias.
- `requirements-lock.txt`: versiones instaladas en el entorno original.
- `exploracion_sleep_edfx.py`: versión inicial de la exploración.
- `data/sleep-edfx/`: carpeta local donde debe colocarse el dataset.

## Configuración local

Después de clonar el repositorio, entra en su carpeta:

```bash
cd sleep-edfx-exploracion
```

Crea un entorno virtual local:

```bash
python3 -m venv .venv
```

Instala las dependencias:

```bash
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

El entorno `.venv` se crea únicamente en el computador de cada integrante y no se comparte mediante Git.

## Registrar el kernel del notebook

Para que el entorno aparezca como opción en Jupyter o VS Code, registra el kernel local:

```bash
.venv/bin/python -m ipykernel install --user \
  --name sleep-edfx \
  --display-name "Python (Sleep-EDFx)"
```

Después, al abrir el notebook, selecciona el kernel `Python (Sleep-EDFx)`. Este kernel también es local y cada integrante debe registrarlo en su propio computador.

## Descargar los datos

Descarga Sleep-EDFx desde PhysioNet:

<https://physionet.org/content/sleep-edfx/1.0.0/>

Coloca los archivos dentro de:

```text
data/sleep-edfx/
```

La estructura esperada es:

```text
data/sleep-edfx/
├── sleep-cassette/
├── sleep-telemetry/
├── SHA256SUMS.txt
├── SC-subjects.xls
└── ST-subjects.xls
```

También se puede utilizar la copia oficial de Amazon S3:

```bash
aws s3 sync --no-sign-request \
  s3://physionet-open/sleep-edfx/1.0.0/ \
  data/sleep-edfx/
```

El dataset no está incluido en este repositorio y cada integrante debe descargarlo localmente.

## Abrir el notebook

Desde la carpeta raíz del repositorio:

```bash
.venv/bin/jupyter lab 01_exploracion_sleep_edfx.ipynb
```

También se puede abrir el archivo desde VS Code y seleccionar el kernel `Python (Sleep-EDFx)`.

Ejecuta las celdas en orden. El notebook utiliza la ruta relativa `data/sleep-edfx/`, por lo que es importante abrirlo desde la carpeta raíz del repositorio.

## Resultados

El notebook explora:

- Registros PSG e hipnogramas.
- Sujetos y subconjuntos SC/ST.
- Canales disponibles.
- Frecuencias de muestreo.
- Épocas de 30 segundos.
- Distribución de las clases W, N1, N2, N3, REM, M y Sin clasificar.
- Posibles desafíos de calidad y desbalance.
- Integridad de los archivos mediante SHA-256.

La exploración identificó 394 archivos EDF organizados en 197 parejas PSG–hipnograma y correspondientes a 100 sujetos.

Los resultados se generan localmente en `outputs/notebook/`. Esos archivos pueden regenerarse ejecutando el notebook y no se suben al repositorio.
