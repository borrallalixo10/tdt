import requests
import re

# URLs de las fuentes
TDT_CHANNELS_URL = "https://www.tdtchannels.com/lists/tv.m3u"
IPTV_ORG_ES_URL = "https://iptv-org.github.io/iptv/countries/es.m3u"

# URL fija para DMAX
DMAX_FIXED_URL = "https://streaming.aurora.enhanced.live/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NjI0NTE1MzksIm5iZiI6MTc2MjQ1MTUzOSwiZXhwIjoxNzYyNDUxODk5LCJjb3VndHJ5Q29kZSI6ImVzIiwidWlwIjoiNzkuMTE2LjE4Mi4zMyJ9.bzxhLaIKA-3yHdC7ja06aWSYFWGZvJDnEwOrVENOjwU/live/es/b9243cdb24df40128098f3ea25fcf47d/index_3.m3u8"

# Lista de tvg-id de tdtchannels para los canales principales (favoritos)
FAVORITOS_TVG_IDS = {
    "RTVE1.TV",      # La 1
    "RTVE2.TV",      # La 2
    "TVGAL.TV",      # TVG
    "ANTENA3.TV",    # Antena 3
    "TELECINCO.TV",  # Telecinco
    "LASEXTA.TV",    # La Sexta
    "CUATRO.TV",     # Cuatro
    "24H.TV",        # 24h
    "DMAX.TV",       # DMAX
    "FDF.TV",        # FDF
    "PARAMOUNT.TV",  # Paramount Network
    "TRECE.TV",      # Trece
    "RMTV.TV",       # Real Madrid TV
    "CLAN.TV",       # Clan
    "A3SERIES.TV",   # A3Series
    "MEGA.TV",       # Mega
    "BEMAD.TV",      # BeMad
    "NEOX.TV",       # Neox
    "NOVA.TV",       # Nova
    "DIVINITY.TV",   # Divinity
    "Squirrel.es@SD", # Squirrel
    "ENERGY.TV",     # Energy
    "Teledeporte.es@SD", # TDP (Teledeporte)
    "TEN.TV",        # Ten
    "TVG2.TV",       # TVG2
    # Añadir aquí si se quiere incluir BOING.TV
}

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
    print("📥 Descargando listas...")
    tdt_resp = requests.get(TDT_CHANNELS_URL)
    tdt_resp.raise_for_status()
    tdt_channels = parse_m3u(tdt_resp.text)

    iptv_resp = requests.get(IPTV_ORG_ES_URL)
    iptv_resp.raise_for_status()
    iptv_channels = parse_m3u(iptv_resp.text)

    # Crear mapa de tvg-id -> (extinf, url) para iptv-org
    iptv_map = {tvg_id: (extinf, url) for tvg_id, extinf, url in iptv_channels if tvg_id}

    # --- Procesar favoritos ---
    favoritos_output = ['#EXTM3U url-tvg="https://www.tdtchannels.com/epg/TV.json"']
    otros_output = ['#EXTM3U']

    # Mapeo de tvg-id de tdtchannels al tvg-id de iptv-org
    # Basado en tu lista y en coincidencias de nombre/contenido
    # Si no hay coincidencia directa, se puede intentar mapeo manual
    # Este mapeo se basa en la información que proporcionaste
    tdt_to_iptv_map = {
        "RTVE1.TV": "La1.es@SD",
        "RTVE2.TV": "La2.es@SD",
        "TVGAL.TV": "TVG.es@SD", # Asumiendo que existe en iptv-org, si no, usar la URL fija de tdtchannels o vacío
        "ANTENA3.TV": "Antena3.es@National",
        "TELECINCO.TV": "Telecinco.es@SD",
        "LASEXTA.TV": "LaSexta.es@SD",
        "CUATRO.TV": "Cuatro.es@SD",
        "24H.TV": "24Horas.es@SD",
        "DMAX.TV": "DMAX.es@SD", # Asumiendo este tvg-id en iptv-org
        "FDF.TV": "FactoriadeFiccion.es@SD",
        "PARAMOUNT.TV": "ParamountNetwork.es@SD",
        "TRECE.TV": "Trece.es@SD",
        "RMTV.TV": "RealMadridTV.es@SD",
        "CLAN.TV": "Clan.es@SD",
        "A3SERIES.TV": "Atreseries.es@SD",
        "MEGA.TV": "Mega.es@SD",
        "BEMAD.TV": "BeMad.es@SD",
        "NEOX.TV": "Neox.es@SD",
        "NOVA.TV": "Nova.es@SD",
        "DIVINITY.TV": "Divinity.es@SD",
        # "DKISS.TV": "DKiss.es@SD", # No incluido en favoritos
        "Squirrel.es@SD": "Squirrel.es@SD", # Id ya compatible
        "ENERGY.TV": "Energy.es@SD",
        "Teledeporte.es@SD": "Teledeporte.es@SD", # Id ya compatible
        "TEN.TV": "TEN.es@SD",
        "TVG2.TV": "TVG2.es@SD",
        # "BOING.TV": "Boing.es@SD", # No incluido en favoritos
    }

    # Obtener los EXTINF de tdtchannels
    tdt_map = {tvg_id: (extinf, url) for tvg_id, extinf, url in tdt_channels if tvg_id}

    for tvg_id in FAVORITOS_TVG_IDS:
        if tvg_id in tdt_map:
            tdt_extinf, _ = tdt_map[tvg_id]
            iptv_tvg_id = tdt_to_iptv_map.get(tvg_id)
            stream_url = None
            if tvg_id == "DMAX.TV" and DMAX_FIXED_URL:
                stream_url = DMAX_FIXED_URL
            elif iptv_tvg_id and iptv_tvg_id in iptv_map:
                _, stream_url = iptv_map[iptv_tvg_id]

            if stream_url:
                # Modificar el EXTINF para usar group-title="tdt"
                # Buscar y reemplazar group-title
                updated_extinf = re.sub(r'group-title="[^"]*"', 'group-title="tdt"', tdt_extinf)
                # Si no existe group-title, añadirlo
                if 'group-title=' not in updated_extinf:
                    updated_extinf = updated_extinf.replace(',', ' group-title="tdt",')
                
                favoritos_output.append(updated_extinf)
                favoritos_output.append(stream_url)

    # --- Procesar otros ---
    # Canales de tdtchannels que no están en FAVORITOS_TVG_IDS
    for tvg_id, (extinf, url) in tdt_map.items():
        if tvg_id not in FAVORITOS_TVG_IDS:
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
