#!/usr/bin/env python3
import requests
import json
import re
import os
import sys

# URL de la lista de iptv-org para España
IPTV_ORG_ES_URL = "https://iptv-org.github.io/iptv/countries/es.m3u"

# Archivo de equivalencias (ubicado en el mismo directorio del script)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EQUIVALENCIAS_FILE = os.path.join(BASE_DIR, "equivalencias.json")

# URL fija para DMAX
DMAX_FIXED_URL = "https://streaming.aurora.enhanced.live/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NjI0NTE1MzksIm5iZiI6MTc2MjQ1MTUzOSwiZXhwIjoxNzYyNDUxODk5LCJjb3VudHJ5Q29kZSI6ImVzIiwidWlwIjoiNzkuMTE2LjE4Mi4zMyJ9.bzxhLaIKA-3yHdC7ja06aWSYFWGZvJDnEwOrVENOjwU/live/es/b9243cdb24df40128098f3ea25fcf47d/index_3.m3u8"

VARIANT_HINTS = (
    "internacional",
    "canarias",
    "catalunya",
    "cataluna",
    "catala",
    "latin",
    "latam",
    "usa",
)

def normalize_token(value):
    """Normaliza texto para comparaciones robustas (minúsculas + alfanumérico)."""
    return re.sub(r'[^a-z0-9]+', '', (value or "").lower())

def extract_channel_name(extinf):
    """Extrae el nombre visible del canal de una línea #EXTINF."""
    if "," not in extinf:
        return ""
    return extinf.split(",", 1)[1].strip()

def parse_m3u(content):
    """Parsea una lista M3U y devuelve una lista de canales con tvg_id/extinf/url/nombre."""
    raw_lines = content.splitlines()
    lines = [ln for ln in raw_lines]
    channels = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.upper().startswith('#EXTINF'):
            extinf = lines[i].rstrip('\r\n')
            # buscar siguiente línea no vacía como URL
            j = i + 1
            url = ""
            while j < len(lines):
                candidate = lines[j].strip()
                if candidate == "":
                    j += 1
                    continue
                if candidate.upper().startswith("#EXTINF"):
                    break
                if candidate.startswith("#"):
                    j += 1
                    continue
                url = candidate
                j += 1
                break
            # Extraer tvg-id si existe
            tvg_id_match = re.search(r'tvg-id="([^"]+)"', extinf)
            tvg_id = tvg_id_match.group(1) if tvg_id_match else ""
            channels.append({
                "tvg_id": tvg_id,
                "extinf": extinf,
                "url": url,
                "name": extract_channel_name(extinf),
            })
            i = j
        else:
            i += 1
    return channels

