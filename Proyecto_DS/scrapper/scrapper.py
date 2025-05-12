import os
import json
import requests
import time
from bs4 import BeautifulSoup
import unicodedata
import difflib
# Ruta donde guardaremos el archivo JSON final
OUTPUT_JSON = "datos/json/catalogo_general.json"

# --- FUNCIONES EXTRA ---

def normalizar(texto):
    if not texto:
        return ''
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    return texto

def buscar_nombre_aproximado(lista, nombre_objetivo):
    nombre_objetivo_norm = normalizar(nombre_objetivo)
    lista_normalizada = [normalizar(nombre) for nombre in lista]
    coincidencias = difflib.get_close_matches(nombre_objetivo_norm, lista_normalizada, n=1, cutoff=0.7)
    if coincidencias:
        idx = lista_normalizada.index(coincidencias[0])
        return lista[idx]
    return None
# Tiempo entre solicitudes para no saturar el servidor
DELAY_SEGUNDOS = 2

def cargar_catalogo_original(ruta):
    """ Cargar el catálogo de revistas original en JSON """
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)

def cargar_catalogo_scrapeado():
    """ Cargar revistas ya scrapeadas si existe el archivo """
    if os.path.exists(OUTPUT_JSON):
        with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}

def guardar_catalogo_scrapeado(datos):
    """ Guardar datos actualizados en el JSON """
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

from urllib.parse import urljoin

def obtener_info_revista(nombre_revista):
    print(f"Buscando: {nombre_revista}")
    url_busqueda = f"https://www.scimagojr.com/journalsearch.php?q={nombre_revista.replace(' ', '+')}"
    print(f"URL de búsqueda: {url_busqueda}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    # Buscar la revista
    respuesta = requests.get(url_busqueda, headers=headers)
    soup = BeautifulSoup(respuesta.text, 'html.parser')

    # Buscar el primer resultado (basado en cómo se ve la estructura actual)
    link_tag = soup.select_one('a[href*="journalsearch.php?q="] span.jrnlname')
    if not link_tag:
        print(f"No encontrada: {nombre_revista}")
        return None

    link_href = link_tag.find_parent('a')['href']
    link_revista = urljoin("https://www.scimagojr.com/", link_href)
    print(f"Revista encontrada: {nombre_revista}")
    print(f"URL revista: {link_revista}")

    # Acceder a la página específica de la revista
    respuesta_revista = requests.get(link_revista, headers=headers)
    soup_revista = BeautifulSoup(respuesta_revista.text, 'html.parser')

    def extraer_contenido(label):
        tag = soup_revista.find('div', string=label)
        return tag.find_next('div').text.strip() if tag else "No disponible"

    def extraer_sitio_web():
        btn = soup_revista.find('a', class_='btn btn-home-links')
        return btn['href'] if btn else "No disponible"

    def extraer_issn():
        span = soup_revista.find('span', string='ISSN')
        if span:
            return span.find_next_sibling('span').text.strip()
        return "No disponible"

    return {
        'sitio_web': extraer_sitio_web(),
        'h_index': extraer_contenido('H Index'),
        'area_y_categoria': soup_revista.find('div', class_='subjectareas').text.strip() if soup_revista.find('div', class_='subjectareas') else "No disponible",
        'publisher': extraer_contenido('Publisher'),
        'issn': extraer_issn(),
        'widget': soup_revista.find('iframe')['src'] if soup_revista.find('iframe') else "No disponible",
        'tipo_publicacion': extraer_contenido('Type'),
        'ultima_visita': time.strftime("%Y-%m-%d")
    }



def scrappear_revistas():
    """ Scrappear todas las revistas del catálogo """
    catalogo = cargar_catalogo_original('datos/json/catalogo_general.json')  
    revistas_scrapeadas = cargar_catalogo_scrapeado()

    for titulo in catalogo.keys():
        titulo_lower = titulo.lower()

        # Si ya existe en el JSON y fue visitado hace menos de 30 días, NO lo buscamos de nuevo
        if titulo_lower in revistas_scrapeadas:
            ultima_visita = revistas_scrapeadas[titulo_lower].get('ultima_visita')
            # Si existe fecha, calculamos los días pasados desde la última visita
            # Si no existe fecha, obligamos a volver a scrappear
            if ultima_visita:
                try:
                    dias_pasados = (time.time() - time.mktime(time.strptime(ultima_visita, "%Y-%m-%d"))) / (60 * 60 * 24)
                except ValueError:
                    print(f"Fecha inválida para {titulo}, scrappeando de nuevo...")
                    ultima_visita = None
            else:
                ultima_visita = None
                dias_pasados = None
        # Scrapear la revista
        info_revista = obtener_info_revista(titulo)
        if info_revista:
            revistas_scrapeadas[titulo_lower] = info_revista

        # Guardar cada vez que obtenemos nueva info (por si se interrumpe)
        guardar_catalogo_scrapeado(revistas_scrapeadas)

        # Esperar para no saturar el servidor
        time.sleep(DELAY_SEGUNDOS)

if __name__ == "__main__":
    scrappear_revistas()
