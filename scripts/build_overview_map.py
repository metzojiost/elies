"""
Builds one wide-area satellite map showing every mapped parcel's boundary
together, for the "Xwrafia (Ola)" (all lands) overview page. Unlike the
per-parcel maps, this is for orientation only — no tree detection.

Usage: python scripts/build_overview_map.py
Writes: data/parcels/imagery/overview_map.png
"""
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
PARCELS_JSON = ROOT / "data" / "parcels" / "parcels.json"
OUT_PATH = ROOT / "data" / "parcels" / "imagery" / "overview_map.png"

TILE_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
ZOOM = 17
TILE_SIZE = 256
PAD_FRACTION = 0.05  # tight crop — keep the southernmost/northernmost parcels near the edge


def lonlat_to_tile(lon, lat, z):
    n = 2 ** z
    xt = (lon + 180.0) / 360.0 * n
    lat_rad = math.radians(lat)
    yt = (1 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2 * n
    return xt, yt


def boxes_overlap(a, b, pad=4):
    return not (a[2] + pad < b[0] or b[2] + pad < a[0] or a[3] + pad < b[1] or b[3] + pad < a[1])


def main():
    parcels = json.loads(PARCELS_JSON.read_text(encoding="utf-8"))

    all_coords = []
    parcel_coords = []
    for p in parcels:
        gj_path = ROOT / p["boundary_geojson"]
        gj = json.loads(gj_path.read_text(encoding="utf-8"))
        coords = gj["geometry"]["coordinates"][0]
        parcel_coords.append((p, coords))
        all_coords.extend(coords)

    lons = [c[0] for c in all_coords]
    lats = [c[1] for c in all_coords]
    minlon, maxlon = min(lons), max(lons)
    minlat, maxlat = min(lats), max(lats)
    padlon = (maxlon - minlon) * PAD_FRACTION
    padlat = (maxlat - minlat) * PAD_FRACTION
    minlon, maxlon = minlon - padlon, maxlon + padlon
    minlat, maxlat = minlat - padlat, maxlat + padlat

    x1f, y1f = lonlat_to_tile(minlon, maxlat, ZOOM)
    x2f, y2f = lonlat_to_tile(maxlon, minlat, ZOOM)
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
            tmp = ROOT / "data" / "parcels" / "imagery" / "_tmp_ov_tile.jpg"
            tmp.write_bytes(data)
            tile_img = Image.open(tmp).convert("RGB")
            mosaic.paste(tile_img, (col * TILE_SIZE, row * TILE_SIZE))
    (ROOT / "data" / "parcels" / "imagery" / "_tmp_ov_tile.jpg").unlink(missing_ok=True)

    # crop to the exact requested extent (tile grid is coarser than the bbox)
    crop_x0, crop_y0 = lonlat_to_tile(minlon, maxlat, ZOOM)
    crop_x1, crop_y1 = lonlat_to_tile(maxlon, minlat, ZOOM)
    left = (crop_x0 - xtile_min) * TILE_SIZE
    top = (crop_y0 - ytile_min) * TILE_SIZE
    right = (crop_x1 - xtile_min) * TILE_SIZE
    bottom = (crop_y1 - ytile_min) * TILE_SIZE
    mosaic = mosaic.crop((int(left), int(top), int(right), int(bottom)))
    origin_x, origin_y = left, top

    def lonlat_to_px(lon, lat):
        xt, yt = lonlat_to_tile(lon, lat, ZOOM)
        return (xt - xtile_min) * TILE_SIZE - origin_x, (yt - ytile_min) * TILE_SIZE - origin_y

    draw = ImageDraw.Draw(mosaic)
    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except Exception:
        font = ImageFont.load_default()

    # draw all boundaries, and collect each parcel's bbox + centroid + label
    parcel_boxes = []  # no-go zones for label placement (the land itself)
    entries = []
    for p, coords in parcel_coords:
        poly_px = [lonlat_to_px(lon, lat) for lon, lat in coords]
        draw.polygon(poly_px, outline=(255, 220, 0), width=3)

        xs = [pt[0] for pt in poly_px]
        ys = [pt[1] for pt in poly_px]
        bbox = (min(xs), min(ys), max(xs), max(ys))
        parcel_boxes.append(bbox)

        cx = sum(xs) / len(xs)
        cy = sum(ys) / len(ys)
        place, qualifier = p.get("place_name"), p.get("place_qualifier")
        label = f"{place} ({qualifier})" if place and qualifier else (place or p["id"])
        entries.append({"bbox": bbox, "centroid": (cx, cy), "label": label})

    # label placement: try positions outside this parcel's own bbox first
    # (above/below/left/right, then corners, then push further out), reject
    # any candidate that overlaps another label, any parcel's bbox, or falls
    # outside the image canvas (the crop is tight, so edge parcels need this)
    canvas_w, canvas_h = mosaic.size
    placed_label_boxes = []
    GAP = 10

    for e in entries:
        bx0, by0, bx1, by1 = e["bbox"]
        bw, bh = bx1 - bx0, by1 - by0
        mid_x, mid_y = (bx0 + bx1) / 2, (by0 + by1) / 2
        label = e["label"]
        bbox_txt = draw.textbbox((0, 0), label, font=font)
        tw, th = bbox_txt[2] - bbox_txt[0], bbox_txt[3] - bbox_txt[1]
        hw, hh = tw / 2 + 5, th / 2 + 4

        base_candidates = [
            (mid_x, by0 - GAP - hh),           # above
            (mid_x, by1 + GAP + hh),           # below
            (bx0 - GAP - hw, mid_y),           # left
            (bx1 + GAP + hw, mid_y),           # right
            (bx0 - GAP - hw, by0 - GAP - hh),  # corners
            (bx1 + GAP + hw, by0 - GAP - hh),
            (bx0 - GAP - hw, by1 + GAP + hh),
            (bx1 + GAP + hw, by1 + GAP + hh),
        ]

        def in_canvas(box, margin=3):
            return box[0] >= margin and box[1] >= margin and box[2] <= canvas_w - margin and box[3] <= canvas_h - margin

        chosen = None
        for push in (0, 40, 80, 130, 190, 260, 340):
            for lx, ly in base_candidates:
                # push further away from the bbox center along the same direction
                ddx, ddy = lx - mid_x, ly - mid_y
                dist = math.hypot(ddx, ddy) or 1
                lx2 = lx + ddx / dist * push
                ly2 = ly + ddy / dist * push
                box = (lx2 - hw, ly2 - hh, lx2 + hw, ly2 + hh)
                if not in_canvas(box):
                    continue
                if any(boxes_overlap(box, pb, pad=2) for pb in parcel_boxes):
                    continue
                if any(boxes_overlap(box, lb) for lb in placed_label_boxes):
                    continue
                chosen = (lx2, ly2, box)
                break
            if chosen:
                break

        if chosen is None:
            # fallback: prefer any in-canvas position, even if it overlaps
            # something; only as a last resort allow off-canvas (clamped)
            for lx, ly in base_candidates:
                box = (lx - hw, ly - hh, lx + hw, ly + hh)
                if in_canvas(box):
                    chosen = (lx, ly, box)
                    break
        if chosen is None:
            lx2, ly2 = mid_x, by0 - GAP - hh
            box = (lx2 - hw, ly2 - hh, lx2 + hw, ly2 + hh)
            # clamp fully inside canvas
            shift_x = max(0, 3 - box[0]) + min(0, canvas_w - 3 - box[2])
            shift_y = max(0, 3 - box[1]) + min(0, canvas_h - 3 - box[3])
            lx2, ly2 = lx2 + shift_x, ly2 + shift_y
            chosen = (lx2, ly2, (lx2 - hw, ly2 - hh, lx2 + hw, ly2 + hh))

        lx, ly, box = chosen
        placed_label_boxes.append(box)

        cx, cy = e["centroid"]
        draw.line([(cx, cy), (lx, ly)], fill=(255, 220, 0), width=1)
        draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 220, 0))
        draw.rectangle(box, fill=(0, 0, 0))
        draw.text((lx - tw / 2, ly - th / 2), label, fill=(255, 255, 255), font=font)

    mosaic.save(OUT_PATH)
    print(f"Saved overview map: {OUT_PATH} ({mosaic.width}x{mosaic.height}px)")


if __name__ == "__main__":
    main()
