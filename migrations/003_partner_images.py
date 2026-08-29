"""
003 - Convertir la imagen unica de la seccion "Partner Network" (home) en un
carrusel de varias imagenes.

Antes la home tenia una sola columna `home_page.partner_image`. Ahora las
imagenes del carrusel viven en su propia tabla `partner_images` (id, image_url,
sort_order), consultada por /api/home y editable desde el admin.

Que hace, de forma idempotente:
  1. Crea la tabla `partner_images` si no existe.
  2. Si la tabla esta vacia y `home_page.partner_image` tiene valor, migra esa
     imagen como el primer item del carrusel (para no perder la data subida).

IMPORTANTE: NO borra la columna `home_page.partner_image`. Se deja intacta como
respaldo y fallback. La data existente no se pierde.
"""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS partner_images (
    id SERIAL PRIMARY KEY,
    image_url TEXT NOT NULL DEFAULT '',
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


def main():
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    with engine.begin() as conn:
        # 1. Crear tabla
        conn.execute(text(CREATE_TABLE))
        print("[003] Tabla partner_images lista.")

        # 2. Migrar la imagen actual solo si el carrusel esta vacio
        count = conn.execute(text("SELECT COUNT(*) FROM partner_images")).scalar()
        if count and count > 0:
            print(f"[003] partner_images ya tiene {count} fila(s); no se migra nada.")
            return

        current = conn.execute(
            text("SELECT partner_image FROM home_page WHERE id = 1")
        ).scalar()

        if current and current.strip():
            conn.execute(
                text(
                    "INSERT INTO partner_images (image_url, sort_order) "
                    "VALUES (:url, 1)"
                ),
                {"url": current},
            )
            print(f"[003] Migrada imagen existente al carrusel: {current}")
        else:
            print("[003] home_page.partner_image esta vacio; nada que migrar.")

        print("[003] home_page.partner_image se conserva intacta (backup/fallback).")


if __name__ == "__main__":
    main()
