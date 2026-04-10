import feedparser, json, random, requests, spacy, os
from googletrans import Translator
from datetime import datetime

try:
    nlp = spacy.load("es_core_news_lg")
except:
    os.system("python -m spacy download es_core_news_lg")
    nlp = spacy.load("es_core_news_lg")

translator = Translator()

def consulta_cerebro_unesco(termino):
    """
    Simula el pensamiento del Tesauro UNESCO y Wikidata. 
    Busca la disciplina académica real para CUALQUIER término.
    """
    url = "https://query.wikidata.org/sparql"
    # Query para encontrar la disciplina madre (P279) de nivel académico (Q11862829)
    query = f"""
    SELECT ?areaLabel WHERE {{
      ?item rdfs:label "{termino.lower()}"@es.
      ?item wdt:P279* ?area.
      ?area wdt:P31 wd:Q11862829. 
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "es". }}
    }} LIMIT 1
    """
    try:
        r = requests.get(url, params={'format': 'json', 'query': query}, timeout=4)
        datos = r.json()['results']['bindings']
        if datos:
            return datos[0]['areaLabel']['value'].upper()
    except: pass
    return "CIENCIAS MULTIDISCIPLINARIAS"

def ejecutar():
    # Ampliamos fuentes para un flujo casi infinito
    fuentes = [
        {"url": "https://rss.sciencedaily.com/top.xml", "nombre": "ScienceDaily"},
        {"url": "https://arxiv.org/rss/math", "nombre": "ArXiv Matemáticas"},
        {"url": "https://arxiv.org/rss/physics", "nombre": "ArXiv Física"},
        {"url": "https://www.nature.com/nature.rss", "nombre": "Nature Journal"},
        {"url": "https://phys.org/rss-feed/", "nombre": "Phys.org"}
    ]
    
    biblioteca = []
    leyendas = ["INNOVACIÓN", "HALLAZGO", "DESCUBRIMIENTO", "AVANCE CIENTÍFICO", "AVANCE TECNOLÓGICO"]

    for f in fuentes:
        feed = feedparser.parse(f["url"])
        for e in feed.entries:
            try:
                t_es = translator.translate(e.title, dest='es').text
                r_es = translator.translate(e.summary[:350], dest='es').text
                
                # El Cerebro identifica el concepto técnico principal
                doc = nlp(t_es + " " + r_es)
                sustantivos = [t.text for t in doc if t.pos_ == "NOUN" and len(t.text) > 5]
                termino_clave = sustantivos[0] if sustantivos else "Investigación"
                
                # Clasificación dinámica sin etiquetas manuales
                area_especifica = consulta_cerebro_unesco(termino_clave)
                
                # Palabras Clave extraídas directamente del texto
                kw = [ent.text.upper() for ent in doc.ents] + [s.upper() for s in sustantivos[:4]]
                
                anio_noticia = random.choice([2026, 2026, 2025, 2024, 2023])
                fecha_full = datetime.now().strftime("%d de %B") + f" de {anio_noticia}"

                biblioteca.append({
                    "titulo": t_es.upper(),
                    "procedencia": f"{f['nombre']}, Centro de Investigación, {fecha_full}",
                    "resumen": r_es,
                    "area": area_especifica,
                    "subcategoria": termino_clave.upper(),
                    "leyenda": random.choice(leyendas),
                    "fecha": anio_noticia,
                    "palabras_clave": ", ".join(list(set(kw))[:6]),
                    "img": f"https://picsum.photos/seed/{random.randint(1,99999)}/800/600",
                    "link": e.link
                })
            except: continue

    random.shuffle(biblioteca)
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(biblioteca, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    ejecutar()
