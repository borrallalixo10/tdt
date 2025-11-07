# generate_channels.py
import json
import sys

def main():
    if len(sys.argv) != 2:
        print("Uso: python generate_channels.py <archivo_configuracion.json>")
        sys.exit(1)

    config_file = sys.argv[1]

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de configuración '{config_file}'.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: El archivo '{config_file}' no es un JSON válido.")
        sys.exit(1)

    tvg_ids = config.get('channels', [])

    with open('channels.xml', 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<channels>\n')
        for tvg_id in tvg_ids:
            # Escribir cada canal como un elemento XML
            # El formato es: <channel site="..." lang="..." xmltv_id="..." site_id="...">Nombre</channel>
            # Como no tenemos site, lang, site_id específicos, los dejamos vacíos o genéricos.
            # El xmltv_id será el tvg_id mismo.
            f.write(f'  <channel xmltv_id="{tvg_id}"></channel>\n')
        f.write('</channels>\n')

    print(f"Archivo 'channels.xml' generado con {len(tvg_ids)} canales.")

if __name__ == "__main__":
    main()
