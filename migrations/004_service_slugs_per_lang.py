"""
004 - Slugs por idioma para los servicios (SEO multilingue).

Antes `services` tenia una sola columna `slug` (en neerlandes), igual para los 3
idiomas. Para poder tener una URL localizada por idioma, se anaden:

  slug_en, slug_es, slug_nl

Sembrado (idempotente, solo rellena lo que este vacio):
  - slug_nl  <- el `slug` actual (ya esta en neerlandes, sirve tal cual).
  - slug_en  <- slug generado a partir de title_en.
  - slug_es  <- slug generado a partir de title_es.

IMPORTANTE: la columna `slug` original NO se toca. Se conserva como slug legacy
para los redirects 301 y como fallback de resolucion en la API. No se pierde data.
"""
import os
import re
import unicodedata

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


def slugify(value):
    if not value:
        return ""
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def unique_slug(base, taken):
    """Devuelve un slug unico dentro de `taken` (set), anadiendo -2, -3, ..."""
    if not base:
        base = "service"
    candidate = base
    n = 2
    while candidate in taken:
        candidate = f"{base}-{n}"
        n += 1
    taken.add(candidate)
    return candidate


ADD_COLUMNS = [
    "ALTER TABLE services ADD COLUMN IF NOT EXISTS slug_en VARCHAR(255)",
    "ALTER TABLE services ADD COLUMN IF NOT EXISTS slug_es VARCHAR(255)",
    "ALTER TABLE services ADD COLUMN IF NOT EXISTS slug_nl VARCHAR(255)",
]


def main():
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    with engine.begin() as conn:
        for stmt in ADD_COLUMNS:
            conn.execute(text(stmt))
        print("[004] Columnas slug_en/slug_es/slug_nl listas.")

        rows = conn.execute(
            text(
                "SELECT id, slug, slug_en, slug_es, slug_nl, "
                "title_en, title_es, title_nl FROM services ORDER BY id"
            )
        ).fetchall()

        # Conjuntos de slugs ya usados por idioma (para garantizar unicidad).
        taken = {"en": set(), "es": set(), "nl": set()}
        for r in rows:
            m = r._mapping
            if m["slug_en"]:
                taken["en"].add(m["slug_en"])
            if m["slug_es"]:
                taken["es"].add(m["slug_es"])
            if m["slug_nl"]:
                taken["nl"].add(m["slug_nl"])

        updated = 0
        for r in rows:
            m = r._mapping
            new_vals = {}

            if not m["slug_nl"]:
                base = m["slug"] or slugify(m["title_nl"])
                new_vals["slug_nl"] = unique_slug(base, taken["nl"])
            if not m["slug_en"]:
                new_vals["slug_en"] = unique_slug(slugify(m["title_en"]), taken["en"])
            if not m["slug_es"]:
                new_vals["slug_es"] = unique_slug(slugify(m["title_es"]), taken["es"])

            if new_vals:
                set_clause = ", ".join(f"{k} = :{k}" for k in new_vals)
                new_vals["id"] = m["id"]
                conn.execute(
                    text(f"UPDATE services SET {set_clause} WHERE id = :id"), new_vals
                )
                updated += 1

        print(f"[004] Servicios con slugs sembrados: {updated}")
        print("[004] La columna `slug` original se conserva intacta (legacy/redirect).")

        # Resumen
        for r in conn.execute(
            text("SELECT id, slug, slug_en, slug_es, slug_nl FROM services ORDER BY sort_order")
        ):
            print("  ", dict(r._mapping))


if __name__ == "__main__":
    main()
