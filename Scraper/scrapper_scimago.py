import requests
from bs4 import BeautifulSoup
import json
import os
import time

def cargar_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def guardar_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def buscar_revista_scimago(nombre):
    url = f'https://www.scimagojr.com/journalsearch.php?q={nombre.replace(" ", "+")}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    resultado = soup.find("a", class_="search_results_title")
    if resultado:
        link = "https://www.scimagojr.com/" + resultado['href']
        return scrapear_info_revista(link)
    else:
        print(f"No encontrada: {nombre}")
        return None

def scrapear_info_revista(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    def extraer_texto(selector):
        tag = soup.select_one(selector)
        return tag.text.strip() if tag else "No disponible"

    return {
        "url": url,
        "H-Index": extraer_texto("div.hindexnumber"),
        "Subject Area and Category": extraer_texto("div.subjectarea"),
        "Publisher": extraer_texto("div.publisher"),
        "ISSN": extraer_texto("div.issn"),
        "Widget": f"https://www.scimagojr.com/journalsearch.php?q={url.split('=')[-1]}",
        "Publication Type": extraer_texto("div.pubtype")
    }

# Cargar revistas base
revistas_base = cargar_json("datos/csv/json/revistas_base.json")
resultado_final = {}

for titulo in revistas_base:
    print(f"Buscando: {titulo}")
    datos = buscar_revista_scimago(titulo)
    if datos:
        resultado_final[titulo] = datos
        time.sleep(2)  # para evitar ser bloqueado

# Guardar resultados
guardar_json(resultado_final, "datos/revistas_scimago.json")
print("Scraping completo.")
