import feedparser, json, random, requests, spacy, os
from googletrans import Translator
from datetime import datetime

try:
    nlp = spacy.load("es_core_news_lg")
except:
    os.system("python -m spacy download es_core_news_lg")
    nlp = spacy.load("es_core_news_lg")

translator = Translator()

def clasificador_profundo(titulo, resumen):
    """Extrae disciplinas específicas analizando el contexto académico del texto."""
    texto_total = (titulo + " " + resumen).lower()
    doc = nlp(texto_total)
    
    # Diccionario de respaldo de Áreas UNESCO si Wikidata falla
    diccionario_emergencia = {
        "MATEMÁTICAS": ["algoritmo", "pascal", "cálculo", "números", "geometría", "estadística", "ecuación"],
        "BIOLOGÍA": ["célula", "genética", "especie", "ecosistema", "proteína", "virus", "adn"],
        "QUÍMICA": ["molécula", "reacción", "átomo", "compuesto", "polímero", "químico"],
        "FÍSICA": ["cuántico", "energía", "partícula", "gravedad", "relatividad", "materia"],
        "INGENIERÍA": ["construcción", "software", "materiales", "puente", "sistema", "mecánica"],
        "PSICOLOGÍA": ["psicoanálisis", "mente", "comportamiento", "clínica", "lacan", "cognitivo"],
        "ECONOMÍA": ["mercado", "finanzas", "precios", "pbi", "inflación", "econofísica"]
    }

    # 1. Intento por palabras clave de alta relevancia
    for area, terminos in diccionario_emergencia.items():
        if any(t in texto_total for t in terminos):
            # Buscar subárea (sustantivo más importante del texto)
            sub = [t.text.upper() for t in doc if t.pos_ == "NOUN" and len(t.text) > 5]
            return area, (sub[0] if sub else "INVESTIGACIÓN")

    # 2. Intento por Wikidata
    entidades = [ent.text for ent in doc.ents]
    if entidades:
        try:
            url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={entidades[0]}&language=es&format=json"
            r = requests.get(url, timeout=2).json()
            if r.get('search'):
                return "CIENCIA APLICADA", r['search'][0]['label'].upper()
        except: pass

    return "CIENCIAS MULTIDISCIPLINARIAS", "ESTUDIO TÉCNICO"

def ejecutar():
    # Aumentamos la cantidad de fuentes para alimentar el scroll infinito
    fuentes = [
        {"url": "https://rss.sciencedaily.com/top.xml", "nombre": "ScienceDaily"},
        {"url": "https://arxiv.org/rss/math", "nombre": "ArXiv Math"},
        {"url": "https://arxiv.org/rss/physics", "nombre": "ArXiv Physics"},
        {"url": "https://www.nature.com/nature.rss", "nombre": "Nature"},
        {"url": "https://phys.org/rss-feed/", "nombre": "Phys.org"}
    ]
    
    biblioteca = []
    leyendas = ["INNOVACIÓN", "HALLAZGO", "DESCUBRIMIENTO", "AVANCE CIENTÍFICO", "AVANCE TECNOLÓGICO"]

    for f in fuentes:
        feed = feedparser.parse(f["url"])
        for e in feed.entries: # Tomamos todas las disponibles
            try:
                t_es = translator.translate(e.title, dest='es').text
                r_es = translator.translate(e.summary[:350], dest='es').text
                
                area, sub = clasificador_profundo(t_es, r_es)
                
                # Keywords precisas
                doc_kw = nlp(t_es + " " + r_es)
                kw = [ent.text.upper() for ent in doc_kw.ents] + [t.text.upper() for t in doc_kw if t.pos_ == "NOUN" and len(t.text) > 5]
                
                fecha_full = datetime.now().strftime("%d de %B de %Y")

                biblioteca.append({
                    "titulo": t_es.upper(),
                    "procedencia": f"{f['nombre']}, Institución Académica, {fecha_full}",
                    "resumen": r_es,
                    "area": area,
                    "subcategoria": sub,
                    "leyenda": random.choice(leyendas),
                    "fecha": 2026, # Año fijo para noticias actuales
                    "keywords": ", ".join(list(set(kw))[:6]),
                    "img": f"https://picsum.photos/seed/{random.randint(1,50000)}/800/600",
                    "link": e.link
                })
            except: continue

    # Mezclamos para que no salgan todas las de la misma fuente juntas (Efecto TikTok)
    random.shuffle(biblioteca)

    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(biblioteca, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    ejecutar()
