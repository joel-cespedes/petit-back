"""
007 - Dos anadidos (aditivo, sin borrar nada):

  1) contact_page.cal_url  (TEXT, sin sufijo de idioma)
        Enlace de reserva (Cal.com) que se muestra como CTA en /contact.
        Se siembra con la URL del cliente si esta vacia; editable desde el admin.

  2) partner_images.alt_text  (TEXT NOT NULL DEFAULT '')
        Texto alternativo por logo del carrusel "Our Partner Network"
        (accesibilidad + SEO). Editable desde el admin del carrusel.
"""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

CAL_URL = "https://cal.com/eduardo-petit-kuuyoi/30min"


def main():
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    with engine.begin() as conn:
        # 1) contact_page.cal_url
        conn.execute(text(
            "ALTER TABLE contact_page ADD COLUMN IF NOT EXISTS cal_url TEXT"
        ))
        conn.execute(
            text(
                "UPDATE contact_page SET cal_url = :url "
                "WHERE id = 1 AND (cal_url IS NULL OR cal_url = '')"
            ),
            {"url": CAL_URL},
        )
        current = conn.execute(
            text("SELECT cal_url FROM contact_page WHERE id = 1")
        ).scalar()
        print(f"[007] contact_page.cal_url = {current!r}")

        # 2) partner_images.alt_text
        conn.execute(text(
            "ALTER TABLE partner_images "
            "ADD COLUMN IF NOT EXISTS alt_text TEXT NOT NULL DEFAULT ''"
        ))
        print("[007] partner_images.alt_text listo.")
        print("[007] Listo (aditivo, sin perdida de datos).")


if __name__ == "__main__":
    main()
