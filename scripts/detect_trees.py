"""
Best-effort tree canopy detection on a satellite mosaic, restricted to the
parcel polygon. This is a heuristic (color threshold + blob detection) meant
to produce a candidate count and marked image for FIELD VERIFICATION, not a
precise survey — merged canopies in dense/overgrown areas will undercount,
and non-olive shrub canopies of similar color may be picked up as false
positives.

Usage: python detect_trees.py data/parcels/parcel_01_boundary.geojson
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ZOOM = 18
TILE_SIZE = 256

# canopy area range in m^2 we'll accept as "one tree" (rough, for old wide-canopy
# olives this is generous on the high end since old trees can be large)
MIN_CANOPY_M2 = 3.0
MAX_CANOPY_M2 = 90.0


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
    base_name = geojson_path.stem.replace("_boundary", "")

    img_dir = Path("data/parcels/imagery")
    mosaic_path = img_dir / f"{base_name}_satellite.png"
    img = Image.open(mosaic_path).convert("RGB")
    arr = np.array(img).astype(np.float32)

    # need the same tile origin used by fetch_satellite.py to convert lon/lat -> px
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    minlon, maxlon = min(lons), max(lons)
    minlat, maxlat = min(lats), max(lats)
    padlon = (maxlon - minlon) * 0.35
    padlat = (maxlat - minlat) * 0.35
    minlon, maxlon = minlon - padlon, maxlon + padlon
    minlat, maxlat = minlat - padlat, maxlat + padlat
    x1f, y1f = lonlat_to_tile(minlon, maxlat, ZOOM)
    xtile_min = int(math.floor(x1f))
    ytile_min = int(math.floor(y1f))

    def lonlat_to_px(lon, lat):
        xt, yt = lonlat_to_tile(lon, lat, ZOOM)
        return (xt - xtile_min) * TILE_SIZE, (yt - ytile_min) * TILE_SIZE

    poly_px = [lonlat_to_px(lon, lat) for lon, lat in coords]

    # polygon mask
    mask_img = Image.new("L", (img.width, img.height), 0)
    ImageDraw.Draw(mask_img).polygon(poly_px, fill=1)
    poly_mask = np.array(mask_img).astype(bool)

    # vegetation "darkness/greenness" heuristic: olive/shrub canopy reads as
    # darker + greener than bare dirt/rock in this imagery
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    excess_green = 2 * g - r - b
    brightness = (r + g + b) / 3

    # Adaptive, per-image thresholds: canopy = darker + greener than most of
    # this specific parcel's ground cover. Fixed absolute thresholds don't
    # transfer between parcels with very different soil/vegetation color
    # (e.g. dense dark maquis vs. open sunlit grey-green olive rows), so we
    # threshold at percentiles of the in-polygon distribution instead.
    bright_thresh = np.percentile(brightness[poly_mask], 40)
    green_thresh = np.percentile(excess_green[poly_mask], 60)
    print(f"Adaptive thresholds: brightness < {bright_thresh:.1f}, excess_green > {green_thresh:.1f}")

    canopy_mask = (excess_green > green_thresh) & (brightness < bright_thresh) & poly_mask

    # clean up speckle noise, and separate touching blobs a bit
    canopy_mask = ndimage.binary_opening(canopy_mask, structure=np.ones((3, 3)))

    labeled, n_labels = ndimage.label(canopy_mask, structure=np.ones((3, 3)))

    # resolution at this latitude/zoom
    lat0 = (minlat + maxlat) / 2
    m_per_px = 156543.03392 * math.cos(math.radians(lat0)) / (2 ** ZOOM)
    m2_per_px2 = m_per_px ** 2

    sizes = ndimage.sum(canopy_mask, labeled, range(1, n_labels + 1))
    centers = ndimage.center_of_mass(canopy_mask, labeled, range(1, n_labels + 1))

    trees = []
    for size_px, (cy, cx) in zip(sizes, centers):
        area_m2 = size_px * m2_per_px2
        if MIN_CANOPY_M2 <= area_m2 <= MAX_CANOPY_M2:
            # crude split: very large blobs are probably 2+ merged canopies
            est_count = max(1, round(area_m2 / 20.0))
            trees.append((cx, cy, area_m2, est_count))

    total_est = sum(t[3] for t in trees)

    debug_path = img_dir / f"{base_name}_candidates_debug.csv"
    with open(debug_path, "w", encoding="utf-8") as f:
        f.write("index,area_m2,est_count\n")
        for i, (cx, cy, area_m2, est_count) in enumerate(trees, start=1):
            f.write(f"{i},{area_m2:.1f},{est_count}\n")
    print(f"Saved per-marker debug data: {debug_path}")

    print(f"Resolution: ~{m_per_px:.2f} m/pixel")
    print(f"Candidate canopy blobs (in size range): {len(trees)}")
    print(f"Estimated tree count (merged blobs split by area/20m2 heuristic): {total_est}")

    # annotate
    annotated = img.copy()
    draw = ImageDraw.Draw(annotated)
    draw.polygon(poly_px, outline=(255, 255, 0), width=3)
    for i, (cx, cy, area_m2, est_count) in enumerate(trees, start=1):
        r_px = 5
        color = (255, 0, 0) if est_count == 1 else (255, 128, 0)
        draw.ellipse([cx - r_px, cy - r_px, cx + r_px, cy + r_px], outline=color, width=2)
        draw.text((cx + 6, cy - 6), str(i), fill=color)

    out_path = img_dir / f"{base_name}_tree_candidates.png"
    annotated.save(out_path)
    print(f"Saved annotated candidate image: {out_path}")

    # also save 2x upscaled for readability
    up = annotated.resize((annotated.width * 2, annotated.height * 2), Image.LANCZOS)
    up_path = img_dir / f"{base_name}_tree_candidates_2x.png"
    up.save(up_path)
    print(f"Saved 2x version: {up_path}")


if __name__ == "__main__":
    main()
