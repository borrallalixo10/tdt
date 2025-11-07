import requests
import json
import re

# URL de la lista de iptv-org para España
IPTV_ORG_ES_URL = "https://iptv-org.github.io/iptv/countries/es.m3u"

# Archivo de equivalencias
EQUIVALENCIAS_FILE = "equivalencias.json"

def parse_m3u(content):
    """Parsea una lista M3U y devuelve una lista de (tvg_id, extinf, url)."""
    lines = content.strip().splitlines()
    channels = []
    i = 0
    while i < len(lines):
        if lines[i].startswith('#EXTINF'):
            if i + 1 < len(lines):
                extinf = lines[i]
                url = lines[i + 1]
                # Extraer tvg-id
                tvg_id_match = re.search(r'tvg-id="([^"]*)"', extinf)
                tvg_id = tvg_id_match.group(1) if tvg_id_match else ""
                channels.append((tvg_id, extinf, url))
                i += 2
            else:
                i += 1
        else:
            i += 1
    return channels

def main():
    print("📥 Descargando lista de iptv-org...")
    iptv_resp = requests.get(IPTV_ORG_ES_URL)
    iptv_resp.raise_for_status()
    iptv_channels = parse_m3u(iptv_resp.text)

    # Cargar equivalencias
    with open(EQUIVALENCIAS_FILE, 'r', encoding='utf-8') as f:
        equivalencias = json.load(f)

    # Crear un conjunto de tvg-ids deseados
    tvg_ids_deseados = set(equivalencias.values())

    # --- Procesar favoritos y otros ---
    favoritos_output = ['#EXTM3U'] # Sin url-tvg
    otros_output = ['#EXTM3U'] # Sin url-tvg

    for tvg_id, extinf, url in iptv_channels:
        if tvg_id in tvg_ids_deseados:
            favoritos_output.append(extinf)
            favoritos_output.append(url)
        else:
            otros_output.append(extinf)
            otros_output.append(url)

    # --- Escribir archivos ---
    with open('favoritos.m3u', 'w', encoding='utf-8') as f:
        f.write('\n'.join(favoritos_output) + '\n')
    print(f"✅ Generado favoritos.m3u con {len(favoritos_output)//2} canales.")

    with open('otros.m3u', 'w', encoding='utf-8') as f:
        f.write('\n'.join(otros_output) + '\n')
    print(f"✅ Generado otros.m3u con {len(otros_output)//2} canales.")

if __name__ == "__main__":
    main()
