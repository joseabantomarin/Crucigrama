# Naming — Pista

**Fecha:** 2026-05-21
**Estado:** propuesta para aprobación

## Decisión

- **Nombre del producto:** `Pista`
- **Tagline:** `Crucigramas en español`
- **Pestaña / `<title>`:** `Pista — Crucigramas en español`
- **Repo / dominio interno:** mantiene `Crucigrama` por ahora (el nombre del repo no afecta la UI).

## Por qué Pista

1. **Significado literal directo.** El crucigrama *da* pistas; cada celda gris pintada con la flecha le dice al jugador "acá viene una pista". La marca no estira ninguna metáfora — es exactamente lo que el producto hace.
2. **Fonética firme.** Dos sílabas, consonantes claras (p, s, t), ningún sonido ambiguo. Se lee igual en cualquier variante del español.
3. **Tono ingenioso sin esfuerzo.** "Pista" carga la idea de descubrir / deducir sin necesidad de tipografía o ilustración para vender personalidad. La palabra ya la trae.
4. **Doble lectura útil.** Pista del crucigrama + pista (rastro, sendero) — refuerza la idea de "ir siguiendo algo hasta encontrar la respuesta".
5. **Encaja con el lenguaje gráfico actual.** Las flechas → y ↓ son el código visual del estilo sueco y ya están omnipresentes en la grilla. La letra `i` o la `t` del logo pueden adoptar la flecha sin romper la consistencia.

## Por qué no las otras opciones

- **Trama** — buena pero el verbo asociado es "tejer", no "resolver". Mejor para revista literaria que para generador de crucigramas.
- **Indicio** — más largo (7 letras, 4 sílabas), pierde la inmediatez. Sirve si quisiéramos un giro detectivesco, pero el producto no es ese.
- **Hilo** — métafora suave pero ambigua con "hilo de chat / hilo de discusión", confunde en contexto digital.
- **Marcas inventadas (Cruxia, Letrida, Verbax)** — más brandables pero requieren explicación. El usuario tipo de este producto (adulto que resuelve crucigramas) recompensa la claridad antes que la originalidad.

## Implicancias visuales (para el siguiente paso, no parte de este spec)

- El logo debería explotar la integración natural con las flechas existentes en la grilla. Opciones a explorar cuando se diseñe la maquetación:
  - `i` reemplazada por una flecha vertical (↓)
  - `t` cuyo travesaño actúa como una flecha horizontal (→)
  - Un mini-bloque tipo celda de crucigrama detrás de una letra
- Paleta: mantener el azul existente (#1f6feb de las flechas) como acento principal.
- Tipografía: pendiente de definir en el spec de UI.

## Alcance

Este spec cubre **únicamente la decisión de nombre y tagline**. Quedan fuera:
- El diseño del logo (siguiente brainstorm).
- La maquetación de la página (siguiente brainstorm).
- Cualquier registro de dominio o marca legal.

## Cambios concretos al aprobarse

1. Actualizar `<title>` en [index.html](../../../index.html) → `Pista — Crucigramas en español`
2. Actualizar `<h1>` y subtítulo del header → `Pista` / `Crucigramas en español`
3. README: agregar `# Pista` como nombre antes del `# Crucigrama` actual (o reemplazar).

Estos cambios son menores y se aplicarían como parte del primer paso de la maquetación general, no como tarea suelta.
