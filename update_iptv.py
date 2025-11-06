import requests
import re

OUTPUT_FILE = "favoritos.m3u"
SOURCE_URL = "https://iptv-org.github.io/iptv/countries/es.m3u"

# Nombres EXACTOS como aparecen en iptv-org (después de la coma en #EXTINF)
IPTV_ORG_NAMES = {
    "La 1", "La 2", "TVG", "Antena 3", "Telecinco", "La Sexta", "Cuatro", "24h",
    "DMAX", "FDF", "Paramount Network", "Trece", "Real Madrid TV", "Clan",
    "A3Series", "Mega", "BeMad", "Neox", "Nova", "Divinity", "DKiss",
    "Squirrel", "Energy", "Teledeporte", "Ten", "Boing", "TVG2"
}

# Mapeo: nombre en iptv-org → tvg-id
TVD_ID_MAP = {
    "La 1": "RTVE1.TV",
    "La 2": "RTVE2.TV",
    "TVG": "TVGAL.TV",
    "TVG2": "TVG2.TV",
    "Antena 3": "ANTENA3.TV",
    "Telecinco": "TELECINCO.TV",
    "La Sexta": "LASEXTA.TV",
    "Cuatro": "CUATRO.TV",
    "24h": "24H.TV",
    "DMAX": "DMAX.TV",
    "FDF": "FDF.TV",
    "Paramount Network": "PARAMOUNT.TV",
    "Trece": "TRECE.TV",
    "Real Madrid TV": "RMTV.TV",
    "Clan": "CLAN.TV",
    "A3Series": "A3SERIES.TV",
    "Mega": "MEGA.TV",
    "BeMad": "BEMAD.TV",
    "Neox": "NEOX.TV",
    "Nova": "NOVA.TV",
    "Divinity": "DIVINITY.TV",
    "DKiss": "DKISS.TV",
    "Squirrel": "Squirrel.es@SD",
    "Energy": "ENERGY.TV",
    "Teledeporte": "Teledeporte.es@SD",
    "Ten": "TEN.TV",
    "Boing": "BOING.TV",
}

# Logos
def get_logo(name):
    slug = name.lower().replace(" ", "").replace("real madrid tv", "realmadrid")
    logo_map = {
        "la1": "la1.png", "la2": "la2.png", "tvg": "tvg.png", "tvg2": "tvg2.png",
        "antena3": "antena3.png", "telecinco": "telecinco.png", "lasexta": "lasexta.png",
        "cuatro": "cuatro.png", "24h": "24h.png", "dmax": "dmax.png", "fdf": "fdf.png",
        "paramountnetwork": "paramount.png", "trece": "trece.png", "realmadrid": "realmadrid.png",
        "clan": "clan.png", "a3series": "a3series.png", "mega": "mega.png", "bemad": "bemad.png",
        "neox": "neox.png", "nova": "nova.png", "divinity": "divinity.png", "dkiss": "dkiss.png",
        "squirrel": "squirrel.png", "energy": "energy.png", "teledeporte": "tdp.png", "ten": "ten.png",
        "boing": "boing.png"
    }
    key = re.sub(r'[^a-z0-9]', '', slug)
    return "https://www.tdtchannels.com/logos/" + logo_map.get(key, "default.png")

# URL fija para DMAX
DMAX_URL = "https://streaming.aurora.enhanced.live/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NjI0NTE1MzksIm5iZiI6MTc2MjQ1MTUzOSwiZXhwIjoxNzYyNDUxODk5LCJjb3VudHJ5Q29kZSI6ImVzIiwidWlwIjoiNzkuMTE2LjE4Mi4zMyJ9.bzxhLaIKA-3yHdC7ja06aWSYFWGZvJDnEwOrVENOjwU/live/es/b9243cdb24df40128098f3ea25fcf47d/index_3.m3u8"

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
                channels.append((name, extinf, url))
                i += 2
            else:
                i += 1
        else:
            i += 1
    return channels

def main():
    print("📥 Descargando es.m3u...")
    resp = requests.get(SOURCE_URL)
    resp.raise_for_status()
    all_channels = parse_m3u(resp.text)

    output_lines = ['#EXTM3U url-tvg="https://www.tdtchannels.com/epg/TV.json"']
    for name, extinf, url in all_channels:
        if name in IPTV_ORG_NAMES:
            tvg_id = TVD_ID_MAP[name]
            logo = get_logo(name)
            # Usar nombre original para mostrar
            new_extinf = f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{name}" tvg-logo="{logo}" group-title="",{name}'
            final_url = DMAX_URL if name == "DMAX" else url
            output_lines.append(new_extinf)
            output_lines.append(final_url)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(output_lines) + "\n")

    print(f"✅ Generado {OUTPUT_FILE} con {len(output_lines)//2} canales.")

if __name__ == "__main__":
    main()
