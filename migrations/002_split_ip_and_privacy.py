"""
002 - Separar "IP & Privacy Policies" en dos servicios independientes.

El servicio `privacy-policy` mezclaba propiedad intelectual y privacidad/RGPD
en un solo slug, lo que diluye la relevancia tematica de ambos. Queda asi:

  privacy-policy        -> solo privacidad / RGPD
  intellectual-property -> solo propiedad intelectual (servicio nuevo)

De paso corrige dos errores que ya arrastraba el registro original:
  - El contenido NL era el de `establish-company` (tema equivocado).
  - La seccion "Results" en EN estaba escrita en espanol.

Idempotente: si `intellectual-property` ya existe, no hace nada.
Antes de tocar nada vuelca services a migrations/backup_services.json.
"""
import json
import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

PRIVACY = {
    "title_en": "Privacy Policies & GDPR Compliance",
    "description_en": "<p>A simplified, high-protection framework that brings your data flows into full GDPR compliance without the typical legal complexity.</p>",
    "section_1_title_en": "Overview",
    "section_1_content_en": "<p>In the digital economy, your data is one of your most valuable assets, but it also carries significant risks. We are your go-to consultancy to navigate the complexities of privacy law, specifically focusing on mitigating the risk of joint and several liability for GDPR fines. This approach ensures your digital infrastructure is solid from the beginning, providing the necessary shield to scale your project across borders with confidence.</p>",
    "section_2_title_en": "Our Approach",
    "section_2_content_en": "<p>We combine analytical legal skills with practical business strategy to adapt your privacy framework to your project. Although it is customized work, we deliver at a high tempo. Depending on your needs and based on your feedback, we can even deliver within five business days, so you are on time for the launch of your product or platform.</p><p>&nbsp;</p><p>We deliver a comprehensive suite of essential protections:</p><ol><li><strong>Privacy &amp; Cookie Policies:</strong> Tailored documents that ensure transparency and compliance with Dutch and EU standards.</li><li><strong>Joint Controllership Agreements:</strong> Specialised frameworks to clearly define responsibilities between partners, essential for avoiding the \"trap\" of shared liability.</li><li><strong>Multi-Language Support:</strong> To ensure you never get \"lost in translation,\" all policies and consultations are provided in English, Spanish, or Dutch.</li></ol>",
    "section_3_title_en": "Results",
    "section_3_content_en": "<p class=\"ql-align-justify\">A professional infrastructure that has successfully passed rigorous due diligence processes. You gain full control over your data flows and the peace of mind that your company is protected from the high administrative penalties associated with GDPR non-compliance. The result is a secure, compliant foundation that lets you focus on innovation while we make sure your legal shield is solid from the start.</p>",

    "title_es": "Políticas de Privacidad y Cumplimiento del RGPD",
    "description_es": "<p>Un marco simplificado de alta protección, diseñado para garantizar el pleno cumplimiento del RGPD sin la complejidad legal habitual.</p>",
    "section_1_title_es": "Visión General",
    "section_1_content_es": "<p>En la economía digital, tus datos son uno de tus activos más valiosos, pero también conllevan riesgos significativos.</p><p>Somos tu consultora de referencia para navegar por las complejidades del derecho de privacidad, con un enfoque específico en mitigar el riesgo de responsabilidad solidaria por multas del RGPD.</p><p>Este enfoque garantiza que tu infraestructura digital sea sólida desde el principio, proporcionando el escudo necesario para escalar tu proyecto con confianza.</p>",
    "section_2_title_es": "Nuestro Enfoque",
    "section_2_content_es": "<p>Combinamos un riguroso análisis jurídico con estrategia empresarial práctica para adaptar tu marco de privacidad a las necesidades de tu negocio. Ofrecemos un servicio totalmente personalizado con gran agilidad, pudiendo completar la entrega en tan solo cinco días hábiles para garantizar que llegues a tiempo al lanzamiento de tu producto o plataforma.</p><p>Entregamos un conjunto completo de protecciones esenciales:</p><p>1.&nbsp;&nbsp;&nbsp;&nbsp;<strong>Políticas de Privacidad y Cookies: </strong>Documentos a medida que garantizan la transparencia y el cumplimiento con los estándares neerlandeses y europeos.</p><p>2.&nbsp;&nbsp;&nbsp;&nbsp;<strong>Acuerdos de Corresponsabilidad: </strong>Marcos especializados para definir claramente las responsabilidades entre socios en cuanto a la gestión, protección y manejo de los datos personales.</p><p>3.&nbsp;&nbsp;&nbsp;&nbsp;<strong>Soporte Multilingüe:</strong> Eliminamos cualquier incertidumbre idiomática. Toda la asesoría y la documentación técnica se gestionan en tu propio idioma (inglés, español o neerlandés) para garantizar tu total control sobre cada normativa.</p>",
    "section_3_title_es": "Resultados",
    "section_3_content_es": "<p class=\"ql-align-justify\">Una infraestructura profesional que ha superado con éxito procesos de due diligence rigurosos. Obtienes control total sobre tus flujos de datos y la tranquilidad de que tu empresa está protegida de las elevadas sanciones administrativas asociadas al incumplimiento del RGPD. El resultado es una base segura y conforme que te permite centrarte en la innovación mientras garantizamos que tu escudo legal sea sólido desde el inicio.</p>",

    "title_nl": "Privacybeleid en AVG-compliance",
    "description_nl": "<p>Een vereenvoudigd kader met hoge bescherming dat uw gegevensstromen volledig AVG-conform maakt, zonder de gebruikelijke juridische complexiteit.</p>",
    "section_1_title_nl": "Overzicht",
    "section_1_content_nl": "<p>In de digitale economie zijn uw gegevens een van uw waardevolste bezittingen, maar ze brengen ook aanzienlijke risico's met zich mee.</p><p>Wij zijn uw vaste adviespartner om de complexiteit van het privacyrecht te doorgronden, met specifieke aandacht voor het beperken van het risico op hoofdelijke aansprakelijkheid bij AVG-boetes.</p><p>Zo staat uw digitale infrastructuur vanaf het begin op een solide fundament en beschikt u over het schild dat nodig is om uw project met vertrouwen over de grens op te schalen.</p>",
    "section_2_title_nl": "Onze aanpak",
    "section_2_content_nl": "<p>Wij combineren scherpe juridische analyse met praktische bedrijfsstrategie om uw privacykader op uw project af te stemmen. Hoewel het maatwerk is, leveren wij in hoog tempo: afhankelijk van uw wensen en uw feedback kunnen wij zelfs binnen vijf werkdagen leveren, zodat u op tijd bent voor de lancering van uw product of platform.</p><p>Wij leveren een compleet pakket essentiële bescherming:</p><ol><li><strong>Privacy- en cookiebeleid:</strong> Documenten op maat die transparantie en naleving van Nederlandse en Europese normen waarborgen.</li><li><strong>Overeenkomsten gezamenlijke verwerkingsverantwoordelijkheid:</strong> Gespecialiseerde kaders die de verantwoordelijkheden tussen partners duidelijk vastleggen, essentieel om de valkuil van gedeelde aansprakelijkheid te vermijden.</li><li><strong>Meertalige ondersteuning:</strong> Al het advies en alle documentatie leveren wij in het Engels, Spaans of Nederlands, zodat u nooit \"lost in translation\" raakt.</li></ol>",
    "section_3_title_nl": "Resultaten",
    "section_3_content_nl": "<p>Een professionele infrastructuur die strenge due-diligencetrajecten met succes heeft doorstaan. U krijgt volledige controle over uw gegevensstromen en de zekerheid dat uw onderneming beschermd is tegen de hoge bestuurlijke boetes bij niet-naleving van de AVG. Het resultaat is een veilige, compliant basis waarmee u zich op innovatie kunt richten.</p>",
}

