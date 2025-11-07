import requests
import re

# URLs de las fuentes
TDT_CHANNELS_URL = "https://www.tdtchannels.com/lists/tv.m3u"
IPTV_ORG_ES_URL = "https://iptv-org.github.io/iptv/countries/es.m3u"

# URL fija para DMAX
DMAX_FIXED_URL = "https://streaming.aurora.enhanced.live/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NjI0NTE1MzksIm5iZiI6MTc2MjQ1MTUzOSwiZXhwIjoxNzYyNDUxODk5LCJjb3VudHJ5Q29kZSI6ImVzIiwidWlwIjoiNzkuMTE2LjE4Mi4zMyJ9.bzxhLaIKA-3yHdC7ja06aWSYFWGZvJDnEwOrVENOjwU/live/es/b9243cdb24df40128098f3ea25fcf47d/index_3.m3u8"

# Lista de nombres de canales deseados (normalizados)
FAVORITOS_NOMBRES = {
    "la1", "la2", "tvg", "antena3", "telecinco", "lasexta", "cuatro", "24h",
    "dmax", "fdf", "paramountnetwork", "trece", "realmadridtv", "clan",
    "a3series", "mega", "bemad", "neox", "nova", "divinity", "squirrel",
    "energy", "teledeporte", "ten", "tvg2"
}

def parse_m3u(content):
    """Parsea una lista M3U y devuelve una lista de (tvg_id, nombre_normalizado, extinf, url)."""
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
                # Extraer nombre del canal (después de la coma)
                name_match = re.search(r',(.*)', extinf)
                full_name = name_match.group(1).strip() if name_match else ""
                # Normalizar nombre: quitar HD, SD, espacios, pasar a minúsculas
                normalized_name = re.sub(r'\s*(HD|SD|UHD|FHD|4K|1080p|720p)\s*', '', full_name, flags=re.IGNORECASE)
                normalized_name = re.sub(r'\s+', '', normalized_name.lower())
                channels.append((tvg_id, normalized_name, extinf, url))
                i += 2
            else:
                i += 1
        else:
            i += 1
    return channels

def main():
    print("📥 Descargando listas...")
    tdt_resp = requests.get(TDT_CHANNELS_URL)
    tdt_resp.raise_for_status()
    tdt_channels = parse_m3u(tdt_resp.text)

    iptv_resp = requests.get(IPTV_ORG_ES_URL)
    iptv_resp.raise_for_status()
    iptv_channels = parse_m3u(iptv_resp.text)

    # Crear mapa de nombre_normalizado -> (tvg_id, extinf, url) para iptv-org
    iptv_map = {name: (tvg_id, extinf, url) for tvg_id, name, extinf, url in iptv_channels}

    # --- Procesar favoritos ---
    favoritos_output = ['#EXTM3U url-tvg="https://www.tdtchannels.com/epg/TV.json"']
    otros_output = ['#EXTM3U']

    for tdt_tvg_id, tdt_name, tdt_extinf, tdt_url in tdt_channels:
        if tdt_name in FAVORITOS_NOMBRES:
            # Buscar stream en iptv-org usando el nombre normalizado
            iptv_info = iptv_map.get(tdt_name)
            stream_url = None
            if tdt_name == "dmax" and DMAX_FIXED_URL:
                 stream_url = DMAX_FIXED_URL
            elif iptv_info:
                _, _, stream_url = iptv_info

            if stream_url:
                # Modificar el EXTINF de tdtchannels para usar group-title="tdt"
                # Buscar y reemplazar group-title
                updated_extinf = re.sub(r'group-title="[^"]*"', 'group-title="tdt"', tdt_extinf)
                # Si no existe group-title, añadirlo
                if 'group-title=' not in updated_extinf:
                    updated_extinf = updated_extinf.replace(',', ' group-title="tdt",')
                
                favoritos_output.append(updated_extinf)
                favoritos_output.append(stream_url)
            else:
                print(f"⚠️ No se encontró stream para el canal favorito: {tdt_name} (tvg-id: {tdt_tvg_id})")
        else:
            # Canal no deseado, va a otros.m3u
            otros_output.append(tdt_extinf)
            otros_output.append(tdt_url)

    # --- Escribir archivos ---
    with open('favoritos.m3u', 'w', encoding='utf-8') as f:
        f.write('\n'.join(favoritos_output) + '\n')
    print(f"✅ Generado favoritos.m3u con {len(favoritos_output)//2} canales.")

    with open('otros.m3u', 'w', encoding='utf-8') as f:
        f.write('\n'.join(otros_output) + '\n')
    print(f"✅ Generado otros.m3u con {len(otros_output)//2} canales.")

if __name__ == "__main__":
    main()
