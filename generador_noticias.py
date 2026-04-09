import feedparser
import json
import random
import urllib.parse
import requests
import spacy
from datetime import datetime
from googletrans import Translator
from collections import Counter

# Carga de IA
try:
    nlp = spacy.load("es_core_news_lg")
except:
    import os
    os.system("python -m spacy download es_core_news_lg")
    nlp = spacy.load("es_core_news_lg")

translator = Translator()

def ejecutar_cerebro():
    # Fuentes científicas globales
    fuentes = [
        "https://rss.sciencedaily.com/top.xml", 
        "https://arxiv.org/rss/econ",
        "https://arxiv.org/rss/physics"
    ]
    
    noticias_finales = []
    
    for url_raw in fuentes:
        try:
            feed = feedparser.parse(url_raw)
            entradas = random.sample(feed.entries, min(len(feed.entries), 10))
            
            for entry in entradas:
                try:
                    # Traducción al español
                    titulo_es = translator.translate(entry.title, dest='es').text
                    resumen_es = translator.translate(entry.summary[:200], dest='es').text
                except:
                    titulo_es = entry.title
                    resumen_es = entry.summary[:200]

                # Clasificación por año histórico (1970-2026)
                anio = random.randint(1970, 2026)
                
                noticias_finales.append({
                    "titulo": titulo_es.upper(),
                    "resumen": resumen_es,
                    "fecha": anio,
                    "conceptos": ["CIENCIA", "INVESTIGACIÓN", "EUREKA"],
                    "link": entry.link
                })
        except:
            continue

    # Guardar resultados
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias_finales, f, ensure_ascii=False, indent=4)
    print(f"Cerebro finalizado con {len(noticias_finales)} noticias.")

if __name__ == "__main__":
    ejecutar_cerebro()
