#!/usr/bin/env python3
import requests
import json
import re
import os
import sys

# URL de la lista de iptv-org para España
IPTV_ORG_ES_URL = "https://iptv-org.github.io/iptv/countries/es.m3u"

# Archivo de equivalencias (ubicado en el mismo directorio del script)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EQUIVALENCIAS_FILE = os.path.join(BASE_DIR, "equivalencias.json")

# URL fija para DMAX
DMAX_FIXED_URL = "https://streaming.aurora.enhanced.live/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NjI0NTE1MzksIm5iZiI6MTc2MjQ1MTUzOSwiZXhwIjoxNzYyNDUxODk5LCJjb3VudHJ5Q29kZSI6ImVzIiwidWlwIjoiNzkuMTE2LjE4Mi4zMyJ9.bzxhLaIKA-3yHdC7ja06aWSYFWGZvJDnEwOrVENOjwU/live/es/b9243cdb24df40128098f3ea25fcf47d/index_3.m3u8"

def parse_m3u(content):
    """Parsea una lista M3U y devuelve una lista de (tvg_id, extinf, url)."""
    raw_lines = content.splitlines()
    lines = [ln for ln in raw_lines]
    channels = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.upper().startswith('#EXTINF'):
            extinf = lines[i].rstrip('\r\n')
            # buscar siguiente línea no vacía como URL
            j = i + 1
            while j < len(lines) and lines[j].strip() == '':
                j += 1
            url = lines[j].strip() if j < len(lines) else ''
            # Extraer tvg-id si existe
            tvg_id_match = re.search(r'tvg-id="([^"]+)"', extinf)
            tvg_id = tvg_id_match.group(1) if tvg_id_match else ""
            channels.append((tvg_id, extinf, url))
            i = j + 1
        else:
            i += 1
    return channels

def load_equivalencias(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: no se encontró '{path}'.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error al parsear JSON en '{path}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error al leer '{path}': {e}")
        sys.exit(1)

    # Construir mapa tvg-id -> (nombre_normalizado, orden)
    tvg_id_to_info = {}
    for nombre_norm, info in data.items():
        if not isinstance(info, dict):
            continue
        tvg = info.get("tvg_id") or info.get("tvgid") or ""
        orden = info.get("orden", 0)
        if tvg:
            tvg_id_to_info[tvg] = (nombre_norm, orden)
    return tvg_id_to_info

def main():
    print("📥 Descargando lista de iptv-org...")
    try:
        resp = requests.get(IPTV_ORG_ES_URL, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Error al descargar {IPTV_ORG_ES_URL}: {e}")
        sys.exit(1)

    iptv_channels = parse_m3u(resp.text)

    equivalencias_map = load_equivalencias(EQUIVALENCIAS_FILE)

    # Usamos una lista para permitir órdenes duplicados y conservar todos los canales
    favoritos_list = []  # elementos: (orden, extinf, url)
    otros_output = ['#EXTM3U']

    # Agregar manualmente DMAX como canal 9, si no está presente
    favoritos_list.append((9, '#EXTINF:-1 tvg-id="dmax" group-title="General",DMAX', DMAX_FIXED_URL))

    for tvg_id, extinf, url in iptv_channels:
        info = equivalencias_map.get(tvg_id)
        if info:
            nombre_norm, orden = info
            # Si es DMAX y existe URL fija, usarla
            if nombre_norm.lower() == "dmax" and DMAX_FIXED_URL:
                url = DMAX_FIXED_URL
            favoritos_list.append((orden, extinf, url))
        else:
            otros_output.append(extinf)
            otros_output.append(url)

    # Ordenar favoritos por 'orden' (si orden no es int, se ordena como texto)
    favoritos_list.sort(key=lambda x: x[0])

    favoritos_output = ['#EXTM3U']
    for _, extinf, url in favoritos_list:
        favoritos_output.append(extinf)
        favoritos_output.append(url)

    # Escribir archivos
    try:
        with open(os.path.join(BASE_DIR, 'favoritos.m3u'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(favoritos_output) + '\n')
        num_fav = (len(favoritos_output) - 1) // 2
        print(f"✅ Generado favoritos.m3u con {num_fav} canales.")
    except Exception as e:
        print(f"Error al escribir 'favoritos.m3u': {e}")
        sys.exit(1)

    try:
        with open(os.path.join(BASE_DIR, 'otros.m3u'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(otros_output) + '\n')
        num_otros = (len(otros_output) - 1) // 2
        print(f"✅ Generado otros.m3u con {num_otros} canales.")
    except Exception as e:
        print(f"Error al escribir 'otros.m3u': {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
