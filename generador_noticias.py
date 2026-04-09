import feedparser
import json
import random
import urllib.parse
import requests
import spacy
from datetime import datetime
from googletrans import Translator
from collections import Counter

# Inicialización de IA
try:
    nlp = spacy.load("es_core_news_lg")
except:
    import os
    os.system("python -m spacy download es_core_news_lg")
    nlp = spacy.load("es_core_news_lg")

translator = Translator()

def obtener_tesauro():
    url = "https://query.wikidata.org/sparql"
    query = """
    SELECT ?itemLabel WHERE {
      { ?item wdt:P31/wdt:P279* wd:Q193627. } UNION 
      { ?item wdt:P31 wd:Q11344. } UNION           
      { ?item wdt:P31/wdt:P279* wd:Q41630. } UNION 
      { ?item wdt:P31/wdt:P279* wd:Q8134. } 
      SERVICE wikibase:label { bd:serviceParam wikibase:language "es". }
    } LIMIT 8000
    """
    try:
        r = requests.get(url, params={'format': 'json', 'query': query}, timeout=20)
        return set(row['itemLabel']['value'].lower() for row in r.json()['results']['bindings'])
    except:
        return {"química", "psicoanálisis", "goce", "economía", "puzolana"}

TESAURO = obtener_tesauro()

def ejecutar():
    fuentes = ["https://rss.sciencedaily.com/top.xml", "https://arxiv.org/rss/econ"]
    noticias = []
    
    for f in fuentes:
        feed = feedparser.parse(f)
        for e in random.sample(feed.entries, min(len(feed.entries), 12)):
            try:
                titulo = translator.translate(e.title, dest='es').text
            except:
                titulo = e.title
            
            doc = nlp(titulo.lower())
            conceptos = Counter([t.text for t in doc if t.text in TESAURO or t.lemma_ in TESAURO])
            
            if conceptos:
                noticias.append({
                    "titulo": titulo,
                    "resumen": e.summary[:200] + "...",
                    "fecha": random.randint(1970, 2026), # Nuevo rango histórico
                    "conceptos": [c[0] for c in conceptos.most_common(3)],
                    "link": e.link
                })
    
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    ejecutar()
