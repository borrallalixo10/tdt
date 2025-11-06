import requests
import re

OUTPUT_FILE = "favoritos.m3u"
SOURCE_URL = "https://iptv-org.github.io/iptv/countries/es.m3u"

# Lista fija de canales deseados (normalizados)
DESIRED_CHANNELS = {
    "la 1", "la 2", "tvg", "antena 3", "telecinco", "la sexta", "cuatro", "24h",
    "dmax", "fdf", "paramount network", "trece", "realmadrid tv", "clan",
    "a3series", "mega", "bemad", "neox", "nova", "divinity", "dkiss",
    "squirrel", "energy", "tdp", "ten", "boing", "tvg2"
}

# Mapeo tvg-id corregido
TVD_ID_MAP = {
    "la 1": "RTVE1.TV",
    "la 2": "RTVE2.TV",
    "tvg": "TVGAL.TV",
    "tvg2": "TVG2.TV",
    "antena 3": "ANTENA3.TV",
    "telecinco": "TELECINCO.TV",
    "la sexta": "LASEXTA.TV",
    "cuatro": "CUATRO.TV",
    "24h": "24H.TV",
    "dmax": "DMAX.TV",
    "fdf": "FDF.TV",
    "paramount network": "PARAMOUNT.TV",
    "trece": "TRECE.TV",
    "realmadrid tv": "RMTV.TV",
    "clan": "CLAN.TV",
    "a3series": "A3SERIES.TV",
    "mega": "MEGA.TV",
    "bemad": "BEMAD.TV",
    "neox": "NEOX.TV",
    "nova": "NOVA.TV",
    "divinity": "DIVINITY.TV",
    "dkiss": "DKISS.TV",
    "squirrel": "Squirrel.es@SD",
    "energy": "ENERGY.TV",
    "tdp": "Teledeporte.es@SD",
    "ten": "TEN.TV",
    "boing": "BOING.TV",
}

DMAX_URL = "https://streaming.aurora.enhanced.live/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NjI0NTE1MzksIm5iZiI6MTc2MjQ1MTUzOSwiZXhwIjoxNzYyNDUxODk5LCJjb3VudHJ5Q29kZSI6ImVzIiwidWlwIjoiNzkuMTE2LjE4Mi4zMyJ9.bzxhLaIKA-3yHdC7ja06aWSYFWGZvJDnEwOrVENOjwU/live/es/b9243cdb24df40128098f3ea25fcf47d/index_3.m3u8"

def clean_name(name):
    return re.sub(r'\s+', ' ', name.strip().lower())

def parse_m3u(content):
    lines = content.strip().splitlines()
    channels = []
    i = 0
    while i < len(lines):
        if lines[i].startswith('#EXTINF'):
            if i + 1 < len(lines):
                extinf = lines[i]
                url = lines[i + 1]
                name = extinf.split(',', 1)[1] if ',' in extinf else ''
                channels.append((clean_name(name), extinf, url))
                i += 2
            else:
                i += 1
        else:
            i += 1
    return channels

def get_tvg_id(name_clean):
    return TVD_ID_MAP.get(name_clean, name_clean.upper().replace(" ", "") + ".TV")

def get_logo(name_clean):
    base = "https://www.tdtchannels.com/logos/"
    logo_map = {
        "la 1": "la1.png", "la 2": "la2.png", "tvg": "tvg.png", "tvg2": "tvg2.png",
        "antena 3": "antena3.png", "telecinco": "telecinco.png", "la sexta": "lasexta.png",
        "cuatro": "cuatro.png", "24h": "24h.png", "dmax": "dmax.png", "fdf": "fdf.png",
        "paramount network": "paramount.png", "trece": "trece.png", "clan": "clan.png",
        "a3series": "a3series.png", "mega": "mega.png", "bemad": "bemad.png",
        "neox": "neox.png", "nova": "nova.png", "divinity": "divinity.png",
        "dkiss": "dkiss.png", "energy": "energy.png", "ten": "ten.png", "boing": "boing.png",
        "realmadrid tv": "realmadrid.png", "squirrel": "squirrel.png", "tdp": "tdp.png"
    }
    return base + logo_map.get(name_clean, "default.png")

def main():
    print("📥 Descargando es.m3u...")
    resp = requests.get(SOURCE_URL)
    resp.raise_for_status()
    all_channels = parse_m3u(resp.text)

    output_lines = ['#EXTM3U url-tvg="https://www.tdtchannels.com/epg/TV.json"']
    for name_clean, extinf, url in all_channels:
        if name_clean in DESIRED_CHANNELS:
            tvg_id = get_tvg_id(name_clean)
            logo = get_logo(name_clean)
            orig_name = extinf.split(',', 1)[1] if ',' in extinf else name_clean

            if name_clean == "dmax":
                url = DMAX_URL

            new_extinf = f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{orig_name}" tvg-logo="{logo}" group-title="",{orig_name}'
            output_lines.append(new_extinf)
            output_lines.append(url)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(output_lines) + "\n")

    print(f"✅ Generado {OUTPUT_FILE} con {len(output_lines)//2} canales.")

if __name__ == "__main__":
    main()