INTELLECTUAL_PROPERTY = {
    "slug": "intellectual-property",
    "icon": "flaticon-stats",
    "sort_order": 3,

    "title_en": "Intellectual Property Protection",
    "description_en": "<p>Robust structures to secure, license and monetise the intellectual property your business is built on.</p>",
    "section_1_title_en": "Overview",
    "section_1_content_en": "<p>In the digital economy, your intellectual property is one of your most valuable assets, and often the one least formally protected. We help you establish who owns what, how it can be used and how it can be commercialised, before ambiguity turns into a dispute. This approach ensures the foundation of your project is solid from the beginning, giving you the confidence to license, partner and scale across borders.</p>",
    "section_2_title_en": "Our Approach",
    "section_2_content_en": "<p>We combine analytical legal skills with practical business strategy to adapt your IP framework to your project. Although it is customized work, we deliver at a high tempo. Depending on your needs and based on your feedback, we can even deliver within five business days, so you are on time for the launch of your product or platform.</p><p>&nbsp;</p><p>We deliver a comprehensive suite of essential protections:</p><ol><li><strong>Licensing Agreements:</strong> Robust structures to protect and monetise your intellectual property.</li><li><strong>Ownership &amp; Assignment Clauses:</strong> Clear terms in your contracts with founders, employees and contractors, so the rights to what they create sit where they belong.</li><li><strong>Multi-Language Support:</strong> To ensure you never get \"lost in translation,\" all agreements and consultations are provided in English, Spanish, or Dutch.</li></ol>",
    "section_3_title_en": "Results",
    "section_3_content_en": "<p class=\"ql-align-justify\">A professional infrastructure that has successfully passed rigorous due diligence processes. You gain clarity over what your company owns and the confidence to license and commercialise it without opening the door to disputes. The result is a secure foundation that lets you focus on innovation while we make sure your legal shield is solid from the start.</p>",

    "title_es": "Protección de la Propiedad Intelectual (PI)",
    "description_es": "<p>Estructuras sólidas para asegurar, licenciar y monetizar la propiedad intelectual sobre la que se construye tu negocio.</p>",
    "section_1_title_es": "Visión General",
    "section_1_content_es": "<p>En la economía digital, tu propiedad intelectual es uno de tus activos más valiosos y, a menudo, el que menos formalmente protegido está.</p><p>Te ayudamos a establecer quién es titular de qué, cómo puede usarse y cómo puede comercializarse, antes de que la ambigüedad se convierta en un conflicto.</p><p>Este enfoque garantiza que la base de tu proyecto sea sólida desde el principio, dándote la confianza necesaria para licenciar, asociarte y escalar con seguridad.</p>",
    "section_2_title_es": "Nuestro Enfoque",
    "section_2_content_es": "<p>Combinamos un riguroso análisis jurídico con estrategia empresarial práctica para adaptar tu marco de PI a las necesidades de tu negocio. Ofrecemos un servicio totalmente personalizado con gran agilidad, pudiendo completar la entrega en tan solo cinco días hábiles para garantizar que llegues a tiempo al lanzamiento de tu producto o plataforma.</p><p>Entregamos un conjunto completo de protecciones esenciales:</p><p>1.&nbsp;&nbsp;&nbsp;&nbsp;<strong>Acuerdos de Licencia: </strong>Estructuras sólidas para proteger y monetizar tu propiedad intelectual.</p><p>2.&nbsp;&nbsp;&nbsp;&nbsp;<strong>Cláusulas de Titularidad y Cesión: </strong>Términos claros en tus contratos con socios, empleados y colaboradores, para que los derechos sobre lo que crean queden donde corresponde.</p><p>3.&nbsp;&nbsp;&nbsp;&nbsp;<strong>Soporte Multilingüe:</strong> Eliminamos cualquier incertidumbre idiomática. Toda la asesoría y la documentación se gestionan en tu propio idioma (inglés, español o neerlandés).</p>",
    "section_3_title_es": "Resultados",
    "section_3_content_es": "<p class=\"ql-align-justify\">Una infraestructura profesional que ha superado con éxito procesos de due diligence rigurosos. Obtienes claridad sobre lo que tu empresa posee y la confianza para licenciarlo y comercializarlo sin abrir la puerta a conflictos. El resultado es una base segura que te permite centrarte en la innovación mientras garantizamos que tu escudo legal sea sólido desde el inicio.</p>",

    "title_nl": "Bescherming van Intellectueel Eigendom",
    "description_nl": "<p>Solide structuren om het intellectueel eigendom waarop uw onderneming rust vast te leggen, te licentiëren en te verzilveren.</p>",
    "section_1_title_nl": "Overzicht",
    "section_1_content_nl": "<p>In de digitale economie is uw intellectueel eigendom een van uw waardevolste bezittingen, en vaak het minst formeel beschermde.</p><p>Wij helpen u vast te leggen wie eigenaar is van wat, hoe het gebruikt mag worden en hoe het gecommercialiseerd kan worden, voordat onduidelijkheid uitgroeit tot een geschil.</p><p>Zo staat de basis van uw project vanaf het begin stevig en kunt u met vertrouwen licentiëren, samenwerken en opschalen.</p>",
    "section_2_title_nl": "Onze aanpak",
    "section_2_content_nl": "<p>Wij combineren scherpe juridische analyse met praktische bedrijfsstrategie om uw IE-kader op uw project af te stemmen. Hoewel het maatwerk is, leveren wij in hoog tempo: afhankelijk van uw wensen en uw feedback kunnen wij zelfs binnen vijf werkdagen leveren, zodat u op tijd bent voor de lancering van uw product of platform.</p><p>Wij leveren een compleet pakket essentiële bescherming:</p><ol><li><strong>Licentieovereenkomsten:</strong> Solide structuren om uw intellectueel eigendom te beschermen en te verzilveren.</li><li><strong>Eigendoms- en overdrachtsbepalingen:</strong> Heldere afspraken in uw contracten met oprichters, werknemers en opdrachtnemers, zodat de rechten op wat zij creëren op de juiste plek terechtkomen.</li><li><strong>Meertalige ondersteuning:</strong> Alle overeenkomsten en advisering leveren wij in het Engels, Spaans of Nederlands, zodat u nooit \"lost in translation\" raakt.</li></ol>",
    "section_3_title_nl": "Resultaten",
    "section_3_content_nl": "<p>Een professionele infrastructuur die strenge due-diligencetrajecten met succes heeft doorstaan. U krijgt duidelijkheid over wat uw onderneming bezit en het vertrouwen om dit te licentiëren en te commercialiseren zonder de deur open te zetten voor geschillen.</p>",
}


