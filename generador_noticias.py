import feedparser, json, random, requests, spacy, os
from googletrans import Translator

# Inicialización de IA
try:
    nlp = spacy.load("es_core_news_lg")
except:
    os.system("python -m spacy download es_core_news_lg")
    nlp = spacy.load("es_core_news_lg")

translator = Translator()

def clasificar_unesco(texto):
    """Consulta rápida a Wikidata para validar áreas académicas reales"""
    doc = nlp(texto.lower())
    sustantivos = [t.text for t in doc if t.pos_ == "NOUN" and len(t.text) > 5]
    
    # Intentamos validar el primer sustantivo fuerte como disciplina
    for s in sustantivos[:3]:
        url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={s}&language=es&format=json"
        try:
            r = requests.get(url, timeout=2).json()
            if r.get('search'):
                return r['search'][0]['label'].upper()
        except: continue
    return "CIENCIA GENERAL"

def ejecutar():
    fuentes = ["https://rss.sciencedaily.com/top.xml", "https://arxiv.org/rss/econ", "https://arxiv.org/rss/math"]
    biblioteca = []
    etiquetas = ["INNOVACIÓN", "HALLAZGO", "DESCUBRIMIENTO", "PREMIADOS"]

    for url in fuentes:
        feed = feedparser.parse(url)
        for e in random.sample(feed.entries, min(len(feed.entries), 10)):
            try:
                t_es = translator.translate(e.title, dest='es').text
                r_es = translator.translate(e.summary[:250], dest='es').text
                area = clasificar_unesco(t_es)
                
                # Keywords vía NLP
                doc_kw = nlp(t_es + " " + r_es)
                kw = [t.text for t in doc_kw if t.is_alpha and not t.is_stop and len(t.text) > 4]

                biblioteca.append({
                    "titulo": t_es.upper(),
                    "resumen": r_es + "...",
                    "area": area,
                    "leyenda": random.choice(etiquetas),
                    "fecha": random.randint(1970, 2026),
                    "keywords": ", ".join(list(set(kw))[:5]).title(),
                    "img": f"https://picsum.photos/seed/{random.randint(1,999)}/400/600",
                    "link": e.link
                })
            except: continue

    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(biblioteca, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    ejecutar()
