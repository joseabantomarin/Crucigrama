#!/usr/bin/env python3
"""
Construye un banco de palabras + pistas cortas a partir del dump de
Wikcionario (kaikki.org/eswiktionary).

Entrada:  data/raw.jsonl.gz
Salida:   data/bank.json  (mapa PALABRA -> pista corta)

Filtros aplicados:
  - lang_code == "es"
  - pos en {noun, adj, verb, adv}
  - palabra de 3 a 10 letras, una sola palabra, sin dígitos
  - se elige la primera glosa cuya versión limpia tenga 4..38 caracteres
  - se descartan glosas con marcas que las hacen malas pistas
    (referencias circulares al lema, "véase", "forma de", etc.)
"""

import gzip
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "raw.jsonl.gz"
OUT = ROOT / "data" / "bank.json"

# Banco curado: glosas cortas y limpias, sólo POS comunes.
WANTED_POS = {"noun", "adj", "verb", "adv"}

# Prefijos académicos / marcas tipográficas que suelen aparecer en
# Wikcionario y que ensucian la pista para crucigrama.
GLOSS_TRIM_PREFIXES = [
    "dicho de una persona:",
    "dicho de una cosa:",
    "dicho de un animal:",
    "dicho de algo:",
    "dicho de alguien:",
]

GLOSS_REJECT_PATTERNS = [
    re.compile(r"^forma\s+(del|de\s+(?:la|el))\b", re.I),
    re.compile(r"^plural\s+de\b", re.I),
    re.compile(r"^femenino\s+de\b", re.I),
    re.compile(r"^masculino\s+de\b", re.I),
    re.compile(r"^diminutivo\s+de\b", re.I),
    re.compile(r"^aumentativo\s+de\b", re.I),
    re.compile(r"^superlativo\s+de\b", re.I),
    re.compile(r"^variante\s+(de|ortográfica|moderna|gráfica)\b", re.I),
    re.compile(r"^variante\s+\w+\s+de\b", re.I),
    re.compile(r"^grafía\s+(alternativa|obsoleta|antigua|moderna|de)\b", re.I),
    re.compile(r"^véase\b", re.I),
    re.compile(r"^sinónimo\s+de\b", re.I),
    re.compile(r"^antiguamente\b", re.I),
    re.compile(r"^obsoleto\b", re.I),
    re.compile(r"^desusado\b", re.I),
    re.compile(r"^arcaísmo\b", re.I),
    re.compile(r"\bvulgar\b", re.I),
    re.compile(r"\bmalsonante\b", re.I),
    re.compile(r"\bobsceno\b", re.I),
    # circulares de conjugación / derivación
    re.compile(r"^gerundio\b", re.I),
    re.compile(r"^participio\b", re.I),
    re.compile(r"^infinitivo\b", re.I),
    re.compile(r"^primera\s+persona\b", re.I),
    re.compile(r"^segunda\s+persona\b", re.I),
    re.compile(r"^tercera\s+persona\b", re.I),
    re.compile(r"^acción\s+(y|o)\s+(efecto|resultado)\s+de\b", re.I),
    re.compile(r"^acción\s+de\b", re.I),
    re.compile(r"^efecto\s+de\b", re.I),
    re.compile(r"^resultado\s+de\b", re.I),
    re.compile(r"^cualidad\s+de\b", re.I),
    re.compile(r"^forma\s+(pronominal|conjugada|impersonal|reflexiva|verbal)\s+de\b", re.I),
    re.compile(r"^forma\s+del\s+verbo\b", re.I),
    re.compile(r"^perteneciente\s+o\s+relativo\s+a\b", re.I),
    re.compile(r"^pre?rteneciente\b", re.I),  # typo común en Wikcionario
    re.compile(r"^relativo\s+a\b", re.I),
    re.compile(r"^relacionado\s+con\b", re.I),
    re.compile(r"^propio\s+de\b", re.I),
    re.compile(r"^lo\s+que\s+es\b", re.I),
    re.compile(r"^conjugación\b", re.I),
    re.compile(r"^apócope\s+de\b", re.I),
    re.compile(r"^acrónimo\s+de\b", re.I),
    re.compile(r"^siglas?\s+de\b", re.I),
    re.compile(r"^por\s+extensión\b", re.I),
    re.compile(r"^en\s+sentido\s+figurado\b", re.I),
]

