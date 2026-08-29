"""
005 - Slugs por idioma para los blogs (SEO multilingue), igual que servicios.

Anade a `blogs`:  slug_en, slug_es, slug_nl

Sembrado (idempotente, solo rellena lo vacio):
  - slug_en <- slug generado de title_en
  - slug_es <- slug generado de title_es
  - slug_nl <- slug generado de title_nl

IMPORTANTE: la columna `slug` original NO se toca (legacy/redirect/fallback).
Los slugs legacy actuales (DAFT, IP_privacy, ...) siguen funcionando via 301.

NOTA de contenido: hoy los titulos ES/NL de varios articulos son placeholders
de la plantilla (no traducciones reales). Por eso slug_es/slug_nl pueden salir
con texto placeholder; se corrigen en el admin cuando se traduzca el articulo.
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
    if not base:
        base = "post"
    candidate = base
    n = 2
    while candidate in taken:
        candidate = f"{base}-{n}"
        n += 1
    taken.add(candidate)
    return candidate


ADD_COLUMNS = [
    "ALTER TABLE blogs ADD COLUMN IF NOT EXISTS slug_en VARCHAR(255)",
    "ALTER TABLE blogs ADD COLUMN IF NOT EXISTS slug_es VARCHAR(255)",
    "ALTER TABLE blogs ADD COLUMN IF NOT EXISTS slug_nl VARCHAR(255)",
]


def main():
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    with engine.begin() as conn:
        for stmt in ADD_COLUMNS:
            conn.execute(text(stmt))
        print("[005] Columnas slug_en/slug_es/slug_nl listas en blogs.")

        rows = conn.execute(
            text(
                "SELECT id, slug, slug_en, slug_es, slug_nl, "
                "title_en, title_es, title_nl FROM blogs ORDER BY id"
            )
        ).fetchall()

        taken = {"en": set(), "es": set(), "nl": set()}
        for r in rows:
            m = r._mapping
            for lng in ("en", "es", "nl"):
                if m[f"slug_{lng}"]:
                    taken[lng].add(m[f"slug_{lng}"])

        updated = 0
        for r in rows:
            m = r._mapping
            new_vals = {}
            for lng in ("en", "es", "nl"):
                if not m[f"slug_{lng}"]:
                    base = slugify(m[f"title_{lng}"]) or slugify(m["slug"])
                    new_vals[f"slug_{lng}"] = unique_slug(base, taken[lng])
            if new_vals:
                set_clause = ", ".join(f"{k} = :{k}" for k in new_vals)
                new_vals["id"] = m["id"]
                conn.execute(
                    text(f"UPDATE blogs SET {set_clause} WHERE id = :id"), new_vals
                )
                updated += 1

        print(f"[005] Blogs con slugs sembrados: {updated}")
        print("[005] La columna `slug` original se conserva intacta (legacy/redirect).")

        for r in conn.execute(
            text("SELECT id, slug, slug_en, slug_es, slug_nl FROM blogs ORDER BY id")
        ):
            print("  ", dict(r._mapping))


if __name__ == "__main__":
    main()
