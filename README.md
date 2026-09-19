# Exploración revisada de Sleep-EDFx

Abre `01_exploracion_sleep_edfx.ipynb` y selecciona el entorno local `.venv` o el kernel Python (Sleep-EDFx). El notebook está guardado con todas las celdas ejecutadas y las conclusiones verificadas.

- Texto para la propuesta: `texto_datos_para_propuesta.md`.
- Resultados vigentes: `outputs/notebook/` (197 registros, 100 sujetos).
- Copia previa: `backups/revision_2026-09-19/`.
- El script inicial `exploracion_sleep_edfx.py` y las salidas de `outputs/` fuera de `notebook/` son anteriores a esta revisión: usa el notebook para obtener las cifras actualizadas.

La lectura corregida conserva los EDF originales. La comprobación SHA-256 lee los 394 EDF por bloques y no descarga datos. La exportación reemplaza CSV, JSON y Excel en `outputs/notebook/`. Ejecuta con la descarga terminada.

Para abrir con Jupyter desde esta carpeta:

```bash
.venv/bin/jupyter lab 01_exploracion_sleep_edfx.ipynb
```

El notebook utiliza las rutas relativas al directorio de trabajo que define `PROJECT_DIR` en la primera celda. Las dependencias exactas están en `requirements-lock.txt`.
