"""
006 - Metadatos SEO editables: seo_title / seo_description por pagina e idioma,
      y el nombre de marca (site_name) global.

Anade (aditivo, sin borrar nada):
  - A home_page, services_page, about_page, contact_page, blog_page:
        seo_title_en/es/nl, seo_description_en/es/nl
  - A global_content:
        site_name  (una sola columna, sin sufijo de idioma)

Se siembra site_name = 'Bucare Consulting' (editable desde el admin SEO).
Los seo_title/seo_description quedan VACIOS: el frontend usa un fallback
inteligente (titulo de pagina + marca) hasta que se rellenen en el admin.
"""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

PAGE_TABLES = [
    "home_page",
    "services_page",
    "about_page",
    "contact_page",
    "blog_page",
]

LANGS = ["en", "es", "nl"]


def main():
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    with engine.begin() as conn:
        for tbl in PAGE_TABLES:
            for lng in LANGS:
                conn.execute(text(
                    f"ALTER TABLE {tbl} ADD COLUMN IF NOT EXISTS seo_title_{lng} VARCHAR(255)"
                ))
                conn.execute(text(
                    f"ALTER TABLE {tbl} ADD COLUMN IF NOT EXISTS seo_description_{lng} TEXT"
                ))
            print(f"[006] {tbl}: columnas seo_title/seo_description listas.")

        conn.execute(text(
            "ALTER TABLE global_content ADD COLUMN IF NOT EXISTS site_name VARCHAR(255)"
        ))
        # Sembrar marca solo si esta vacia (idempotente)
        conn.execute(text(
            "UPDATE global_content SET site_name = 'Bucare Consulting' "
            "WHERE id = 1 AND (site_name IS NULL OR site_name = '')"
        ))
        current = conn.execute(
            text("SELECT site_name FROM global_content WHERE id = 1")
        ).scalar()
        print(f"[006] global_content.site_name = {current!r}")
        print("[006] Listo (aditivo, sin perdida de datos).")


if __name__ == "__main__":
    main()
