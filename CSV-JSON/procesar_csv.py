import csv
import json
import os
from collections import defaultdict

def leer_csv_y_agrupar(path, tipo):
    revistas = defaultdict(lambda: {"areas": [], "catalogos": []})
    for archivo in os.listdir(path):
        if archivo.endswith(".csv"):
            with open(os.path.join(path, archivo), encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    titulo = row["titulo"].strip().lower()
                    valor = row[tipo].strip()
                    if valor not in revistas[titulo][tipo + "s"]:
                        revistas[titulo][tipo + "s"].append(valor)
    return revistas

def fusionar_dicts(dict1, dict2):
    for k, v in dict2.items():
        if k in dict1:
            dict1[k]["areas"].extend([area for area in v["areas"] if area not in dict1[k]["areas"]])
            dict1[k]["catalogos"].extend([cat for cat in v["catalogos"] if cat not in dict1[k]["catalogos"]])
        else:
            dict1[k] = v
    return dict1

def guardar_json(diccionario, path_json):
    with open(path_json, 'w', encoding='utf-8') as f:
        json.dump(diccionario, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    areas = leer_csv_y_agrupar("datos/csv/areas", "area")
    catalogos = leer_csv_y_agrupar("datos/csv/catalogos", "catalogo")
    combinado = fusionar_dicts(areas, catalogos)
    guardar_json(combinado, "datos/json/revistas_base.json")
    print("Archivo JSON generado con éxito.")
