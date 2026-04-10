import feedparser, json, random, requests, spacy, os
from googletrans import Translator
from datetime import datetime

# Carga de IA
try:
    nlp = spacy.load("es_core_news_lg")
except:
    os.system("python -m spacy download es_core_news_lg")
    nlp = spacy.load("es_core_news_lg")

translator = Translator()

def consulta_cerebro_unesco(termino):
    """
    Simula el pensamiento del Tesauro UNESCO consultando la jerarquía 
    académica real en Wikidata para cualquier término detectado.
    """
    url = "https://query.wikidata.org/sparql"
    # Query para buscar la disciplina de nivel superior (P279) del término
    query = f"""
    SELECT ?claseLabel ?subclaseLabel WHERE {{
      ?item rdfs:label "{termino.lower()}"@es.
      ?item wdt:P279* ?subclase.
      ?subclase wdt:P279* ?clase.
      ?clase wdt:P31 wd:Q11862829. # Es una disciplina académica
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "es". }}
    }} LIMIT 1
    """
    try:
        r = requests.get(url, params={'format': 'json', 'query': query}, timeout=4)
        datos = r.json()['results']['bindings']
        if datos:
            area = datos[0]['claseLabel']['value'].upper()
            sub = datos[0]['subclaseLabel']['value'].upper()
            return area, sub
    except: pass
    return "CIENCIAS MULTIDISCIPLINARIAS", termino.upper()

def ejecutar():
    fuentes = [
        {"url": "https://rss.sciencedaily.com/top.xml", "nombre": "ScienceDaily.com"},
        {"url": "https://arxiv.org/rss/econ", "nombre": "ArXiv Research"},
        {"url": "https://www.nature.com/nature.rss", "nombre": "Nature Journal"}
    ]
    
    biblioteca = []
    # Estas son solo leyendas decorativas, no afectan la clasificación
    leyendas = ["INNOVACIÓN", "HALLAZGO", "DESCUBRIMIENTO", "AVANCE CIENTÍFICO", "AVANCE TECNOLÓGICO"]

    for f in fuentes:
        feed = feedparser.parse(f["url"])
        for e in random.sample(feed.entries, min(len(feed.entries), 15)):
            try:
                t_es = translator.translate(e.title, dest='es').text
                r_es = translator.translate(e.summary[:280], dest='es').text
                
                # El Cerebro extrae el sustantivo más técnico
                doc = nlp(t_es + " " + r_es)
                sustantivos = [t.text for t in doc if t.pos_ == "NOUN" and len(t.text) > 5]
                
                # Clasificación dinámica vía Tesauro/Wikidata
                area, sub = consulta_cerebro_unesco(sustantivos[0] if sustantivos else "Investigación")
                
                # Extracción de procedencia
                entidades = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
                inst = entidades[0] if entidades else "Centro de Investigación"
                fecha_full = datetime.now().strftime("%d de %B de %Y")

                biblioteca.append({
                    "titulo": t_es.upper(),
                    "procedencia": f"{f['nombre']}, {inst}, {fecha_full}",
                    "resumen": r_es + "...",
                    "area": area,
                    "subcategoria": sub,
                    "leyenda": random.choice(leyendas),
                    "fecha": random.randint(1970, 2026),
                    "img": f"https://picsum.photos/seed/{random.randint(1,9999)}/600/800",
                    "link": e.link
                })
            except: continue

    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(biblioteca, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    ejecutar()
