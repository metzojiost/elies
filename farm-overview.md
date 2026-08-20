# Olive Grove — Farm Overview

_Living notes file. Update as we learn more / add parcels._

## Basics
- Total land: 45,000 m² (4.5 ha) originally estimated — 10 parcels now actually mapped totals 43,370 m² (4.34 ha), a close match
- Total trees: owner's refined on-the-ground estimate is **400-500** (updated from the original ~500 guess). Satellite/algorithmic detection across all 10 mapped parcels comes out lower, **270-346** — a real, expected gap: satellite detection systematically undercounts in dense/overgrown clusters (touching canopies read as one blob) and can't see trees hidden under weeds (already flagged in the Platanaki notes). Treat the satellite total as a floor, not the real number — owner's field count is the one to trust as parcels get walked and corrected.
- Density: ~111 trees/ha → old, likely irregular planting rather than modern intensive rows
- Tree age: most trees ~80 years old, some older (large trunk diameter) — heritage/monumental trees
- Grove condition: long-neglected before current management started
- Expansion: unplanted space available within the land — new tree planting to be planned

## Site Characteristics
- **Terrain: sloped, much of it >45° grade, terraced.** This drives most infrastructure decisions:
  - Irrigation: gravity-fed mainlines likely feasible downhill, but pressure-compensating (PC) drippers are needed wherever the line crosses elevation changes, or pressure will be wildly uneven between top and bottom of a terrace run
  - Erosion control: any bare soil / cultivation on this grade is a serious erosion risk — ground cover, drainage cuts, and terrace wall condition all matter
  - Access: equipment/machinery use is likely limited on the steepest terraces — mule/manual work or monorail-type systems may be relevant
  - New planting on terraces: spacing constrained by terrace width, not free rectangular grid

## Pruning Log
| Date range | Trees pruned | Notes |
|---|---|---|
| ~2 months (started this year) | 50 | Heavy restoration pruning on very neglected trees |

Remaining: ~450 trees not yet restored.

**Notes on pace:** For severely neglected olive trees, restoration pruning is often done gradually over 2–3 seasons per tree (removing no more than ~25–30% of canopy in one go avoids shocking the tree and triggering excessive watersprouts). So 50 trees in 2 months of heavy renovation work isn't necessarily "slow" — it may just reflect how much cutting each neglected tree actually needed. Worth tracking per-tree so we know which ones got a first pass vs. a full restoration.

