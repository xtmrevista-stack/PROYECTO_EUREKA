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
      { ?item wdt:P31/wdt:P279* wd:Q193627. } UNION # Áreas UNESCO
      { ?item wdt:P31 wd:Q11344. } UNION           # Elementos Químicos
      { ?item wdt:P31 wd:Q11173. } UNION           # Compuestos Químicos
      { ?item wdt:P31/wdt:P279* wd:Q41630. } UNION # Psicoanálisis
      { ?item wdt:P31/wdt:P279* wd:Q8134. } UNION  # Economía
      { ?item wdt:P31/wdt:P279* wd:Q12136. }       # Salud (PubMed)
      SERVICE wikibase:label { bd:serviceParam wikibase:language "es". }
    } LIMIT 10000
    """
    try:
        r = requests.get(url, params={'format': 'json', 'query': query}, timeout=20)
        return set(row['itemLabel']['value'].lower() for row in r.json()['results']['bindings'])
    except:
        return {"química", "psicoanálisis", "goce", "economía", "antropología", "nitruro"}

TESAURO = obtener_tesauro_universal()

def ejecutar_cerebro():
    fuentes = [
        "https://rss.sciencedaily.com/top.xml", 
        "https://arxiv.org/rss/econ",
        "https://arxiv.org/rss/physics"
    ]
    
    noticias_finales = []
    for url_raw in fuentes:
        # Uso de urllib.parse para seguridad de la URL
        url = urllib.parse.quote(url_raw, safe=':/?=')
        feed = feedparser.parse(url)
        
        # Selección aleatoria para dinamismo
        entradas = random.sample(feed.entries, min(len(feed.entries), 12))

        for entry in entradas:
            try:
                texto_es = translator.translate(entry.title, dest='es').text
            except:
                texto_es = entry.title
            
            doc = nlp(texto_es.lower())
            
            # Counter para identificar conceptos del tesauro
            conteo = Counter([t.text for t in doc if t.text in TESAURO or t.lemma_ in TESAURO])
            es_basura = any(t.text in PSEUDOCIENCIA for t in doc)
            
            if conteo and not es_basura:
                noticias_finales.append({
                    "titulo": texto_es,
                    "resumen": entry.summary[:200] + "..." if 'summary' in entry else "",
                    "fecha": datetime.now().year,
                    "conceptos": [c[0] for c in conteo.most_common(4)],
                    "link": entry.link
                })
    
    # Escritura del archivo para GitHub
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias_finales, f, ensure_ascii=False, indent=4)
    print(f"✅ Éxito: {len(noticias_finales)} hallazgos científicos procesados.")

if __name__ == "__main__":
    ejecutar_cerebro()
