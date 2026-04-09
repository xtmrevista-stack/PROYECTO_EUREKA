import feedparser
import json
import random
import urllib.parse
import requests
import spacy
import os
from datetime import datetime
from googletrans import Translator
from collections import Counter

# Inicialización de IA con manejo de errores
try:
    nlp = spacy.load("es_core_news_lg")
except:
    os.system("python -m spacy download es_core_news_lg")
    nlp = spacy.load("es_core_news_lg")

translator = Translator()

def ejecutar_cerebro():
    # Fuentes diversas para asegurar flujo constante
    fuentes = [
        "https://rss.sciencedaily.com/top.xml",
        "https://arxiv.org/rss/econ",
        "https://arxiv.org/rss/physics",
        "https://www.nature.com/nature.rss"
    ]
    
    noticias_nuevas = []
    
    # Seleccionamos fuentes al azar para mayor variedad
    random.shuffle(fuentes)
    
    for url in fuentes:
        try:
            feed = feedparser.parse(url)
            # Tomamos una muestra aleatoria amplia de cada fuente
            items = feed.entries
            random.shuffle(items)
            
            for entry in items[:8]:
                try:
                    # Traducción forzada para evitar textos en inglés
                    t_es = translator.translate(entry.title, dest='es').text
                    r_es = translator.translate(entry.summary[:250], dest='es').text
                except:
                    t_es, r_es = entry.title, entry.summary[:250]

                # Rango histórico solicitado 1970-2026
                anio_h = random.randint(1970, 2026)
                
                noticias_nuevas.append({
                    "titulo": t_es.upper(),
                    "resumen": r_es + "...",
                    "fecha": anio_h,
                    "conceptos": ["CIENCIA", "EUREKA", "INVESTIGACIÓN"],
                    "link": entry.link
                })
        except:
            continue

    # IMPORTANTE: Sobrescritura total del archivo para que no se quede fijo
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias_nuevas, f, ensure_ascii=False, indent=4)
    print(f"✅ Cerebro Eureka actualizado: {len(noticias_nuevas)} noticias nuevas.")

if __name__ == "__main__":
    ejecutar_cerebro()
