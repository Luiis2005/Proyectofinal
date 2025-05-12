import json
import time

# Ruta de tu archivo original
archivo_original = 'datos/json/revistas_scrapeadas.json'

# Ruta donde guardaremos el archivo corregido
archivo_corregido = 'datos/json/revistas_scrapeadas_limpio.json'

def validar_fecha(fecha_str):
    """Revisa si la fecha está en el formato correcto."""
    try:
        time.strptime(fecha_str, "%Y-%m-%d")
        return True
    except Exception:
        return False

def limpiar_archivo():
    # Abrimos el archivo
    with open(archivo_original, 'r', encoding='utf-8') as f:
        revistas = json.load(f)

    revistas_limpias = {}

    for titulo, datos in revistas.items():
        ultima_visita = datos.get('ultima_visita')

        # Si no hay fecha o está mal, ponemos una fecha antigua
        if not ultima_visita or not validar_fecha(ultima_visita):
            print(f"Corrigiendo fecha para: {titulo}")
            datos['ultima_visita'] = "2000-01-01"

        revistas_limpias[titulo] = datos

    # Guardamos en un nuevo archivo
    with open(archivo_corregido, 'w', encoding='utf-8') as f:
        json.dump(revistas_limpias, f, indent=4, ensure_ascii=False)

    print(f"Archivo corregido guardado en: {archivo_corregido}")

if __name__ == "__main__":
    limpiar_archivo()
