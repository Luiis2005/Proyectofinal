import os
import csv
import json

def generar_catalogo():
    catalogo = {}

    # Leer áreas
    path_areas = 'datos/csv/areas'
    print(f"Leyendo áreas desde: {path_areas}")
    for archivo in os.listdir(path_areas):
        if archivo.endswith('.csv'):
            ruta = os.path.join(path_areas, archivo)
            print(f"🔍 Leyendo archivo de área: {ruta}")
            with open(ruta, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)  # Saltar encabezado
                for row in reader:
                    if not row or not row[0].strip():
                        continue
                    revista = row[0].strip().lower()
                    area = archivo.replace('.csv', '')
                    if revista not in catalogo:
                        catalogo[revista] = {"areas": [], "catalogos": []}
                    if area not in catalogo[revista]["areas"]:
                        catalogo[revista]["areas"].append(area)

    # Leer catálogos
    path_catalogos = 'datos/csv/catalogos'
    print(f"Leyendo catálogos desde: {path_catalogos}")
    for archivo in os.listdir(path_catalogos):
        if archivo.endswith('.csv'):
            ruta = os.path.join(path_catalogos, archivo)
            print(f"🔍 Leyendo archivo de catálogo: {ruta}")
            with open(ruta, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)  # Saltar encabezado
                for row in reader:
                    if not row or not row[0].strip():
                        continue
                    revista = row[0].strip().lower()
                    catalogo_nombre = archivo.replace('.csv', '')
                    if revista not in catalogo:
                        catalogo[revista] = {"areas": [], "catalogos": []}
                    if catalogo_nombre not in catalogo[revista]["catalogos"]:
                        catalogo[revista]["catalogos"].append(catalogo_nombre)

    # Guardar JSON
    output_path = 'datos/json/catalogo_general.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(catalogo, f, indent=4, ensure_ascii=False)

    print(f'✅ Catálogo generado en {output_path} con {len(catalogo)} revistas.')

# Ejecutar la función
if __name__ == "__main__":
    generar_catalogo()
