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

    with open('channels.m3u', 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        for tvg_id in tvg_ids:
            # Escribir la línea EXTINF con comillas escapadas para el archivo m3u
            f.write(f'#EXTINF:-1 tvg-id="{tvg_id}"\n')
            f.write(',placeholder\n') # URL temporal, no se usa realmente para el EPG

    print(f"Archivo 'channels.m3u' generado con {len(tvg_ids)} canales.")

if __name__ == "__main__":
    main()
