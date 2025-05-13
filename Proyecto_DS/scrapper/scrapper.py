import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import json
import re
import os

def normalizar(texto):
    return texto.lower().strip()

def obtener_info_revista(nombre_revista, catalogo_extraido):
    print(f"Buscando: {nombre_revista}")
    url_busqueda = f"https://www.scimagojr.com/journalsearch.php?q={nombre_revista.replace(' ', '+')}"
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        respuesta = requests.get(url_busqueda, headers=headers)
        soup = BeautifulSoup(respuesta.text, 'html.parser')

        link_tag = None
        for a in soup.select('a[href^="journalsearch.php?q="]'):
            span = a.find('span', class_='jrnlname')
            if span and normalizar(span.text) == normalizar(nombre_revista):
                link_tag = a
                break

        if not link_tag:
            print(f"No encontrada: {nombre_revista}")
            return

        link_revista = urljoin("https://www.scimagojr.com/", link_tag['href'])
        print(f"Revista encontrada en: {link_revista}")

        resp_revista = requests.get(link_revista, headers=headers)
        soup_revista = BeautifulSoup(resp_revista.text, 'html.parser')

        def extraer_dato_por_h2(etiqueta):
            h2 = soup_revista.find('h2', string=etiqueta)
            if h2:
                p = h2.find_next_sibling('p')
                return p.text.strip() if p else "No disponible"
            return "No disponible"

        def extraer_hindex():
            h2 = soup_revista.find('h2', string="H-Index")
            if h2:
                p = h2.find_next_sibling('p', class_='hindexnumber')
                return p.text.strip() if p else "No disponible"
            return "No disponible"

        def extraer_sitio_web():
            link = soup_revista.find('a', class_='btn btn-home-links') or soup_revista.find('a', string='Homepage')
            return link.get('href', 'No disponible') if link else "No disponible"

        def extraer_widget():
            widget_section = soup_revista.find('div', class_='widgetlegend')
            if widget_section:
                input_code = widget_section.find('input', {'id': 'embed_code'})
                if input_code and 'value' in input_code.attrs:
                    return input_code['value']
                iframe = widget_section.find('iframe')
                if iframe:
                    return iframe.get('src', 'No disponible')
            return "No disponible"

        def extraer_areas():
            seccion = soup_revista.find('h2', string="Subject Area and Category")
            if not seccion:
                return "No disponible"
            ul = seccion.find_next('ul')
            if ul:
                return ' | '.join([li.text.strip() for li in ul.find_all('li')])
            return "No disponible"

        def extraer_tipo_publicacion():
            for dt in soup_revista.find_all('dt'):
                if 'publication type' in normalizar(dt.text):
                    dd = dt.find_next_sibling('dd')
                    if dd:
                        return dd.get_text(strip=True)
            for heading in soup_revista.find_all(['h2', 'h3']):
                if 'publication type' in normalizar(heading.text):
                    next_element = heading.find_next(['p', 'div', 'ul'])
                    if next_element:
                        return next_element.get_text(strip=True)
            for li in soup_revista.find_all('li'):
                if 'publication type' in normalizar(li.text):
                    return li.get_text(strip=True).replace('Publication Type:', '').strip()
            issn = extraer_dato_por_h2('ISSN')
            if issn != "No disponible":
                return "Journal"
            return "No disponible"

        journal_data = {
            'sitio_web': extraer_sitio_web(),
            'h_index': extraer_hindex(),
            'area_y_categoria': extraer_areas(),
            'publisher': extraer_dato_por_h2('Publisher'),
            'issn': extraer_dato_por_h2('ISSN'),
            'widget': extraer_widget(),
            'tipo_publicacion': extraer_tipo_publicacion(),
            'ultima_visita': time.strftime("%Y-%m-%d")
        }

        print(f"Datos extraídos: {journal_data}")
        catalogo_extraido.append({nombre_revista: journal_data})

    except Exception as e:
        print(f"Error con {nombre_revista}: {str(e)}")

def leer_catalogo_general():
    ruta = r'C:\Users\valeu\Downloads\Proyectofinal-main (1)\Proyectofinal-main\Proyecto_DS\datos\json\catalogo_general.json'
    if not os.path.exists(ruta):
        print("Archivo de catálogo general no encontrado.")
        return []
    with open(ruta, 'r', encoding='utf-8') as file:
        return json.load(file)

def obtener_informacion_de_revistas():
    catalogo = leer_catalogo_general()
    if not catalogo:
        print("Catálogo vacío o no válido.")
        return

    catalogo_extraido = []

    for revista in catalogo:
        obtener_info_revista(revista, catalogo_extraido)
        time.sleep(2)

    with open('catalogo_extraido.json', 'w', encoding='utf-8') as json_file:
        json.dump(catalogo_extraido, json_file, indent=4, ensure_ascii=False)

    print("\n✅ Información guardada en catalogo_extraido.json")

obtener_informacion_de_revistas()