# Caracteres permitidos en la palabra (mayúsculas)
WORD_OK = re.compile(r"^[A-ZÑ]+$")

MIN_LEN = 2
MAX_LEN = 10
MIN_GLOSS = 3
MAX_GLOSS = 40
MAX_GLOSS_LOOSE = 60  # tolerancia para el banco extra (segunda pasada)


def strip_accents_preserve_n(text: str) -> str:
    text = text.replace("Ñ", "\x01").replace("ñ", "\x02")
    nfd = unicodedata.normalize("NFD", text)
    stripped = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    return stripped.replace("\x01", "Ñ").replace("\x02", "ñ")


def normalize_word(word: str) -> "str | None":
    if not word:
        return None
    w = strip_accents_preserve_n(word).upper()
    if not WORD_OK.match(w):
        return None
    if not (MIN_LEN <= len(w) <= MAX_LEN):
        return None
    # Descartar formas pronominales (terminadas en -SE, -RSE)
    if len(w) > 4 and (w.endswith("RSE") or w.endswith("SE") and w.endswith(("ARSE", "ERSE", "IRSE"))):
        return None
    if len(w) > 5 and w.endswith("RSE"):
        return None
    # Descartar gerundios (-ANDO / -IENDO / -YENDO)
    if len(w) >= 5 and (w.endswith("ANDO") or w.endswith("IENDO") or w.endswith("YENDO")):
        return None
    return w


def clean_gloss(gloss: str, lemma: str, strict: bool = True) -> "str | None":
    g = gloss.strip()
    if not g:
        return None

    # Quitar referencias de marca al principio: "Música. ", "(Biología) ", etc.
    g = re.sub(r"^\([^)]{1,40}\)\s*", "", g)
    g = re.sub(r"^[A-ZÁÉÍÓÚÑa-záéíóúñ]{1,18}\.\s+", "", g)

    low = g.lower()
    for pref in GLOSS_TRIM_PREFIXES:
        if low.startswith(pref):
            g = g[len(pref):].strip()
            low = g.lower()
            break

    if strict:
        for pat in GLOSS_REJECT_PATTERNS:
            if pat.search(g):
                return None
        # La pista no puede contener al lema (ni con/sin acentos)
        lemma_low = strip_accents_preserve_n(lemma).lower()
        if lemma_low and lemma_low in strip_accents_preserve_n(g).lower():
            return None

    # Eliminar referencias entre paréntesis al final
    g = re.sub(r"\s*\([^)]*\)\s*$", "", g).strip()

    # Quitar punto final
    g = g.rstrip(".").strip()

    if not g:
        return None
    max_gloss = MAX_GLOSS if strict else MAX_GLOSS_LOOSE
    if not (MIN_GLOSS <= len(g) <= max_gloss):
        return None
    bad_chars = ("\n", "\r") if not strict else ("\n", "\r", ";", ":")
    if any(ch in g for ch in bad_chars):
        return None
    if g.count("(") != g.count(")"):
        return None

    # Capitalizar inicial
    g = g[0].upper() + g[1:]
    return g


def process():
    bank = {}
    seen_count = 0

    with gzip.open(SRC, "rt", encoding="utf-8") as f:
        for line in f:
            seen_count += 1
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("lang_code") != "es":
                continue
            if e.get("pos") not in WANTED_POS:
                continue
            lemma = e.get("word")
            if not lemma or any(ch.isspace() for ch in lemma) or "-" in lemma:
                continue
            norm = normalize_word(lemma)
            if not norm:
                continue

            best = None
            for s in e.get("senses") or []:
                for raw in s.get("glosses") or []:
                    c = clean_gloss(raw, lemma, strict=True)
                    if c and (best is None or len(c) < len(best)):
                        best = c
            if best is None:
                continue
            existing = bank.get(norm)
            if existing is None or len(best) < len(existing):
                bank[norm] = best

    print(f"lines read   : {seen_count}")
    print(f"final entries: {len(bank)}")

    payload = json.dumps(bank, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    OUT.write_text(payload, encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024 / 1024:.2f} MB)")
    # Variante .js para cargar desde file:// (donde fetch() falla).
    OUT_JS = OUT.with_suffix(".js")
    OUT_JS.write_text(f"window.CRUCIGRAMA_BANK={payload};", encoding="utf-8")
    print(f"wrote {OUT_JS} ({OUT_JS.stat().st_size / 1024 / 1024:.2f} MB)")


if __name__ == "__main__":
    process()
