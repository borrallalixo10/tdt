import re
from pathlib import Path

# Mapeo de nombres de canales para hacerlos compatibles con el EPG
EPG_CHANNEL_MAPPING = {
    "La1.es@SD": "La 1.es",
    "La2.es@SD": "La 2.es",
    "Antena3.es@National": "Antena 3.es",
    "Telecinco.es@SD": "Telecinco.es",
    "Cuatro.es@SD": "Cuatro.es",
    "24Horas.es@SD": "24 Horas.es",
    "Clan.es@SD": "Clan.es",
    "ParamountNetwork.es@SD": "Paramount Network.es",
    "Trece.es@SD": "Trece.es",
    "RealMadridTV.es@SD": "Real Madrid TV.es",
    "Teledeporte.es@SD": "Teledeporte.es",
    "Divinity.es@SD": "Divinity.es",
    "dmax": "DMAX.es",
    "FactoriadeFiccion.es@SD": "Factoría de Ficción.es",
    "Atreseries.es@SD": "Atreseries.es",
    "Mega.es@SD": "Mega.es",
    "BeMad.es@SD": "Be Mad.es",
    "Neox.es@SD": "Neox.es",
    "Nova.es@SD": "Nova.es",
    "Squirrel.es@SD": "Squirrel.es",
    "Energy.es@SD": "Energy.es",
    "TEN.es@SD": "TEN.es",
    "TVG2.es@SD": "TVG2.es",
}

def normalize_channel_name(name):
    """Normaliza el nombre del canal según el mapeo."""
    return EPG_CHANNEL_MAPPING.get(name.strip(), name.strip())

def fix_m3u_for_epg(file_path):
    """Actualiza los nombres de los canales en el archivo M3U para que coincidan con el EPG."""
    # Leer el archivo M3U
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    updated_lines = []
    for line in lines:
        if line.startswith("#EXTINF"):
            # Extraer el valor de tvg-id
            match = re.search(r'tvg-id="([^"]+)"', line)
            if match:
                old_tvg_id = match.group(1)
                new_tvg_id = normalize_channel_name(old_tvg_id)

                # Reemplazar el tvg-id en la línea
                line = line.replace(f'tvg-id="{old_tvg_id}"', f'tvg-id="{new_tvg_id}"')

        updated_lines.append(line)

    # Sobrescribir el archivo M3U con las líneas actualizadas
    with open(file_path, "w", encoding="utf-8") as file:
        file.writelines(updated_lines)

if __name__ == "__main__":
    # Ruta del archivo M3U
    m3u_file = Path("favoritos.m3u")

    # Actualizar el archivo M3U
    fix_m3u_for_epg(m3u_file)
    print("Archivo M3U actualizado para compatibilidad con EPG.")
