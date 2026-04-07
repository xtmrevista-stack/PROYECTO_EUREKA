import feedparser
import json
import random
import urllib.parse
from datetime import datetime
from googletrans import Translator

# TAXONOMÍA COMPLETA (Basada en Outline of Academic Disciplines)
DICCIONARIO_MAESTRO = {
    "HUMANIDADES": ["Artes visuales", "Literatura", "Filosofía", "Religión", "Musicología", "Teatro", "Lingüística", "Ética"],
    "CIENCIAS SOCIALES": ["Antropología", "Arqueología", "Economía", "Geografía", "Ciencia política", "Psicología", "Sociología", "Psicoanálisis", "Derecho", "Etnología"],
    "CIENCIAS NATURALES": ["Astronomía", "Biología", "Química", "Ciencias de la Tierra", "Física", "Ecología", "Oceanografía", "Paleontología"],
    "CIENCIAS FORMALES": ["Lógica", "Matemáticas", "Estadística", "Ciencia de la computación", "Teoría de sistemas", "Teoría de juegos"],
    "CIENCIAS APLICADAS": ["Agricultura", "Arquitectura", "Diseño", "Educación", "Ingeniería", "Medicina", "Oncología", "Farmacología", "Nanotecnología", "Robótica", "Inteligencia Artificial", "Ciberseguridad"]
}

def traducir_texto(texto):
    try:
        translator = Translator()
        return translator.translate(texto, dest='es').text
    except: return texto

def ejecutar_oceano_eureka():
    biblioteca = []
    # Fecha exacta: Lunes 06 de Abril de 2026
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    ahora = datetime.now()
    fecha_hoy = f"{dias[ahora.weekday()]} {ahora.day:02d} de {meses[ahora.month-1]} de {ahora.year}"

    # Recorremos cada disciplina para asegurar volumen masivo
    todas_las_ramas = [(cat, sub) for cat, subs in DICCIONARIO_MAESTRO.items() for sub in subs]
    
    for categoria, disciplina in todas_las_ramas:
        query = urllib.parse.quote(f'"{disciplina}" research discovery')
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        
        try:
            feed = feedparser.parse(url)
            for entrada in feed.entries[:8]: # 8 noticias por disciplina = Miles de noticias
                biblioteca.append({
                    "tema": categoria,
                    "subtema": disciplina.upper(),
                    "fecha": fecha_hoy,
                    "titulo": traducir_texto(entrada.title),
                    "fuente": entrada.source.get('title', 'Global Research'),
                    "link": entrada.link
                })
        except: continue

    random.shuffle(biblioteca)
    with open("noticias.json", "w", encoding="utf-8") as f:
        json.dump(biblioteca, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    ejecutar_oceano_eureka()
