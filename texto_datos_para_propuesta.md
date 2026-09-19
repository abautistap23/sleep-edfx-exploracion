## Exploración y descripción de los datos

Se realizó una exploración reproducible de Sleep-EDF Expanded (Sleep-EDFx), disponible en PhysioNet, mediante un notebook en Python. Se identificaron 394 archivos EDF, organizados en 197 parejas PSG–hipnograma, correspondientes a 100 sujetos. Sleep Cassette (SC) aporta 306 archivos, equivalentes a 153 registros de 78 sujetos, y Sleep Telemetry (ST) aporta 88 archivos, equivalentes a 44 registros de 22 sujetos. Cada registro comprende un archivo PSG con las señales fisiológicas y un hipnograma con las anotaciones de los estadios del sueño. La integridad de los 394 archivos EDF se verificó mediante comparación SHA-256 con el manifiesto distribuido con la base.

Los dos canales EEG (Fpz-Cz y Pz-Oz) y el EOG horizontal están presentes en todos los registros y tienen una frecuencia de muestreo de 100 Hz. Por tanto, una época de 30 segundos contiene 3.000 muestras por canal EEG. El EMG submental presenta diferencias entre estudios: 1 Hz en SC y 100 Hz en ST. En SC corresponde a una envolvente de actividad muscular; por ello, su incorporación requerirá un tratamiento específico y no se asumirá equivalencia directa con el EMG de ST.

Las anotaciones originales siguen la nomenclatura de Rechtschaffen y Kales. Para el análisis se mapearon los estadios 1 y 2 a N1 y N2, se agruparon 3 y 4 como N3 y se convirtió R en REM, conservando W, M y ?. Esta agrupación no constituye una nueva estadificación bajo criterios AASM.

Se contabilizaron 461.870 ventanas completas de 30 segundos dentro de las señales. De ellas, 459.198 cuentan con una anotación válida que cubre toda la ventana; las 2.672 restantes (0,58 %) carecen de cobertura del hipnograma y pertenecen a ST. Estas ventanas se excluyen del conjunto supervisado y se distinguen de las 1.335 épocas etiquetadas explícitamente como ?. La distribución de las épocas anotadas, antes de recortar vigilia o aplicar otros filtros, fue:

| Clase | Número de épocas | Porcentaje |
|---|---:|---:|
| W | 289.856 | 63,122 % |
| N1 | 25.175 | 5,482 % |
| N2 | 88.983 | 19,378 % |
| N3 | 19.454 | 4,237 % |
| REM | 34.184 | 7,444 % |
| M | 211 | 0,046 % |
| ? | 1.335 | 0,291 % |
| **Total** | **459.198** | **100,000 %** |

Se observó un desbalance marcado: W concentra el 63,12 % de las épocas y M representa apenas el 0,046 %. La proporción de vigilia también difiere entre estudios: 68,54 % en SC y 10,34 % en ST. Estas cifras describen los registros completos y no deben interpretarse como la distribución de una noche de sueño previamente delimitada. Se evaluará una regla explícita de recorte de vigilia y se documentará su efecto sobre el tamaño y la distribución del conjunto utilizado para modelar.

Durante la lectura se detectaron siete hipnogramas con discrepancias entre la fecha textual del campo de identificación del registro y su fecha fija de cabecera. Se resolvió la incompatibilidad de lectura utilizando la fecha y hora fijas, que coinciden con las del PSG correspondiente, y se conservaron los archivos originales. Así fue posible procesar los 197 registros. La exploración verificó estructura, canales, integridad y cobertura de etiquetas; aún no comprende una evaluación sistemática de artefactos o calidad de las señales.

De acuerdo con el alcance de IBIO, se conservarán las cinco clases principales y la clase adicional M, excluyendo ? del conjunto supervisado. Esto deja 457.863 épocas candidatas, antes de otros criterios de preparación. Las particiones de entrenamiento, validación y prueba se realizarán por sujeto. Se reportarán F1 macro y métricas por clase, y cualquier estrategia de balanceo se aplicará exclusivamente al entrenamiento. La escasa representación de M deberá considerarse en la evaluación y en la interpretación de los resultados.

Fuente de la base y sus características: [PhysioNet, Sleep-EDF Expanded](https://physionet.org/content/sleep-edfx/1.0.0/). Los conteos y porcentajes corresponden a la exploración local revisada.
