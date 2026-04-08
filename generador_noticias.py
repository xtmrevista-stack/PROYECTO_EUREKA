import feedparser
import json
import random
import urllib.parse
import requests
import spacy
from datetime import datetime
from googletrans import Translator
from collections import Counter

# Inicialización de IA y Traducción
try:
    nlp = spacy.load("es_core_news_lg")
except:
    import os
    os.system("python -m spacy download es_core_news_lg")
    nlp = spacy.load("es_core_news_lg")

translator = Translator()

# FILTROS DE SEGURIDAD (Ignorar Pseudociencia)
PSEUDOCIENCIA = ["horóscopo", "astrología", "zodiaco", "mágico", "milagroso", "tarot"]

def obtener_tesauro_universal():
    """Consulta Wikidata para traer miles de términos de todas las áreas por igual"""
    url = "https://query.wikidata.org/sparql"
    query = """
    SELECT ?itemLabel WHERE {
      { ?item wdt:P31/wdt:P279* wd:Q193627. } UNION # Áreas UNESCO / ArXiv
      { ?item wdt:P31 wd:Q11344. } UNION           # Elementos Químicos (Tabla Periódica)
      { ?item wdt:P31 wd:Q11173. } UNION           # Compuestos Químicos
      { ?item wdt:P31/wdt:P279* wd:Q41630. } UNION # Psicoanálisis (Lacan/Freud)
      { ?item wdt:P31/wdt:P279* wd:Q8134. } UNION  # Economía
      { ?item wdt:P31/wdt:P279* wd:Q12136. }       # Salud (PubMed)
      SERVICE wikibase:label { bd:serviceParam wikibase:language "es". }
    } LIMIT 10000
    """
    try:
        r = requests.get(url, params={'format': 'json', 'query': query}, timeout=20)
        return set(row['itemLabel']['value'].lower() for row in r.json()['results']['bindings'])
    except:
        return {"química", "psicoanálisis", "goce", "economía", "puzolana", "antropología"}

TESAURO = obtener_tesauro_universal()

def ejecutar_cerebro():
    # Usamos urllib.parse para asegurar que las URLs sean válidas
    fuentes = [
        "https://rss.sciencedaily.com/top.xml", 
        "https://arxiv.org/rss/econ",
        "https://arxiv.org/rss/physics"
    ]
    
    noticias_finales = []
    for url_raw in fuentes:
        url = urllib.parse.quote(url_raw, safe=':/?=')
        feed = feedparser.parse(url)
        
        # Seleccionamos una muestra aleatoria si hay muchas noticias
        entradas = feed.entries
        if len(entradas) > 10:
            entradas = random.sample(entradas, 10)

        for entry in entradas:
            try:
                texto_es = translator.translate(entry.title, dest='es').text
            except:
                texto_es = entry.title
            
            doc = nlp(texto_es.lower())
            
            # Usamos Counter para medir la densidad de conceptos científicos
            conteo_conceptos = Counter([t.text for t in doc if t.text in TESAURO or t.lemma_ in TESAURO])
            
            # Filtro de Pseudociencia
            es_basura = any(t.text in PSEUDOCIENCIA for t in doc)
            
            if conteo_conceptos and not es_basura:
                noticias_finales.append({
                    "titulo": texto_es,
                    "resumen": entry.summary[:250] + "..." if 'summary' in entry else "",
                    "fecha": datetime.now().year,
                    "conceptos": [c[0] for c in conteo_conceptos.most_common(4)],
                    "link": entry.link
                })
    
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias_finales, f, ensure_ascii=False, indent=4)
    print(f"✅ Cerebro sincronizado: {len(noticias_finales)} noticias validadas.")

if __name__ == "__main__":
    ejecutar_cerebro()
