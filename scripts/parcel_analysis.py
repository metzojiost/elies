"""
Analyze a parcel boundary given as EGSA87 (EPSG:2100) vertex coordinates.
Usage: python parcel_analysis.py data/parcels/parcel_01_boundary.csv
Reads a CSV with columns: point,X,Y
Prints area, perimeter, bounding box, and WGS84 lat/lon of vertices + centroid.
Also writes a GeoJSON polygon next to the input file for mapping later.
"""
import csv
import json
import sys
from pathlib import Path

from pyproj import Transformer


def load_points(csv_path):
    points = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            points.append((float(row["X"]), float(row["Y"])))
    return points


def shoelace_area(pts):
    n = len(pts)
    area = 0.0
    for i in range(n - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0


def perimeter(pts):
    total = 0.0
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        total += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return total


def main():
    if len(sys.argv) != 2:
        print("Usage: python parcel_analysis.py <boundary_csv>")
        sys.exit(1)

    csv_path = Path(sys.argv[1])
    points = load_points(csv_path)

    if points[0] != points[-1]:
        points.append(points[0])

    area = shoelace_area(points)
    perim = perimeter(points)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    print(f"File: {csv_path.name}")
    print(f"Vertices: {len(points) - 1}")
    print(f"Area: {area:.2f} m2  ({area/1000:.3f} stremmata, {area/10000:.4f} ha)")
    print(f"Perimeter: {perim:.2f} m")
    print(f"Bounding box: {max(xs)-min(xs):.1f} m (X) x {max(ys)-min(ys):.1f} m (Y)")

    transformer = Transformer.from_crs("EPSG:2100", "EPSG:4326", always_xy=True)
    lonlat = [transformer.transform(x, y) for x, y in points]

    centroid_lon = sum(l[0] for l in lonlat[:-1]) / (len(lonlat) - 1)
    centroid_lat = sum(l[1] for l in lonlat[:-1]) / (len(lonlat) - 1)
    print(f"\nCentroid: lat={centroid_lat:.6f}, lon={centroid_lon:.6f}")
    print(f"Google Maps: https://www.google.com/maps?q={centroid_lat:.6f},{centroid_lon:.6f}")

    geojson = {
        "type": "Feature",
        "properties": {"source_file": csv_path.name},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[lon, lat] for lon, lat in lonlat]],
        },
    }
    out_path = csv_path.with_suffix(".geojson")
    out_path.write_text(json.dumps(geojson, indent=2), encoding="utf-8")
    print(f"\nGeoJSON written to: {out_path}")


if __name__ == "__main__":
    main()