def load_equivalencias(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: no se encontró '{path}'.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error al parsear JSON en '{path}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error al leer '{path}': {e}")
        sys.exit(1)

    # Construir lista de reglas de equivalencia
    equivalencias = []
    for nombre_norm, info in data.items():
        if not isinstance(info, dict):
            continue
        tvg = info.get("tvg_id") or info.get("tvgid") or ""
        orden = info.get("orden", 0)
        try:
            orden = int(orden)
        except (TypeError, ValueError):
            orden = 0
        equivalencias.append({
            "key": nombre_norm,
            "key_norm": normalize_token(nombre_norm),
            "tvg_id": tvg,
            "tvg_id_norm": normalize_token(tvg),
            "tvg_root_norm": normalize_token((tvg.split("@", 1)[0]).split(".", 1)[0]),
            "orden": orden,
        })
    return equivalencias

def match_score(entry, channel):
    """Devuelve una tupla de score (menor es mejor) o None si no hay match."""
    ch_tvg = channel["tvg_id"]
    ch_tvg_norm = normalize_token(ch_tvg)
    ch_name_norm = normalize_token(channel["name"])
    target_tvg = entry["tvg_id"]
    target_tvg_norm = entry["tvg_id_norm"]
    aliases = [entry["key_norm"], entry["tvg_root_norm"]]

    if target_tvg and ch_tvg == target_tvg:
        base = 0
    elif target_tvg_norm and ch_tvg_norm == target_tvg_norm:
        base = 1
    else:
        alias_bases = []
        for alias in aliases:
            if not alias:
                continue
            if alias == ch_name_norm or alias == ch_tvg_norm:
                alias_bases.append(2)
                continue
            if ch_name_norm.startswith(alias) or ch_tvg_norm.startswith(alias):
                alias_bases.append(3)
                continue
            # Solo permitir "contains" en aliases largos para evitar falsos positivos
            if len(alias) >= 5 and (alias in ch_name_norm or alias in ch_tvg_norm):
                alias_bases.append(4)
        if not alias_bases:
            return None
        base = min(alias_bases)

    lower_text = f'{channel["name"]} {ch_tvg}'.lower()
    variant_penalty = 1 if any(hint in lower_text for hint in VARIANT_HINTS) else 0
    specificity = len(ch_name_norm) if ch_name_norm else len(ch_tvg_norm)
    return (base, variant_penalty, specificity)

def main():
    print("📥 Descargando lista de iptv-org...")
    try:
        resp = requests.get(IPTV_ORG_ES_URL, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Error al descargar {IPTV_ORG_ES_URL}: {e}")
        sys.exit(1)

    iptv_channels = parse_m3u(resp.text)

    equivalencias = load_equivalencias(EQUIVALENCIAS_FILE)

    selected = {}  # key_equivalencia -> datos de mejor match
    for idx, channel in enumerate(iptv_channels):
        if not channel["url"]:
            continue
        for entry in equivalencias:
            score = match_score(entry, channel)
            if score is None:
                continue
            current = selected.get(entry["key"])
            if current is None or score < current["score"]:
                selected[entry["key"]] = {
                    "score": score,
                    "orden": entry["orden"],
                    "extinf": channel["extinf"],
                    "url": channel["url"],
                    "idx": idx,
                }

    # Lista final de favoritos y seguimiento de canales ya clasificados
    favoritos_list = []  # elementos: (orden, extinf, url)
    used_indexes = set()
    otros_output = ['#EXTM3U']

    missing = []
    for entry in sorted(equivalencias, key=lambda e: e["orden"]):
        key = entry["key"]
        if key.lower() == "dmax":
            favoritos_list.append((entry["orden"], '#EXTINF:-1 tvg-id="dmax" group-title="General",DMAX', DMAX_FIXED_URL))
            if key in selected:
                used_indexes.add(selected[key]["idx"])
            continue

        best = selected.get(key)
        if best:
            favoritos_list.append((best["orden"], best["extinf"], best["url"]))
            used_indexes.add(best["idx"])
        else:
            missing.append(key)

    for idx, channel in enumerate(iptv_channels):
        if idx in used_indexes or not channel["url"]:
            continue
        otros_output.append(channel["extinf"])
        otros_output.append(channel["url"])

    # Ordenar favoritos por 'orden'
    favoritos_list.sort(key=lambda x: x[0])

    favoritos_output = ['#EXTM3U']
    for _, extinf, url in favoritos_list:
        favoritos_output.append(extinf)
        favoritos_output.append(url)

    # Escribir archivos
    try:
        with open(os.path.join(BASE_DIR, 'favoritos.m3u'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(favoritos_output) + '\n')
        num_fav = (len(favoritos_output) - 1) // 2
        print(f"✅ Generado favoritos.m3u con {num_fav} canales.")
        if missing:
            print(f"⚠️ No se encontraron {len(missing)} favoritos: {', '.join(missing)}")
    except Exception as e:
        print(f"Error al escribir 'favoritos.m3u': {e}")
        sys.exit(1)

    try:
        with open(os.path.join(BASE_DIR, 'otros.m3u'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(otros_output) + '\n')
        num_otros = (len(otros_output) - 1) // 2
        print(f"✅ Generado otros.m3u con {num_otros} canales.")
    except Exception as e:
        print(f"Error al escribir 'otros.m3u': {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
