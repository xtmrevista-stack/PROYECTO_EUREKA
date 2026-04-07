import feedparser
import json
import random
import urllib.parse
from datetime import datetime
from googletrans import Translator

MAPA_MAESTRO = {
    "HUMANIDADES": ["Literature", "Philosophy", "Ethics", "Religion", "Art History", "Musicology", "Linguistics", "Philology"],
    "CIENCIAS SOCIALES": ["Anthropology", "Archaeology", "Economics", "Geography", "Political Science", "Psychology", "Sociology", "Psychoanalysis", "Law", "Ethnology", "Demography"],
    "CIENCIAS NATURALES": ["Astronomy", "Biology", "Chemistry", "Earth Sciences", "Physics", "Ecology", "Oceanography", "Paleontology", "Genetics", "Botany", "Zoology"],
    "CIENCIAS FORMALES": ["Logic", "Mathematics", "Statistics", "Theoretical Computer Science", "Systems Theory", "Game Theory", "Topology", "Number Theory"],
    "CIENCIAS APLICADAS": ["Agriculture", "Architecture", "Engineering", "Medicine", "Oncology", "Pharmacology", "Nanotechnology", "Robotics", "Artificial Intelligence", "Cybersecurity", "Econophysics", "Bionics"]
}

def traducir(texto):
    try:
        translator = Translator()
        return translator.translate(texto, dest='es').text
    except: return texto

def ejecutar_oceano_visual():
    biblioteca = []
    ahora = datetime.now()
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    fecha_hoy = f"{dias[ahora.weekday()]} {ahora.day:02d} de {meses[ahora.month-1]} de {ahora.year}"

    todas = [(cat, sub) for cat, subs in MAPA_MAESTRO.items() for sub in subs]
    
    for cat, sub in todas:
        query = urllib.parse.quote(f'"{sub}" university research breakthrough')
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        try:
            feed = feedparser.parse(url)
            for entrada in feed.entries[:8]:
                # Intentamos extraer la imagen si está disponible en los tags del RSS
                img_url = ""
                if 'media_content' in entrada:
                    img_url = entrada.media_content[0]['url']
                elif 'links' in entrada:
                    for link in entrada.links:
                        if 'image' in link.get('type', ''):
                            img_url = link.href

                biblioteca.append({
                    "tema": cat,
                    "subtema": sub.upper(),
                    "fecha": fecha_hoy,
                    "titulo": traducir(entrada.title),
                    "link": entrada.link,
                    "fuente": entrada.source.get('title', 'Global Research'),
                    "imagen": img_url # Nueva clave para la imagen
                })
        except: continue

    random.shuffle(biblioteca)
    with open("noticias.json", "w", encoding="utf-8") as f:
        json.dump(biblioteca, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    ejecutar_oceano_visual()
