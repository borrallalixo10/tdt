# generate_channels.py
import re
import sys

def main():
    playlist_file = 'favoritos.m3u'
    output_file = 'playlist.m3u'

    try:
        with open(playlist_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{playlist_file}'.")
        sys.exit(1)

    lines = content.strip().split('\n')
    channels = []
    i = 0
    while i < len(lines):
        if lines[i].startswith('#EXTINF:'):
            extinf_line = lines[i]
            if i + 1 < len(lines):
                url = lines[i + 1]
                # Buscar el tvg-id en la línea EXTINF
                tvg_id_match = re.search(r'tvg-id="([^"]*)"', extinf_line)
                if tvg_id_match:
                    tvg_id = tvg_id_match.group(1)
                    # Añadir la línea EXTINF y la URL al canal
                    channels.append((extinf_line, url))
                i += 2
            else:
                i += 1
        else:
            i += 1

    if not channels:
        print("No se encontraron canales con tvg-id en el archivo.")
        return

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        for extinf, url in channels:
            f.write(extinf + '\n')
            f.write(url + '\n')

    print(f"Archivo '{output_file}' generado con {len(channels)} canales.")


if __name__ == "__main__":
    main()
