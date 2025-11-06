import requests
import re

OUTPUT_FILE = "favoritos.m3u"
SOURCE_URL = "https://iptv-org.github.io/iptv/countries/es.m3u"

# Lista de tvg-id que queremos (según tdtchannels + tus correcciones)
DESIRED_TVG_IDS = {
    "RTVE1.TV", "RTVE2.TV", "TVGAL.TV", "TVG2.TV", "ANTENA3.TV", "TELECINCO.TV",
    "LASEXTA.TV", "CUATRO.TV", "24H.TV", "DMAX.TV", "FDF.TV", "PARAMOUNT.TV",
    "TRECE.TV", "RMTV.TV", "CLAN.TV", "A3SERIES.TV", "MEGA.TV", "BEMAD.TV",
    "NEOX.TV", "NOVA.TV", "DIVINITY.TV", "DKISS.TV", "Squirrel.es@SD",
    "ENERGY.TV", "Teledeporte.es@SD", "TEN.TV", "BOING.TV"
}

# Mapeo inverso: tvg-id → nombre para mostrar y logo
TV_INFO = {
    "RTVE1.TV": ("La 1", "la1.png"),
    "RTVE2.TV": ("La 2", "la2.png"),
    "TVGAL.TV": ("TVG", "tvg.png"),
    "TVG2.TV": ("TVG2", "tvg2.png"),
    "ANTENA3.TV": ("Antena 3", "antena3.png"),
    "TELECINCO.TV": ("Telecinco", "telecinco.png"),
    "LASEXTA.TV": ("La Sexta", "lasexta.png"),
    "CUATRO.TV": ("Cuatro", "cuatro.png"),
    "24H.TV": ("24h", "24h.png"),
    "DMAX.TV": ("DMAX", "dmax.png"),
    "FDF.TV": ("FDF", "fdf.png"),
    "PARAMOUNT.TV": ("Paramount Network", "paramount.png"),
    "TRECE.TV": ("Trece", "trece.png"),
    "RMTV.TV": ("Real Madrid TV", "realmadrid.png"),
    "CLAN.TV": ("Clan", "clan.png"),
    "A3SERIES.TV": ("A3Series", "a3series.png"),
    "MEGA.TV": ("Mega", "mega.png"),
    "BEMAD.TV": ("BeMad", "bemad.png"),
    "NEOX.TV": ("Neox", "neox.png"),
    "NOVA.TV": ("Nova", "nova.png"),
    "DIVINITY.TV": ("Divinity", "divinity.png"),
    "DKISS.TV": ("DKiss", "dkiss.png"),
    "Squirrel.es@SD": ("Squirrel", "squirrel.png"),
    "ENERGY.TV": ("Energy", "energy.png"),
    "Teledeporte.es@SD": ("Teledeporte", "tdp.png"),
    "TEN.TV": ("Ten", "ten.png"),
    "BOING.TV": ("Boing", "boing.png"),
}

DMAX_URL = "https://streaming.aurora.enhanced.live/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NjI0NTE1MzksIm5iZiI6MTc2MjQ1MTUzOSwiZXhwIjoxNzYyNDUxODk5LCJjb3VudHJ5Q29kZSI6ImVzIiwidWlwIjoiNzkuMTE2LjE4Mi4zMyJ9.bzxhLaIKA-3yHdC7ja06aWSYFWGZvJDnEwOrVENOjwU/live/es/b9243cdb24df40128098f3ea25fcf47d/index_3.m3u8"

def parse_m3u_with_tvg(content):
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
                name = extinf.split(',', 1)[1] if ',' in extinf else tvg_id
                channels.append((tvg_id, name, url))
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
    all_channels = parse_m3u_with_tvg(resp.text)

    output_lines = ['#EXTM3U url-tvg="https://www.tdtchannels.com/epg/TV.json"']
    for tvg_id, original_name, url in all_channels:
        if tvg_id in DESIRED_TVG_IDS:
            display_name, logo_file = TV_INFO[tvg_id]
            logo_url = f"https://www.tdtchannels.com/logos/{logo_file}"
            final_url = DMAX_URL if tvg_id == "DMAX.TV" else url
            output_lines.append(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{display_name}" tvg-logo="{logo_url}" group-title="",{display_name}')
            output_lines.append(final_url)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(output_lines) + "\n")

    print(f"✅ Generado {OUTPUT_FILE} con {len(output_lines)//2} canales.")

if __name__ == "__main__":
    main()
