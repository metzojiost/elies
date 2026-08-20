"""
Download an Esri World Imagery tile mosaic covering a parcel's bounding box
(with padding), stitch it into one image, and overlay the parcel boundary.

Usage: python fetch_satellite.py data/parcels/parcel_01_boundary.geojson
Writes: data/parcels/imagery/<name>_satellite.png (plain)
        data/parcels/imagery/<name>_satellite_annotated.png (boundary overlay)
"""
import json
import math
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw

TILE_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
ZOOM = 18
TILE_SIZE = 256
PAD_FRACTION = 0.35  # extra context around the parcel


def lonlat_to_tile(lon, lat, z):
    n = 2 ** z
    xt = (lon + 180.0) / 360.0 * n
    lat_rad = math.radians(lat)
    yt = (1 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2 * n
    return xt, yt


def main():
    geojson_path = Path(sys.argv[1])
    gj = json.loads(geojson_path.read_text(encoding="utf-8"))
    coords = gj["geometry"]["coordinates"][0]
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    minlon, maxlon = min(lons), max(lons)
    minlat, maxlat = min(lats), max(lats)
    padlon = (maxlon - minlon) * PAD_FRACTION
    padlat = (maxlat - minlat) * PAD_FRACTION
    minlon, maxlon = minlon - padlon, maxlon + padlon
    minlat, maxlat = minlat - padlat, maxlat + padlat

    x1f, y1f = lonlat_to_tile(minlon, maxlat, ZOOM)  # top-left (north-west)
    x2f, y2f = lonlat_to_tile(maxlon, minlat, ZOOM)  # bottom-right (south-east)

    xtile_min, xtile_max = int(math.floor(x1f)), int(math.floor(x2f))
    ytile_min, ytile_max = int(math.floor(y1f)), int(math.floor(y2f))

    n_cols = xtile_max - xtile_min + 1
    n_rows = ytile_max - ytile_min + 1
    print(f"Fetching {n_cols}x{n_rows} tiles at zoom {ZOOM}...")

    mosaic = Image.new("RGB", (n_cols * TILE_SIZE, n_rows * TILE_SIZE))
    for row, yt in enumerate(range(ytile_min, ytile_max + 1)):
        for col, xt in enumerate(range(xtile_min, xtile_max + 1)):
            url = TILE_URL.format(z=ZOOM, y=yt, x=xt)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
            tile_path = Path("data/parcels/imagery/_tmp_tile.jpg")
            tile_path.write_bytes(data)
            tile_img = Image.open(tile_path).convert("RGB")
            mosaic.paste(tile_img, (col * TILE_SIZE, row * TILE_SIZE))

    out_dir = Path("data/parcels/imagery")
    out_dir.mkdir(parents=True, exist_ok=True)
    base_name = geojson_path.stem.replace("_boundary", "")
    plain_path = out_dir / f"{base_name}_satellite.png"
    mosaic.save(plain_path)
    print(f"Saved plain mosaic: {plain_path}  ({mosaic.width}x{mosaic.height}px)")

    # Overlay parcel boundary
    def lonlat_to_px(lon, lat):
        xt, yt = lonlat_to_tile(lon, lat, ZOOM)
        px = (xt - xtile_min) * TILE_SIZE
        py = (yt - ytile_min) * TILE_SIZE
        return px, py

    annotated = mosaic.copy()
    draw = ImageDraw.Draw(annotated)
    poly_px = [lonlat_to_px(lon, lat) for lon, lat in coords]
    draw.line(poly_px + [poly_px[0]], fill=(255, 255, 0), width=4)

    annotated_path = out_dir / f"{base_name}_satellite_annotated.png"
    annotated.save(annotated_path)
    print(f"Saved annotated mosaic: {annotated_path}")

    (out_dir / "_tmp_tile.jpg").unlink(missing_ok=True)


if __name__ == "__main__":
    main()