def main():
    engine = create_engine(os.getenv("DATABASE_URL"))
    here = os.path.dirname(__file__)

    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM services ORDER BY sort_order, id")).fetchall()
        backup = [dict(r._mapping) for r in rows]
        with open(os.path.join(here, "backup_services.json"), "w", encoding="utf-8") as f:
            json.dump(backup, f, ensure_ascii=False, indent=2, default=str)
        print(f"backup de {len(backup)} servicios -> migrations/backup_services.json")

        if conn.execute(text("SELECT 1 FROM services WHERE slug = 'intellectual-property'")).fetchone():
            print("intellectual-property ya existe: no se hace nada")
            return

        base = conn.execute(text("SELECT * FROM services WHERE slug = 'privacy-policy'")).fetchone()
        if not base:
            print("ERROR: no existe el servicio privacy-policy", file=sys.stderr)
            sys.exit(1)

        sets = ", ".join(f"{k} = :{k}" for k in PRIVACY)
        conn.execute(
            text(f"UPDATE services SET {sets}, updated_at = NOW() WHERE slug = 'privacy-policy'"),
            PRIVACY,
        )
        print("privacy-policy actualizado (solo privacidad/RGPD, NL y EN corregidos)")

        cols = ", ".join(INTELLECTUAL_PROPERTY)
        vals = ", ".join(f":{k}" for k in INTELLECTUAL_PROPERTY)
        new_id = conn.execute(
            text(f"INSERT INTO services ({cols}) VALUES ({vals}) RETURNING id"),
            INTELLECTUAL_PROPERTY,
        ).scalar()
        print(f"intellectual-property creado (id={new_id})")

        conn.commit()


if __name__ == "__main__":
    main()
