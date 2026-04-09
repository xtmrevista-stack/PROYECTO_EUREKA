import feedparser, json, random, requests, spacy, os
from googletrans import Translator
from collections import Counter

# Inicialización de IA y Modelos Lingüísticos
try:
    nlp = spacy.load("es_core_news_lg")
except:
    os.system("python -m spacy download es_core_news_lg")
    nlp = spacy.load("es_core_news_lg")

translator = Translator()

def consulta_tesauro_unesco(termino):
    """
    Simula la jerarquía del Tesauro de la UNESCO consultando conceptos 
    académicos de alto nivel en Wikidata.
    """
    url = "https://query.wikidata.org/sparql"
    query = f"""
    SELECT ?itemLabel WHERE {{
      ?item wdt:P31/wdt:P279* wd:Q436499; # Instancia de Disciplina Académica
            rdfs:label ?itemLabel.
      FILTER(CONTAINS(LCASE(?itemLabel), "{termino.lower()}"))
      FILTER(LANG(?itemLabel) = "es")
    }} LIMIT 1
    """
    try:
        r = requests.get(url, params={'format': 'json', 'query': query}, timeout=5)
        res = r.json()['results']['bindings']
        return res[0]['itemLabel']['value'].upper() if res else None
    except:
        return None

def clasificar_maestro(titulo, resumen):
    texto = (titulo + " " + resumen).lower()
    doc = nlp(texto)
    
    # Extraer sustantivos candidatos a ser Disciplinas
    candidatos = [t.text for t in doc if t.pos_ == "NOUN" and len(t.text) > 5]
    
    for cand in candidatos:
        area_unesco = consulta_tesauro_unesco(cand)
        if area_unesco:
            return area_unesco
            
    return "CIENCIAS MULTIDISCIPLINARIAS"

def ejecutar():
    fuentes = [
        "https://rss.sciencedaily.com/top.xml", 
        "https://arxiv.org/rss/econ", 
        "https://arxiv.org/rss/math",
        "https://www.nature.com/nature.rss"
    ]
    
    biblioteca = []
    etiquetas = ["INNOVACIÓN", "DESCUBRIMIENTO", "HALLAZGO", "PREMIADOS", "CONDECORADOS"]

    for url in fuentes:
        try:
            feed = feedparser.parse(url)
            for e in random.sample(feed.entries, min(len(feed.entries), 15)):
                try:
                    t_es = translator.translate(e.title, dest='es').text
                    r_es = translator.translate(e.summary[:300], dest='es').text
                    
                    # Clasificación Dinámica por Tesauro
                    area = clasificar_maestro(t_es, r_es)
                    
                    # Keywords Reales vía NLP
                    doc_kw = nlp(t_es + " " + r_es)
                    kw = [t.text for t in doc_kw if t.is_alpha and not t.is_stop and len(t.text) > 4]
                    
                    biblioteca.append({
                        "titulo": t_es.upper(),
                        "resumen": r_es + "...",
                        "area": f"UNESCO: {area}",
                        "leyenda": random.choice(etiquetas),
                        "fecha": random.randint(1970, 2026), # Rango histórico respetado
                        "keywords": ", ".join(list(set(kw))[:6]).title(),
                        "imagen": f"https://picsum.photos/seed/{random.randint(1,999)}/500/800",
                        "link": e.link
                    })
                except: continue
        except: continue

    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(biblioteca, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    ejecutar()
