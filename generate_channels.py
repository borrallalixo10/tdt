#!/usr/bin/env python3
# generate_channels.py
import re
import sys
import os

def parse_playlist(playlist_file):
    try:
        with open(playlist_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{playlist_file}'.")
        sys.exit(1)
    except Exception as e:
        print(f"Error al leer '{playlist_file}': {e}")
        sys.exit(1)

    lines = content.splitlines()
    channels = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Aceptar '#EXTINF' con o sin ':' y tolerar espacios
        if line.upper().startswith('#EXTINF'):
            extinf = lines[i].rstrip('\r\n')
            # Buscar la siguiente línea no vacía como URL
            j = i + 1
            while j < len(lines) and lines[j].strip() == '':
                j += 1
            url = lines[j].strip() if j < len(lines) else ''
            # Extraer tvg-id (si existe)
            tvg_id_match = re.search(r'tvg-id="([^"]+)"', extinf)
            if tvg_id_match:
                channels.append((extinf, url))
            # Avanzar el índice
            i = j + 1
        else:
            i += 1

    return channels

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    playlist_file = os.path.join(base_dir, 'favoritos.m3u')
    output_file = os.path.join(base_dir, 'playlist.m3u')

    channels = parse_playlist(playlist_file)

    if not channels:
        print("No se encontraron canales con tvg-id en el archivo.")
        return

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            for extinf, url in channels:
                f.write(extinf + '\n')
                f.write(url + '\n')
    except Exception as e:
        print(f"Error al escribir '{output_file}': {e}")
        sys.exit(1)

    print(f"Archivo '{os.path.basename(output_file)}' generado con {len(channels)} canales.")

if __name__ == "__main__":
    main()
