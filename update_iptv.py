import requests
import re

OUTPUT_FILE = "favoritos.m3u"
SOURCE_URL = "https://iptv-org.github.io/iptv/countries/es.m3u"

# Mapeo: nombre exacto en es.m3u → tvg-id de tdtchannels
NAME_TO_TVGID = {
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
    "Boing": "BOING.TV"
}

# Logos
def get_logo(name):
    slug_map = {
        "La 1": "la1.png", "La 2": "la2.png", "TVG": "tvg.png", "TVG2": "tvg2.png",
        "Antena 3": "antena3.png", "Telecinco": "telecinco.png", "La Sexta": "lasexta.png",
        "Cuatro": "cuatro.png", "24h": "24h.png", "DMAX": "dmax.png", "FDF": "fdf.png",
        "Paramount Network": "paramount.png", "Trece": "trece.png", "Real Madrid TV": "realmadrid.png",
        "Clan": "clan.png", "A3Series": "a3series.png", "Mega": "mega.png", "BeMad": "bemad.png",
        "Neox": "neox.png", "Nova": "nova.png", "Divinity": "divinity.png", "DKiss": "dkiss.png",
        "Squirrel": "squirrel.png", "Energy": "energy.png", "Teledeporte": "tdp.png", "Ten": "ten.png",
        "Boing": "boing.png"
    }
    return "https://www.tdtchannels.com/logos/" + slug_map.get(name, "default.png")

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
                channels.append((name, url))
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
    for name, url in all_channels:
        if name in NAME_TO_TVGID:
            tvg_id = NAME_TO_TVGID[name]
            logo = get_logo(name)
            final_url = DMAX_URL if name == "DMAX" else url
            output_lines.append(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{name}" tvg-logo="{logo}" group-title="",{name}')
            output_lines.append(final_url)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(output_lines) + "\n")

    print(f"✅ Generado {OUTPUT_FILE} con {len(output_lines)//2} canales.")

if __name__ == "__main__":
    main()
