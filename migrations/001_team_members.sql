-- =============================================================
-- 001 - Perfiles de equipo: de fila unica a lista
-- =============================================================
-- Convierte el perfil unico de about_page en una tabla team_members
-- con N filas. NO borra ninguna columna de about_page: los datos
-- originales se quedan ahi como respaldo.
--
-- Idempotente: se puede ejecutar varias veces sin duplicar nada.
-- =============================================================

BEGIN;

CREATE TABLE IF NOT EXISTS team_members (
    id SERIAL PRIMARY KEY,

    -- Perfil
    profile_image VARCHAR(500),
    name VARCHAR(255),
    title_en VARCHAR(255),
    title_es VARCHAR(255),
    title_nl VARCHAR(255),

    -- Contacto
    phone VARCHAR(100),
    email VARCHAR(255),
    experience_en VARCHAR(100),
    experience_es VARCHAR(100),
    experience_nl VARCHAR(100),
    address_en TEXT,
    address_es TEXT,
    address_nl TEXT,

    -- Redes sociales
    social_facebook VARCHAR(500),
    social_twitter VARCHAR(500),
    social_linkedin VARCHAR(500),
    social_pinterest VARCHAR(500),
    social_instagram VARCHAR(500),

    -- Secciones de contenido (por persona)
    about_title_en VARCHAR(255),
    about_title_es VARCHAR(255),
    about_title_nl VARCHAR(255),
    about_content_en TEXT,
    about_content_es TEXT,
    about_content_nl TEXT,

    experience_title_en VARCHAR(255),
    experience_title_es VARCHAR(255),
    experience_title_nl VARCHAR(255),
    experience_content_en TEXT,
    experience_content_es TEXT,
    experience_content_nl TEXT,

    education_title_en VARCHAR(255),
    education_title_es VARCHAR(255),
    education_title_nl VARCHAR(255),
    education_content_en TEXT,
    education_content_es TEXT,
    education_content_nl TEXT,

    achievements_title_en VARCHAR(255),
    achievements_title_es VARCHAR(255),
    achievements_title_nl VARCHAR(255),
    achievements_content_en TEXT,
    achievements_content_es TEXT,
    achievements_content_nl TEXT,

    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_team_members_sort ON team_members (sort_order, id);

-- Migrar el perfil existente de about_page como primer miembro.
-- Solo se ejecuta si team_members esta vacia (guard de idempotencia).
INSERT INTO team_members (
    profile_image, name,
    title_en, title_es, title_nl,
    phone, email,
    experience_en, experience_es, experience_nl,
    address_en, address_es, address_nl,
    social_facebook, social_twitter, social_linkedin, social_pinterest, social_instagram,
    about_title_en, about_title_es, about_title_nl,
    about_content_en, about_content_es, about_content_nl,
    experience_title_en, experience_title_es, experience_title_nl,
    experience_content_en, experience_content_es, experience_content_nl,
    education_title_en, education_title_es, education_title_nl,
    education_content_en, education_content_es, education_content_nl,
    achievements_title_en, achievements_title_es, achievements_title_nl,
    achievements_content_en, achievements_content_es, achievements_content_nl,
    sort_order
)
SELECT
    profile_image, name,
    title_en, title_es, title_nl,
    phone, email,
    experience_en, experience_es, experience_nl,
    address_en, address_es, address_nl,
    social_facebook, social_twitter, social_linkedin, social_pinterest, social_instagram,
    about_title_en, about_title_es, about_title_nl,
    about_content_en, about_content_es, about_content_nl,
    experience_title_en, experience_title_es, experience_title_nl,
    experience_content_en, experience_content_es, experience_content_nl,
    education_title_en, education_title_es, education_title_nl,
    education_content_en, education_content_es, education_content_nl,
    achievements_title_en, achievements_title_es, achievements_title_nl,
    achievements_content_en, achievements_content_es, achievements_content_nl,
    1
FROM about_page
WHERE id = 1
  AND NOT EXISTS (SELECT 1 FROM team_members);

COMMIT;
