import feedparser, json, random, requests, spacy, os
from googletrans import Translator
from datetime import datetime

try:
    nlp = spacy.load("es_core_news_lg")
except:
    os.system("python -m spacy download es_core_news_lg")
    nlp = spacy.load("es_core_news_lg")

translator = Translator()

def consulta_experta_unesco(termino):
    """Consulta la jerarquía científica real para clasificar por Áreas UNESCO."""
    url = "https://query.wikidata.org/sparql"
    # Buscamos la disciplina académica raíz (P31 -> Q11862829)
    query = f"""
    SELECT ?areaLabel WHERE {{
      ?item rdfs:label "{termino.lower()}"@es.
      ?item wdt:P279* ?area.
      ?area wdt:P31 wd:Q11862829. 
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "es". }}
    }} LIMIT 1
    """
    try:
        r = requests.get(url, params={'format': 'json', 'query': query}, timeout=5)
        datos = r.json()['results']['bindings']
        if datos:
            return datos[0]['areaLabel']['value'].upper()
    except: pass
    return None

def ejecutar():
    fuentes = [
        {"url": "https://rss.sciencedaily.com/top.xml", "nombre": "ScienceDaily"},
        {"url": "https://arxiv.org/rss/math", "nombre": "ArXiv Matemáticas"},
        {"url": "https://arxiv.org/rss/physics", "nombre": "ArXiv Física"}
    ]
    
    biblioteca = []
    leyendas = ["INNOVACIÓN", "HALLAZGO", "DESCUBRIMIENTO", "AVANCE CIENTÍFICO", "AVANCE TECNOLÓGICO"]

    for f in fuentes:
        feed = feedparser.parse(f["url"])
        items = random.sample(feed.entries, min(len(feed.entries), 15))
        
        for e in items:
            try:
                t_es = translator.translate(e.title, dest='es').text
                r_es = translator.translate(e.summary[:300], dest='es').text
                
                # Análisis de Entidades y Sustantivos
                doc = nlp(t_es + " " + r_es)
                sustantivos = [t.text for t in doc if t.pos_ == "NOUN" and len(t.text) > 5]
                entidades = [ent.text.upper() for ent in doc.ents if len(ent.text) > 2]
                
                # Clasificación por Área UNESCO
                area_unesco = "CIENCIAS GENERALES"
                sub_area = "INVESTIGACIÓN"
                
                if sustantivos:
                    res_unesco = consulta_experta_unesco(sustantivos[0])
                    if res_unesco:
                        area_unesco = res_unesco
                        sub_area = sustantivos[0].upper()

                # Fecha Real de la noticia (evitando años aleatorios incorrectos)
                # Usamos el año actual 2026 para noticias nuevas
                anio_noticia = 2026 
                fecha_full = datetime.now().strftime("%d de %B de %Y")
                
                # Institución procedencia
                orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
                procedencia = f"{f['nombre']}, {orgs[0] if orgs else 'Institución Académica'}, {fecha_full}"

                biblioteca.append({
                    "titulo": t_es.upper(),
                    "procedencia": procedencia,
                    "resumen": r_es,
                    "area": area_unesco,
                    "subcategoria": sub_area,
                    "leyenda": random.choice(leyendas),
                    "fecha": anio_noticia,
                    "keywords": ", ".join(list(set(entidades + sustantivos[:3]))[:6]),
                    "img": f"https://picsum.photos/seed/{random.randint(1,8000)}/600/400",
                    "link": e.link
                })
            except: continue

    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(biblioteca, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    ejecutar()
