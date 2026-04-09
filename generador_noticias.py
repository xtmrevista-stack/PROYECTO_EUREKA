import feedparser
import json
import random
import requests
import spacy
import os
from googletrans import Translator
from collections import Counter

# Inicialización de IA
try:
    nlp = spacy.load("es_core_news_lg")
except:
    os.system("python -m spacy download es_core_news_lg")
    nlp = spacy.load("es_core_news_lg")

translator = Translator()

def obtener_tesauro_dinamico():
    """Consulta Wikidata para obtener conceptos de ciencias exactas, sociales y humanidades"""
    url = "https://query.wikidata.org/sparql"
    # Query que busca etiquetas de disciplinas científicas y académicas
    query = """
    SELECT ?itemLabel WHERE {
      ?item wdt:P31/wdt:P279* wd:Q11862829. 
      SERVICE wikibase:label { bd:serviceParam wikibase:language "es". }
    } LIMIT 500
    """
    try:
        r = requests.get(url, params={'format': 'json', 'query': query}, timeout=10)
        datos = r.json()
        return [row['itemLabel']['value'].upper() for row in datos['results']['bindings']]
    except:
        # Respaldo si falla la conexión
        return ["QUÍMICA", "MATEMÁTICAS", "ECONOMÍA", "PSICOANÁLISIS", "FÍSICA", "INGENIERÍA"]

TESAURO = obtener_tesauro_dinamico()
ETIQUETAS = ["INNOVACIÓN", "DESCUBRIMIENTO", "HALLAZGO", "NUEVO", "PREMIADOS", "CONDECORADOS"]

def clasificar_con_ia(titulo, resumen):
    texto = (titulo + " " + resumen).lower()
    doc = nlp(texto)
    
    # Buscamos coincidencias con el Tesauro de Wikipedia/UNESCO
    for concepto in TESAURO:
        if concepto.lower() in texto:
            return concepto
            
    # Si no hay coincidencia exacta, usamos el sustantivo más relevante
    sustantivos = [token.text.upper() for token in doc if token.pos_ == "NOUN" and len(token.text) > 4]
    return sustantivos[0] if sustantivos else "INVESTIGACIÓN"

def ejecutar():
    print("Sincronizando con Tesauros Globales...")
    fuentes = [
        "https://rss.sciencedaily.com/top.xml",
        "https://arxiv.org/rss/econ",
        "https://arxiv.org/rss/math",
        "https://www.nature.com/nature.rss"
    ]
    
    noticias_finales = []
    
    for url in fuentes:
        try:
            feed = feedparser.parse(url)
            for e in random.sample(feed.entries, min(len(feed.entries), 8)):
                # Traducción
                try:
                    t_es = translator.translate(e.title, dest='es').text
                    r_es = translator.translate(e.summary[:280], dest='es').text
                except:
                    t_es, r_es = e.title, e.summary[:280]

                area = clasificar_con_ia(t_es, r_es)
                
                # Keywords inteligentes
                doc_kw = nlp(t_es + " " + r_es)
                kw = [t.text for t in doc_kw if t.is_alpha and not t.is_stop and len(t.text) > 3]
                
                noticias_finales.append({
                    "titulo": t_es.upper(),
                    "resumen": r_es + "...",
                    "area": f"ÁREA CIENTÍFICA: {area}",
                    "leyenda": random.choice(ETIQUETAS),
                    "fecha": 2026,
                    "palabras_clave": ", ".join(list(set(kw))[:6]).title(),
                    "imagen": f"https://picsum.photos/seed/{random.randint(1,9999)}/600/400",
                    "link": e.link
                })
        except: continue

    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias_finales, f, ensure_ascii=False, indent=4)
    print("✅ Cerebro Maestro actualizado con Tesauros.")

if __name__ == "__main__":
    ejecutar()
