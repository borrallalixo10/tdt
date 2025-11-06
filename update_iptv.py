import requests
import re

OUTPUT_FILE = "favoritos.m3u"
TDT_URL = "https://www.tdtchannels.com/lists/tv.m3u"
IPTV_URL = "https://iptv-org.github.io/iptv/countries/es.m3u"

# URL fija para DMAX
DMAX_FIXED_URL = "https://streaming.aurora.enhanced.live/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NjI0NTE1MzksIm5iZiI6MTc2MjQ1MTUzOSwiZXhwIjoxNzYyNDUxODk5LCJjb3VudHJ5Q29kZSI6ImVzIiwidWlwIjoiNzkuMTE2LjE4Mi4zMyJ9.bzxhLaIKA-3yHdC7ja06aWSYFWGZvJDnEwOrVENOjwU/live/es/b9243cdb24df40128098f3ea25fcf47d/index_3.m3u8"

# Lista de tvg-id que queremos (de tdtchannels)
TARGET_TVG_IDS = {
    "RTVE1.TV", "RTVE2.TV", "TVGAL.TV", "TVG2.TV", "ANTENA3.TV", "TELECINCO.TV",
    "LASEXTA.TV", "CUATRO.TV", "24H.TV", "DMAX.TV", "FDF.TV", "PARAMOUNT.TV",
    "TRECE.TV", "RMTV.TV", "CLAN.TV", "A3SERIES.TV", "MEGA.TV", "BEMAD.TV",
    "NEOX.TV", "NOVA.TV", "DIVINITY.TV", "DKISS.TV", "Squirrel.es@SD",
    "ENERGY.TV", "Teledeporte.es@SD", "TEN.TV", "BOING.TV"
}

def parse_m3u_with_tvg(content):
    lines = content.strip().splitlines()
    channels = []
    i = 0
    while i < len(lines):
        if lines[i].startswith('#EXTINF'):
            if i + 1 < len(lines):
                extinf = lines[i]
                url = lines[i + 1]
                tvg_id_match = re.search(r'tvg-id="([^"]*)"', extinf)
                tvg_id = tvg_id_match.group(1) if tvg_id_match else ""
                name = extinf.split(',', 1)[1] if ',' in extinf else ''
                channels.append((tvg_id, name.strip(), extinf, url))
                i += 2
            else:
                i += 1
        else:
            i += 1
    return channels

def main():
    # Descargar ambas listas
    tdt_resp = requests.get(TDT_URL)
    tdt_resp.raise_for_status()
    tdt_channels = parse_m3u_with_tvg(tdt_resp.text)

    iptv_resp = requests.get(IPTV_URL)
    iptv_resp.raise_for_status()
    iptv_channels = parse_m3u_with_tvg(iptv_resp.text)

    # Crear mapa: nombre_base -> URL (de iptv-org)
    iptv_url_map = {}
    for tvg_id, name, _, url in iptv_channels:
        # Normalizar nombre: quitar HD/SD y pasar a minúsculas
        base_name = re.sub(r'\s*(HD|SD|UHD|FHD|4K)\s*$', '', name, flags=re.IGNORECASE)
        base_name = re.sub(r'\s+', ' ', base_name.strip().lower())
        iptv_url_map[base_name] = url

    # Generar salida
    output_lines = ['#EXTM3U url-tvg="https://www.tdtchannels.com/epg/TV.json"']
    for tvg_id, name, extinf, _ in tdt_channels:
        if tvg_id not in TARGET_TVG_IDS:
            continue

        # Normalizar nombre de tdtchannels
        base_name = re.sub(r'\s*(HD|SD|UHD|FHD|4K)\s*$', '', name, flags=re.IGNORECASE)
        base_name = re.sub(r'\s+', ' ', base_name.strip().lower())

        # Buscar URL en iptv-org por nombre base
        if base_name in iptv_url_map:
            url = DMAX_FIXED_URL if tvg_id == "DMAX.TV" else iptv_url_map[base_name]
            output_lines.append(extinf)
            output_lines.append(url)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(output_lines) + "\n")

    print(f"✅ Generado {OUTPUT_FILE} con {len(output_lines)//2} canales.")

if __name__ == "__main__":
    main()
