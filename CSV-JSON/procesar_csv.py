import csv
import json
import os
from collections import defaultdict

def leer_csv_por_nombre(path, tipo):
    resultado = {}
    for archivo in os.listdir(path):
        with open(os.path.join(path, archivo), encoding='latin-1', mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                titulo = row["TITULO:"].strip().lower()
                if titulo not in resultado:
                    resultado[titulo] = {"areas": [], "catalogos": []}
                if tipo == "area":
                    if archivo.replace(".csv", "").upper() not in resultado[titulo]["areas"]:
                        resultado[titulo]["areas"].append(archivo.replace(".csv", "").upper())
                elif tipo == "catalogo":
                    if archivo.replace(".csv", "").upper() not in resultado[titulo]["catalogos"]:
                        resultado[titulo]["catalogos"].append(archivo.replace(".csv", "").upper())
    return resultado

def fusionar_dicts(dict1, dict2):
    for k, v in dict2.items():
        if k in dict1:
            dict1[k]["areas"].extend([a for a in v["areas"] if a not in dict1[k]["areas"]])
            dict1[k]["catalogos"].extend([c for c in v["catalogos"] if c not in dict1[k]["catalogos"]])
        else:
            dict1[k] = v
    return dict1

def guardar_json(diccionario, archivo):
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(diccionario, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    areas = leer_csv_por_nombre("datos/csv/areas", "area")
    catalogos = leer_csv_por_nombre("datos/csv/catalogos", "catalogo")
    combinado = fusionar_dicts(areas, catalogos)
    guardar_json(combinado, "datos/csv/json/revistas_base.json")
    print("Archivo JSON generado con éxito.")
