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

# --- FILTROS DE SEGURIDAD (PALABRAS NEGATIVAS) ---
PSEUDOCIENCIA = ["horóscopo", "astrología", "tarot", "mágico", "milagroso", "conspiración", "zodiaco"]

def alimentar_tesauro_universal():
    """Consulta Wikidata para traer miles de términos de TODAS las áreas por igual"""
    url = "https://query.wikidata.org/sparql"
    query = """
    SELECT ?itemLabel WHERE {
      { ?item wdt:P31/wdt:P279* wd:Q193627. } UNION # Áreas del conocimiento (UNESCO)
      { ?item wdt:P31 wd:Q11344. } UNION           # Elementos Químicos
      { ?item wdt:P31 wd:Q11173. } UNION           # Compuestos Químicos
      { ?item wdt:P31/wdt:P279* wd:Q41630. } UNION # Psicoanálisis
      { ?item wdt:P31/wdt:P279* wd:Q8134. }        # Economía
      { ?item wdt:P31/wdt:P279* wd:Q35670. }       # Antropología
      SERVICE wikibase:label { bd:serviceParam wikibase:language "es". }
    } LIMIT 15000
    """
    try:
        r = requests.get(url, params={'format': 'json', 'query': query}, timeout=20)
        datos = r.json()
        return set(row['itemLabel']['value'].lower() for row in datos['results']['bindings'])
    except:
        return {"química", "psicoanálisis", "antropología", "economía", "física", "puzolana"}

CONOCIMIENTO_TOTAL = alimentar_tesauro_universal()

def cerebro_maestro(noticia_raw):
    # Traducción
    try:
        texto_es = translator.translate(noticia_raw["texto"], dest='es').text
    except:
        texto_es = noticia_raw["texto"]

    doc = nlp(texto_es.lower())
    conceptos_identificados = []
    
    # Verificación de Seguridad
    for token in doc:
        if token.text in PSEUDOCIENCIA or token.lemma_ in PSEUDOCIENCIA:
            return None # Descarta basura científica

    # Identificación de conceptos (Equidad Total)
    for token in doc:
        # Si el término está en el Tesauro Universal (sea de la rama que sea)
        if token.text in CONOCIMIENTO_TOTAL or token.lemma_ in CONOCIMIENTO_TOTAL:
            conceptos_identificados.append(token.text)

    if conceptos_identificados:
        return {
            "titulo": texto_es[:90] + "...",
            "resumen": texto_es,
            "fecha": noticia_raw.get("fecha", datetime.now().year),
            "conceptos": list(set(conceptos_identificados))[:5],
            "entidades": [ent.text for ent in doc.ents if ent.label_ in ["ORG", "PER"]][:3],
            "link": noticia_raw.get("link", "#")
        }
    return None

# --- EJECUCIÓN ---
def ejecutar_sistema():
    fuentes = ["https://rss.sciencedaily.com/top.xml", "https://arxiv.org/rss/econ"]
    base_final = []
    
    for url in fuentes:
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            noticia = {"texto": entry.title + " " + entry.summary, "link": entry.link, "fecha": 2026}
            resultado = cerebro_maestro(noticia)
            if resultado:
                base_final.append(resultado)
    
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(base_final, f, ensure_ascii=False, indent=4)
    print("✅ noticias.json actualizado.")

# ejecutar_sistema()
