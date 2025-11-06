import requests
import re

OUTPUT_FILE = "favoritos.m3u"
TDT_URL = "https://www.tdtchannels.com/lists/tv.m3u"
IPTV_URL = "https://iptv-org.github.io/iptv/countries/es.m3u"

# URL fija para DMAX
DMAX_FIXED_URL = "https://streaming.aurora.enhanced.live/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NjI0NTE1MzksIm5iZiI6MTc2MjQ1MTUzOSwiZXhwIjoxNzYyNDUxODk5LCJjb3VudHJ5Q29kZSI6ImVzIiwidWlwIjoiNzkuMTE2LjE4Mi4zMyJ9.bzxhLaIKA-3yHdC7ja06aWSYFWGZvJDnEwOrVENOjwU/live/es/b9243cdb24df40128098f3ea25fcf47d/index_3.m3u8"

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
                channels.append((tvg_id, extinf, url))
                i += 2
            else:
                i += 1
        else:
            i += 1
    return channels

def main():
    print("📥 Descargando lista de tdtchannels...")
    tdt_resp = requests.get(TDT_URL)
    tdt_resp.raise_for_status()
    tdt_channels = parse_m3u_with_tvg(tdt_resp.text)

    print("📥 Descargando lista de iptv-org...")
    iptv_resp = requests.get(IPTV_URL)
    iptv_resp.raise_for_status()
    iptv_channels = parse_m3u_with_tvg(iptv_resp.text)

    # Crear mapa: tvg-id -> URL (de iptv-org)
    iptv_url_map = {tvg_id: url for tvg_id, _, url in iptv_channels if tvg_id}

    # Generar salida
    output_lines = ['#EXTM3U url-tvg="https://www.tdtchannels.com/epg/TV.json"']
    for tvg_id, extinf, _ in tdt_channels:
        if not tvg_id:
            continue
        if tvg_id in iptv_url_map:
            url = DMAX_FIXED_URL if tvg_id == "DMAX.TV" else iptv_url_map[tvg_id]
            output_lines.append(extinf)
            output_lines.append(url)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(output_lines) + "\n")

    print(f"✅ Generado {OUTPUT_FILE} con {len(output_lines)//2} canales.")

if __name__ == "__main__":
    main()
