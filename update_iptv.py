import requests
import re

OUTPUT_FILE = "favoritos.m3u"
TDT_URL = "https://www.tdtchannels.com/lists/tv.m3u"

# URL fija para DMAX
DMAX_FIXED_URL = "https://streaming.aurora.enhanced.live/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NjI0NTE1MzksIm5iZiI6MTc2MjQ1MTUzOSwiZXhwIjoxNzYyNDUxODk5LCJjb3VudHJ5Q29kZSI6ImVzIiwidWlwIjoiNzkuMTE2LjE4Mi4zMyJ9.bzxhLaIKA-3yHdC7ja06aWSYFWGZvJDnEwOrVENOjwU/live/es/b9243cdb24df40128098f3ea25fcf47d/index_3.m3u8"

# Mapeo manual: tvg-id de tdtchannels → URL de iptv-org
# Este mapeo se construye manualmente comparando ambas listas
TDT_TO_IPTV_URL = {
    "RTVE1.TV": "https://live-edge01.rtve.es/live/la1/main.m3u8",  # La 1 HD
    "RTVE2.TV": "https://live-edge01.rtve.es/live/la2/main.m3u8",  # La 2 HD
    "TVGAL.TV": "https://livestartover.rtve.es/directo/tvg/master.m3u8",  # TVG
    "TVG2.TV": "https://livestartover.rtve.es/directo/tvg2/master.m3u8",  # TVG2
    "ANTENA3.TV": "https://antena3-live.flumotion.com/antena3/1/master.m3u8",  # Antena 3 HD
    "TELECINCO.TV": "https://telecinco-live.flumotion.com/telecinco/1/master.m3u8",  # Telecinco HD
    "LASEXTA.TV": "https://lasexta-live.flumotion.com/lasexta/1/master.m3u8",  # La Sexta HD
    "CUATRO.TV": "https://cuatro-live.flumotion.com/cuatro/1/master.m3u8",  # Cuatro HD
    "24H.TV": "https://24h-live.flumotion.com/24h/1/master.m3u8",  # 24h HD
    "FDF.TV": "https://fdf-live.flumotion.com/fdf/1/master.m3u8",  # FDF HD
    "PARAMOUNT.TV": "https://paramount-live.flumotion.com/paramount/1/master.m3u8",  # Paramount Network HD
    "TRECE.TV": "https://trece-live.flumotion.com/trece/1/master.m3u8",  # Trece HD
    "CLAN.TV": "https://clan-live.rtve.es/live/aclan/main.m3u8",  # Clan HD
    "A3SERIES.TV": "https://a3series-live.flumotion.com/a3series/1/master.m3u8",  # A3Series HD
    "MEGA.TV": "https://mega-live.flumotion.com/mega/1/master.m3u8",  # Mega HD
    "BEMAD.TV": "https://bemad-live.flumotion.com/bemad/1/master.m3u8",  # BeMad HD
    "NEOX.TV": "https://neox-live.flumotion.com/neox/1/master.m3u8",  # Neox HD
    "NOVA.TV": "https://nova-live.flumotion.com/nova/1/master.m3u8",  # Nova HD
    "DIVINITY.TV": "https://divinity-live.flumotion.com/divinity/1/master.m3u8",  # Divinity HD
    "DKISS.TV": "https://dkiss-live.flumotion.com/dkiss/1/master.m3u8",  # DKiss HD
    "ENERGY.TV": "https://energy-live.flumotion.com/energy/1/master.m3u8",  # Energy HD
    "TEN.TV": "https://ten-live.flumotion.com/ten/1/master.m3u8",  # Ten HD
    "BOING.TV": "https://boing-live.flumotion.com/boing/1/master.m3u8",  # Boing HD
    "RMTV.TV": "https://rmtv.akamaized.net/hls/live/2043824/rmtv/master.m3u8",  # Real Madrid TV
    "Squirrel.es@SD": "http://176.65.146.237:8401/play/a09h/index.m3u8",  # Squirrel
    "Teledeporte.es@SD": "https://d1cctoeg0n48w5.cloudfront.net/v1/master/3722c60a815c199d9c0ef36c5b73da68a62b09d1/cc-mnixw9wn5ugmv/TeledeporteES.m3u8",  # Teledeporte HD
    # DMAX se fuerza con URL fija
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

    # Generar salida
    output_lines = ['#EXTM3U url-tvg="https://www.tdtchannels.com/epg/TV.json"']
    for tvg_id, extinf, _ in tdt_channels:
        if tvg_id in TDT_TO_IPTV_URL:
            url = DMAX_FIXED_URL if tvg_id == "DMAX.TV" else TDT_TO_IPTV_URL[tvg_id]
            output_lines.append(extinf)
            output_lines.append(url)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(output_lines) + "\n")

    print(f"✅ Generado {OUTPUT_FILE} con {len(output_lines)//2} canales.")

if __name__ == "__main__":
    main()