## Parcels
Workflow: get boundary pins from Ktimatologio (X,Y in ΕΓΣΑ87) → save as `data/parcels/parcel_NN_boundary.csv` → run `python scripts/parcel_analysis.py data/parcels/parcel_NN_boundary.csv` → gives area, perimeter, and a GeoJSON + Google Maps link to confirm location. (Direct KAEK-to-boundary lookup isn't available to me — the official geoportal is an interactive map app, not a queryable API — so pins are still the fastest reliable path. Once we have pins for a parcel, KAEK is only needed as a label.)

| Parcel ID | ΚΑΕΚ | Area | Tree count | Terrain/slope | Notes |
|---|---|---|---|---|---|
| Platanaki (Giagia) | 320780707010 | 7,693 m² (7.69 stremmata / 0.769 ha) | ~50-60, rough, pending on-site recount | Overgrown/dense at south end per owner | Confirmed by owner — this is the parcel pruned last year (50 trees). Internal id `parcel_01`. First of 3 parcels the owner has in the Platanaki area — this one was grandma's ("Giagia"). See "Field Verification" note below. |
| Platanaki (Mpampas 1) | 320780707009 | 1,416 m² (1.42 stremmata / 0.142 ha) | ~7-11, rough satellite estimate, unverified | Adjacent to Platanaki (Giagia), shares its vertices 6-7 edge | Internal id `parcel_02`. Second of 3 Platanaki parcels — this one is dad's ("Mpampas"). Much smaller than Giagia's parcel. Not yet field-checked. |
| Platanaki (Mpampas 2) | 320780707007 | 1,596 m² (1.60 stremmata / 0.160 ha) | ~8-11, rough satellite estimate, unverified | Adjacent to Mpampas 1, shares its vertex-10-to-vertex-1 edge | Internal id `parcel_03`. Third and last of the Platanaki parcels — directly north of Mpampas 1. Not yet field-checked. |
| Kastri (Spiti) | 320780710005 | 11,595 m² (11.59 stremmata / 1.16 ha) | ~80-100, rough satellite estimate, unverified | Flatter/more open than Platanaki, has a house on it, complex concave boundary | Internal id `parcel_04`. New location, different terrain character — larger, gentler, lighter grey-green canopies vs. Platanaki's dark maquis. Not yet field-checked. |
| Kastri (Strofi) | 320780528004 | 1,712 m² (1.71 stremmata / 0.171 ha) | ~19-23, rough satellite estimate, unverified | Narrow curved strip, near a road bend, same open terrain as Spiti | Internal id `parcel_05`. Small parcel near Kastri (Spiti) — centroid very close, likely just across the road. Not yet field-checked. |
| Gallous | 320780512025 | 1,118 m² (1.12 stremmata / 0.112 ha) | ~9, rough satellite estimate, unverified | Darker/denser canopy like Platanaki; small building just outside NE corner | Internal id `parcel_06`. New location, west of Kastri. No qualifier given (unlike the others) — just "Gallous". Not yet field-checked. |
| Agora (Kipos-Katw) | 320780710002 | 9,152 m² (9.15 stremmata / 0.915 ha) | ~59-86, rough satellite estimate, unverified | Dense canopy like Platanaki/Gallous; large irregular shape with narrow eastern spur | Internal id `parcel_07`. New location, third-largest parcel mapped. Densest per-area estimate so far (~9-10 trees/stremma). Not yet field-checked. |
| Agora (Strofi) | 320780512043 | 1,819 m² (1.82 stremmata / 0.182 ha) | ~17-23, rough satellite estimate, unverified | Narrow curved strip, same "Strofi" bend-shape naming pattern as Kastri (Strofi) | Internal id `parcel_08`. Near Agora (Kipos-Katw). Clean detection result. Not yet field-checked. |
| Faraggouli | 320780428010 | 1,014 m² (1.01 stremmata / 0.101 ha) | ~8-10, rough satellite estimate, unverified | ~2.1km south of the main cluster, narrow sliver, dense dark maquis surroundings | Internal id `parcel_09`. Notably distant from every other parcel, near what its name suggests is a small gorge. Less confident detection due to denser/less distinct surrounding vegetation — worth extra scrutiny on-site. |
| Xoirostasio (Kipos) | 320780507007 | 6,255 m² (6.26 stremmata / 0.626 ha) | **13, confirmed by owner (exact, not an estimate)** | Owner's garden/personal project, not the production grove; low density by design, no further planting planned; has a farm building on/adjacent to it | Internal id `parcel_10`. Satellite detection found 19-27 candidate trees — known wrong (likely other garden vegetation), kept only so the parcel has an image in the same format as the rest. Owner will replace with real per-tree positions once on-site — long-term goal is every parcel gets actual hand-mapped tree locations, not satellite guesses. |

## Location & Climate
- Sfaka, Lasithi, Crete, Greece — near Agios Andreas / Mochlos junction, Siteia municipality, eastern Crete (corrected — not Sfakia/White Mountains, that was my mix-up earlier)
- Rainfall: ~450mm/year average, low for the region's needs, and Mediterranean-pattern (concentrated in winter, dry summers) — summer irrigation matters for yield/fruit set even on established trees

## Terrain Detail (by type, per parcel — to fill in as mapped)
- Type A: stone-walled terraces
- Type B: cut/dug dirt terraces (vertical soil face, no stone wall) — more erosion-prone, especially near the cut face; irrigation emitters should not concentrate flow right against these
- Type C: no terrace, raw steep slope (~60% grade, i.e. ~31°) with trees planted directly on it
- Access: vehicle can reach the edge/lower part of most parcels, but tree-to-tree movement within a parcel is on foot only, and difficult-to-slow even on foot in the steepest sections

## Irrigation / Water Lines
- Source: local water utility (metered, not free) — cost makes efficiency important, points toward drip with pressure-compensating (PC) emitters rather than anything less efficient
- Gravity feed is workable from the utility connection given the slope — no pump anticipated for now
- **Future plan (noted, not yet designed):** owner wants to add water storage (cistern/pond) fed by seasonal creek runoff during rain, to reduce reliance on paid mains water. Worth sizing/siting this early even if built later, since it affects where storage + gravity mainline would sit relative to parcels.
- Design implication of terraces: elevation change across each run means PC drippers are close to mandatory, or trees at the bottom of a terrace run will get far more water than trees at the top
- Once we have at least one mapped parcel (boundaries, tree positions, elevation drop, terrace type) we can start proposing an actual drip line layout

### Parcel 01 — Field Verification (owner's first-pass check against satellite markers, from memory, not yet on-site)
- Confirmed false positives (not trees): markers 12, 26, 30, 33
- Marker 35: iffy, might not actually be owner's tree (near boundary edge)
- Marker 10: is a bush/shrub, not a tree (algorithm had split it into 2 candidate trees — both wrong)
- Undercounted: near marker 1, owner recalls ~5 trees there vs. the 2 the algorithm inferred
- Missed entirely: a weed-covered patch inside the area roughly bounded by markers 1, 9, 23, 26, 12 — owner expects 6-7 trees hiding there once cleared
- Missed entirely: unspecified number of trees on the south/bottom side, hidden by weeds grown up between them — will only be known once that area is cleared
- Also: satellite imagery predates some of this year's cutting, so a few marked canopies may reflect wood that's already been removed — expect some natural mismatch for that reason alone
- Owner's own independent manual count from the image: ~55, including noticing 2 shrubs (consistent with marker 10) and also missing the weed-obscured bottom-side trees
- **Net read: rough algorithmic count and owner's manual count converge around 50-60, but both undercount the two weed-covered zones (west patch near markers 1/9/23/26/12, and the south/bottom strip). Real number likely higher. Treat as placeholder until owner does an in-person count.**

## Website Archive
A static, offline, no-hosting-needed site lives in `site/` — open `site/index.html` in a browser (it needs to be served, not opened via double-click, because the image paths won't load over a raw `file://` URL in most browsers; easiest is `python -m http.server` run from the project root, then visit `http://localhost:8000/site/index.html`).

**How it's structured (so this stays easy to extend):**
- `data/parcels/parcels.json` — the one hand-maintained file with parcel facts: local name, area, tree count, terrain, notes, image list, and an empty `seasons` array reserved for future yearly production records (oil liters, water m³, fertilizer, etc.)
- `scripts/build_site_data.py` — reads `parcels.json` + each parcel's boundary CSV, computes a true-to-scale boundary shape, and generates `site/data.js` (never hand-edit `data.js` directly — it gets overwritten)
- `site/index.html`, `style.css`, `app.js` — the site itself, plain HTML/CSS/JS, no build step, no external dependencies (works fully offline)

**To add a new parcel to the site:** add its pins → run `parcel_analysis.py` → add an entry to `parcels.json` → run `build_site_data.py`. To rename a parcel, edit its `place_name` / `place_qualifier` fields in `parcels.json` and rerun the build script.

Sidebar stays a flat list of parcels (no grouping by place name) — owner has few enough parcels that grouping is unnecessary overhead.

**Built: "Xwrafia (Ola)" overview entry.** Pinned at the top of the sidebar (visually separated from the parcel list), selected by default on page load. Shows:
- Aggregate stats: total parcels, total area (stremmata + ha), total tree count as a low-high range (`OVERVIEW.trees_low`/`trees_high` in `site/data.js`), with a note listing which parcels contributed an *exact* (owner-confirmed) count rather than an estimate
- One wide-area satellite map (`data/parcels/imagery/overview_map.png`) with every parcel's boundary drawn and labeled — built by `scripts/build_overview_map.py`, which fetches its own tile mosaic covering the full extent of all parcels (zoom 16, wider/lower-res than per-parcel maps since this is for orientation, not tree counting) and does simple label collision-avoidance (radial offset + leader line) so labels stay readable even where parcels cluster tightly (e.g. the 3 Platanaki parcels, the two Strofi-named parcels)
- A by-location breakdown table (parcels/area/trees grouped by `place_name`)
- A production section that's currently a placeholder ("no records yet") — once any parcel gets `seasons` entries in `parcels.json`, the combined oil/water totals appear here automatically, no code changes needed

**To rebuild after adding/editing a parcel:** run `build_site_data.py` (updates per-parcel data + recomputes OVERVIEW aggregates) and `build_overview_map.py` (only needed if a parcel's boundary changed or a new parcel was added — regenerates the wide map).

Overview map is fetched at zoom 17 (~0.98m/px) with a tight ~5% crop margin around the full extent of all parcels combined, and the `<img>` is set to `width:100%` in CSS so it stretches to fill the frame's border edge-to-edge (minor upscale, negligible at this resolution).

**Noted for later, not fixing now:** on the overview map, Platanaki (Mpampas 2)'s boundary line sits very close to / slightly touching Platanaki (Giagia)'s boundary near their shared area (they're not directly adjacent in the pin data — Mpampas 1 sits between them — but at this zoom level the lines read as nearly overlapping). Owner has visually confirmed this is fine for now and doesn't need correcting, but worth a second look if it ever causes confusion.

## Tree Counting Method (satellite, for reuse on future parcels)
1. Get boundary pins → `scripts/parcel_analysis.py` (area, GeoJSON)
2. `python scripts/fetch_satellite.py data/parcels/parcel_NN_boundary.geojson` — pulls Esri World Imagery tiles around the parcel and stitches them (best available resolution was zoom 18, ~0.49m/pixel, for this parcel — check coverage per-parcel, it can vary by location)
3. `python scripts/detect_trees.py data/parcels/parcel_NN_boundary.geojson` — color/brightness-based blob detection restricted to the polygon, outputs numbered candidate markers

**Update after Parcel 04 (Kastri/Spiti):** the color threshold is now adaptive per-parcel (computed from percentiles of that parcel's own imagery) rather than a fixed value. The original fixed threshold was tuned on Platanaki's dark, dense maquis and badly undercounted Kastri's lighter, more open grey-green canopies (33 vs ~103 trees before/after recalibrating) — different terrain needs different thresholds. Parcels 01-03's images were generated with the old fixed method and were NOT regenerated, because Parcel 01's candidate markers are already tied to the owner's specific field-verification notes (marker numbers 12, 26, 30, 33, etc.) — regenerating would shift those numbers and break that record. All parcels from 04 onward use the adaptive method.

**Known limitations — treat every output as a hypothesis to field-check, not a survey:**
- Can't distinguish olive canopies from other similarly-colored maquis/shrub vegetation (carob, oak scrub, phrygana) — likely some false positives
- Touching/overlapping canopies in dense areas get merged into one blob; the script guesses a split count from blob area, which is crude and likely undercounts in thick clusters
- Sparse/small or oddly-lit canopies may fall outside the brightness/color threshold and get missed entirely
- **Best in open, well-spaced areas; weakest in dense/overgrown zones** — exactly the "jungle" bottom section of Parcel 01 the owner flagged as unclear even in person, so don't trust the count there until it's cleared
- Cross-check: Parcel 01's estimate (~36-57) landed close to the known 50 pruned trees there, a reasonable sanity check for this method, not proof of accuracy elsewhere

## New Planting (Expansion)
- Rough estimate: 10-20% more trees fit-able across the land, based on the parcel already restored last year
- Approach: not matching old wide spacing — plant new trees closer together in gaps, kept smaller via pruning/management (semi-intensive infill rather than replicating the old giants)
- Still needed: variety choice for new trees, and an establishment irrigation plan (young trees need reliable water for their first 2-3 dry seasons regardless of how drought-tolerant the mature grove is)

**Planned (not built yet): real per-tree locations.** Long-term goal is for every parcel to eventually have actual hand-mapped tree positions (from the owner walking each parcel), replacing the satellite candidate markers entirely rather than just correcting them. The satellite images/markers are a placeholder until that happens, parcel by parcel.

## Open Questions / Next Steps
- [ ] Field-verify Parcel 01 tree candidate markers (`data/parcels/imagery/parcel_01_tree_candidates_2x.png`) — confirm/correct against what's actually there, especially the overgrown south end
- [ ] Map remaining parcels (boundary pins + satellite pass each)
- [ ] Variety/varieties of olive (affects pruning style, harvest timing, irrigation needs, and what to plant for expansion — Koroneiki is the common Cretan default, but confirm)
- [ ] Soil type per parcel
- [ ] Any existing irrigation infrastructure already in the ground, or starting from zero
- [ ] Rough siting idea for future water storage (which creek, which parcel it would feed)
