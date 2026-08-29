import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Railway uses postgres:// but SQLAlchemy needs postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Check connection before using
    pool_recycle=300,    # Recycle connections every 5 minutes
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_page_content(db, table_name: str, lang: str):
    """
    Get content from a static page table and return only the specified language.
    Removes the language suffix from column names.
    """
    query = text(f"SELECT * FROM {table_name} WHERE id = 1")
    result = db.execute(query).fetchone()

    if not result:
        return {}

    # Convert to dict and filter by language
    columns = result._mapping.keys()
    filtered = {}

    for col in columns:
        value = result._mapping[col]

        # Skip id and timestamps
        if col in ['id', 'created_at', 'updated_at']:
            continue

        # If column ends with language suffix, check if it matches
        if col.endswith(f'_{lang}'):
            # Remove the language suffix for the response
            clean_key = col[:-3]  # Remove '_en', '_es', '_nl'
            filtered[clean_key] = value
        elif not col.endswith('_en') and not col.endswith('_es') and not col.endswith('_nl'):
            # Column without language suffix (like phone, email, image_url)
            filtered[col] = value

    return filtered


def get_dynamic_content(db, table_name: str, lang: str, where_clause: str = None, order_by: str = None):
    """
    Get content from a dynamic table (services, blogs) with language filtering.
    """
    query = f"SELECT * FROM {table_name}"
    if where_clause:
        query += f" WHERE {where_clause}"
    if order_by:
        query += f" ORDER BY {order_by}"

    result = db.execute(text(query)).fetchall()

    items = []
    for row in result:
        columns = row._mapping.keys()
        filtered = {}

        for col in columns:
            value = row._mapping[col]

            if col in ['created_at', 'updated_at']:
                continue

            if col.endswith(f'_{lang}'):
                clean_key = col[:-3]
                filtered[clean_key] = value
            elif not col.endswith('_en') and not col.endswith('_es') and not col.endswith('_nl'):
                filtered[col] = value

        items.append(filtered)

    return items


def get_single_item(db, table_name: str, lang: str, slug: str):
    """
    Get a single item by slug with language filtering.
    """
    query = text(f"SELECT * FROM {table_name} WHERE slug = :slug")
    result = db.execute(query, {"slug": slug}).fetchone()

    if not result:
        return None

    columns = result._mapping.keys()
    filtered = {}

    for col in columns:
        value = result._mapping[col]

        if col in ['created_at', 'updated_at']:
            continue

        if col.endswith(f'_{lang}'):
            clean_key = col[:-3]
            filtered[clean_key] = value
        elif not col.endswith('_en') and not col.endswith('_es') and not col.endswith('_nl'):
            filtered[col] = value

    return filtered

def _filter_row_lang(mapping, lang):
    """Filtra una fila a un solo idioma (quita sufijos _en/_es/_nl)."""
    data = {}
    for col in mapping.keys():
        if col in ('created_at', 'updated_at'):
            continue
        if col.endswith('_en') or col.endswith('_es') or col.endswith('_nl'):
            continue
        data[col] = mapping[col]
    for col in mapping.keys():
        if col.endswith(f'_{lang}'):
            data[col[:-3]] = mapping[col]
    return data


def _attach_service_slugs(mapping, data, lang):
    """Adjunta el mapa de slugs por idioma y el slug canonico del idioma actual."""
    slug_map = {
        'en': mapping['slug_en'] or mapping['slug'],
        'es': mapping['slug_es'] or mapping['slug'],
        'nl': mapping['slug_nl'] or mapping['slug'],
    }
    data['slugs'] = slug_map
    data['slug'] = slug_map.get(lang) or mapping['slug']
    data['slug_legacy'] = mapping['slug']
    return data


def get_services_list(db, lang, published_only=False):
    """Lista de servicios en un idioma, incluyendo el mapa de slugs por idioma."""
    query = "SELECT * FROM services"
    if published_only:
        query += " WHERE is_published = true"
    query += " ORDER BY sort_order"
    rows = db.execute(text(query)).fetchall()
    items = []
    for row in rows:
        m = row._mapping
        data = _filter_row_lang(m, lang)
        _attach_service_slugs(m, data, lang)
        items.append(data)
    return items


def get_service_by_slug(db, lang, slug):
    """Resuelve un servicio por el slug de cualquier idioma o el slug legacy."""
    query = text(
        "SELECT * FROM services WHERE slug_en = :s OR slug_es = :s "
        "OR slug_nl = :s OR slug = :s LIMIT 1"
    )
    row = db.execute(query, {"s": slug}).fetchone()
    if not row:
        return None
    m = row._mapping
    data = _filter_row_lang(m, lang)
    _attach_service_slugs(m, data, lang)
    return data

def get_blog_by_slug(db, lang, slug):
    """Resuelve un blog por el slug de cualquier idioma o el slug legacy."""
    query = text(
        "SELECT * FROM blogs WHERE slug_en = :s OR slug_es = :s "
        "OR slug_nl = :s OR slug = :s LIMIT 1"
    )
    row = db.execute(query, {"s": slug}).fetchone()
    if not row:
        return None
    m = row._mapping
    data = _filter_row_lang(m, lang)
    _attach_service_slugs(m, data, lang)
    return data
