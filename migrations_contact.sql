-- =============================================
--  Contact feature: contact_page + contact_messages
--  Idempotente: se puede ejecutar varias veces sin romper nada.
-- =============================================

-- Página de contacto editable (un solo registro, id = 1)
CREATE TABLE IF NOT EXISTS contact_page (
    id SERIAL PRIMARY KEY,

    -- Cabecera de página (multi-idioma)
    page_title_en VARCHAR(200), page_title_es VARCHAR(200), page_title_nl VARCHAR(200),
    page_breadcrumb_en VARCHAR(100), page_breadcrumb_es VARCHAR(100), page_breadcrumb_nl VARCHAR(100),
    background_image VARCHAR(500),

    -- Sección de cabecera de la sección de contacto (multi-idioma)
    section_tag_en VARCHAR(150), section_tag_es VARCHAR(150), section_tag_nl VARCHAR(150),
    section_title_en VARCHAR(300), section_title_es VARCHAR(300), section_title_nl VARCHAR(300),
    section_subtitle_en TEXT, section_subtitle_es TEXT, section_subtitle_nl TEXT,

    -- Etiquetas del formulario (multi-idioma)
    form_name_label_en VARCHAR(100), form_name_label_es VARCHAR(100), form_name_label_nl VARCHAR(100),
    form_email_label_en VARCHAR(100), form_email_label_es VARCHAR(100), form_email_label_nl VARCHAR(100),
    form_message_label_en VARCHAR(100), form_message_label_es VARCHAR(100), form_message_label_nl VARCHAR(100),
    form_button_en VARCHAR(100), form_button_es VARCHAR(100), form_button_nl VARCHAR(100),
    form_success_en TEXT, form_success_es TEXT, form_success_nl TEXT,

    -- Datos de contacto (sin idioma)
    email_to VARCHAR(200),        -- destino REAL de los correos del formulario
    email_mailto VARCHAR(200),    -- email mostrado en el botón mailto
    whatsapp_number VARCHAR(50),  -- número internacional sin '+' ni espacios, p.ej. 34123456789
    linkedin_url VARCHAR(500),
    phone VARCHAR(50),
    address_en VARCHAR(300), address_es VARCHAR(300), address_nl VARCHAR(300),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Insertar la fila única con valores por defecto (solo si no existe)
INSERT INTO contact_page (
    id,
    page_title_en, page_title_es, page_title_nl,
    page_breadcrumb_en, page_breadcrumb_es, page_breadcrumb_nl,
    section_tag_en, section_tag_es, section_tag_nl,
    section_title_en, section_title_es, section_title_nl,
    section_subtitle_en, section_subtitle_es, section_subtitle_nl,
    form_name_label_en, form_name_label_es, form_name_label_nl,
    form_email_label_en, form_email_label_es, form_email_label_nl,
    form_message_label_en, form_message_label_es, form_message_label_nl,
    form_button_en, form_button_es, form_button_nl,
    form_success_en, form_success_es, form_success_nl,
    email_to, email_mailto, whatsapp_number, linkedin_url, phone,
    address_en, address_es, address_nl
)
VALUES (
    1,
    'Contact Us', 'Contacto', 'Contact',
    'Contact', 'Contacto', 'Contact',
    'Get In Touch', 'Ponte en contacto', 'Neem contact op',
    'We''d love to hear from you', 'Nos encantaría saber de ti', 'We horen graag van je',
    'Have a project in mind? Send us a message and we will get back to you shortly.',
    '¿Tienes un proyecto en mente? Envíanos un mensaje y te responderemos en breve.',
    'Heb je een project in gedachten? Stuur ons een bericht en we nemen snel contact op.',
    'Your Name', 'Tu Nombre', 'Je Naam',
    'Your Email', 'Tu Email', 'Je E-mail',
    'Your Message', 'Tu Mensaje', 'Je Bericht',
    'Send Message', 'Enviar Mensaje', 'Bericht Versturen',
    'Thank you! Your message has been sent.', '¡Gracias! Tu mensaje ha sido enviado.', 'Bedankt! Je bericht is verzonden.',
    'info@bucareconsultancy.com', 'info@bucareconsultancy.com', '',
    'https://www.linkedin.com/company/75524072/', '',
    '', '', ''
)
ON CONFLICT (id) DO NOTHING;

-- Mensajes recibidos por el formulario de contacto
CREATE TABLE IF NOT EXISTS contact_messages (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
