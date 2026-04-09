import feedparser
import json
import random
import requests
import spacy
import os
from googletrans import Translator
from collections import Counter

# Inicialización de IA para análisis de texto
try:
    nlp = spacy.load("es_core_news_lg")
except:
    os.system("python -m spacy download es_core_news_lg")
    nlp = spacy.load("es_core_news_lg")

translator = Translator()

# Configuración de Áreas y Diccionarios Académicos
AREAS_CIENTIFICAS = {
    "MATEMÁTICAS": ["algoritmo", "pascal", "montecarlo", "teorema", "cálculo", "geometría", "ecuación"],
    "ECONOMÍA": ["mercado", "precio", "finanzas", "pib", "inflación", "ganancia", "econofísica", "bangladesh"],
    "QUÍMICA": ["molécula", "nitruro", "reacción", "átomo", "químico", "compuesto", "síntesis"],
    "PSICOLOGÍA": ["psicoanálisis", "goce", "clínica", "terapia", "subjetividad", "mente"],
    "FÍSICA": ["partícula", "energía", "cuántico", "materia", "universo", "astrofísica"]
}

ETIQUETAS_HALLAZGO = ["INNOVACIÓN", "DESCUBRIMIENTO", "HALLAZGO", "NUEVO", "PREMIADOS", "CONDECORADOS"]

def obtener_area(titulo):
    """Detecta el área académica basada en palabras clave"""
    t = titulo.lower()
    for area, palabras in AREAS_CIENTIFICAS.items():
        if any(p in t for p in palabras):
            return area
    return "CIENCIA GENERAL"

def extraer_keywords(texto):
    """Usa NLP para extraer las 5 palabras más importantes"""
    doc = nlp(texto)
    palabras = [token.text for token in doc if token.is_alpha and not token.is_stop and len(token.text) > 3]
    comunes = [item[0] for item in Counter(palabras).most_common(5)]
    return ", ".join(comunes).title()

def ejecutar_cerebro():
    fuentes = [
        "https://rss.sciencedaily.com/top.xml",
        "https://arxiv.org/rss/econ",
        "https://arxiv.org/rss/math"
    ]
    
    noticias_finales = []
    
    for url in fuentes:
        feed = feedparser.parse(url)
        # Seleccionamos muestras aleatorias para que la página siempre cambie
        entradas = random.sample(feed.entries, min(len(feed.entries), 10))
        
        for entry in entradas:
            try:
                # Traducción al español
                t_es = translator.translate(entry.title, dest='es').text
                r_es = translator.translate(entry.summary[:280], dest='es').text
                
                area = obtener_area(t_es)
                keywords = extraer_keywords(t_es + " " + r_es)
                
                # Imagen dinámica (Unsplash busca por términos clave de la noticia)
                termino_busqueda = t_es.split()[0]
                img_url = f"https://images.unsplash.com/photo-1507413245164-6160d8298b31?auto=format&fit=crop&q=80&w=400" # Imagen base de ciencia por defecto
                # Intentar buscar una específica
                img_url = f"https://source.unsplash.com/featured/400x300?science,{area},{termino_busqueda}"

                noticias_finales.append({
                    "titulo": t_es.upper(),
                    "resumen": r_es + "...",
                    "area_cientifica": area,
                    "categoria": "INVESTIGACIÓN ACADÉMICA",
                    "etiqueta": random.choice(ETIQUETAS_HALLAZGO),
                    "fecha": 2026, # Año real actual solicitado
                    "palabras_clave": keywords,
                    "imagen": img_url,
                    "link": entry.link
                })
            except Exception as e:
                print(f"Error procesando noticia: {e}")
                continue

    # Guardar el archivo JSON final
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias_finales, f, ensure_ascii=False, indent=4)
    print(f"✅ Éxito: Se han generado {len(noticias_finales)} noticias con formato Eureka.")

if __name__ == "__main__":
    ejecutar_cerebro()
