# Auto Hear

Analizador musical con interfaz gráfica para detectar BPM y tonalidad de archivos de audio.

## Requisitos

- Python 3.8 o superior
- Dependencias de Python listadas en [`requirements.txt`](requirements.txt):
  - `ttkthemes`, `numpy`, `matplotlib`, `librosa`, `scipy`, `soundfile`, `pydub`, `ffmpeg-python`
- Binario `ffmpeg` disponible en el sistema
- Opcional: `madmom` y `essentia` (recomendado instalarlas con `conda-forge` en Windows)

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone <URL>
   cd auto-hear
   ```
2. (Opcional) Crear un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Verificar que `ffmpeg` esté instalado y accesible en la variable `PATH`.

## Ejecución de la interfaz gráfica

Ejecutar:
```bash
python auto_hear.py
```
Se abrirá una ventana donde podrás seleccionar un archivo de audio y obtener el análisis de BPM, tonalidad y segmentos de silencio.

## Ejemplo de salida

Usando un tono sintético de prueba se obtiene una salida similar:
```text
BPM: 0.0
Key: A minor
Duration: 1.0
```

## Problemas frecuentes

- **Faltan dependencias**: verifica que todas las librerías de `requirements.txt` estén instaladas.
- **`ffmpeg` no encontrado**: instala `ffmpeg` y asegúrate de que sea accesible desde la línea de comandos.
- **Errores al importar `tkinter`**: en entornos mínimos puede faltar el paquete `python3-tk`.
- **Análisis lento o fallido**: archivos muy grandes o formatos no soportados pueden generar demoras o errores.

## Ejecutar pruebas

```bash
pytest
```

