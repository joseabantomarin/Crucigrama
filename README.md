# Crucigrama

Generador de crucigramas estilo "sueco" (las pistas van dentro de la grilla con flechas) a partir de una lista de palabras propias y un banco de Wikcionario español.

## Cómo correrlo

```sh
python3 -m http.server 8765
# abrir http://localhost:8765/
```

Funciona también abriendo `index.html` con doble click (`file://`): el banco se carga vía `<script>` tag como fallback cuando `fetch` está bloqueado por el navegador.

## Estructura

- [index.html](index.html) — toda la app (HTML + CSS + JS inline)
- [data/bank.json](data/bank.json) — banco curado de palabras + pistas cortas (~20k entradas, 0.7 MB)
- [data/bank.js](data/bank.js) — misma data envuelta en `window.CRUCIGRAMA_BANK = …` para el fallback `file://`
- [scripts/build_bank.py](scripts/build_bank.py) — script que reconstruye el banco

## Rebuild del banco

```sh
# Bajar el dump de Wikcionario español (~95 MB, una sola vez)
curl -sSL -o data/raw.jsonl.gz https://kaikki.org/eswiktionary/raw-wiktextract-data.jsonl.gz

# Procesar
python3 scripts/build_bank.py
```

## Algoritmo

1. **Layout greedy:** coloca las palabras del usuario primero, cruzándolas entre sí. Prueba decenas de órdenes y se queda con la disposición más densa.
2. **Relleno desde el banco:** barre cada celda vacía dentro del tamaño objetivo y prueba colocar palabras del banco (2 a 10 letras) tanto horizontal como vertical, permitiendo cruzar letras ya colocadas.
3. **Iconos en huecos:** ~35% de las celdas que quedan vacías reciben un icono vectorial (estrella, corazón, flor, sol, etc.) sobre fondo blanco. El resto se pinta gris ("negras" del crucigrama tradicional).
4. **Modos solución / imprimible:** un toggle alterna entre mostrar las letras (solución) o dejarlas en blanco para llenar a lápiz.
