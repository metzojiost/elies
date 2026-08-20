function displayName(p) {
  return p.display_name || p.id.replace("_", " ").replace(/\b\w/g, c => c.toUpperCase());
}

function renderList() {
  const listEl = document.getElementById("parcel-list");
  listEl.innerHTML = "";

  const overviewCard = document.createElement("div");
  overviewCard.className = "parcel-card overview-card";
  overviewCard.dataset.index = "overview";
  overviewCard.innerHTML = `
    <div class="name">${OVERVIEW.display_name}</div>
    <div class="meta">${OVERVIEW.total_parcels} parcels &middot; ${OVERVIEW.total_area_stremmata} stremmata total</div>
  `;
  overviewCard.addEventListener("click", () => selectParcel("overview"));
  listEl.appendChild(overviewCard);

  PARCELS.forEach((p, i) => {
    const card = document.createElement("div");
    card.className = "parcel-card";
    card.dataset.index = i;
    card.innerHTML = `
      <div class="name">${displayName(p)}</div>
      <div class="meta">${p.area_stremmata} stremmata &middot; ${p.tree_count_estimate.split(",")[0]}</div>
    `;
    card.addEventListener("click", () => selectParcel(i));
    listEl.appendChild(card);
  });

  document.getElementById("totals").textContent =
    `${PARCELS.length} parcel(s) mapped — ${OVERVIEW.total_area_stremmata} stremmata`;
}

function selectParcel(i) {
  document.querySelectorAll(".parcel-card").forEach(c => c.classList.remove("active"));
  document.querySelector(`.parcel-card[data-index="${i}"]`).classList.add("active");
  if (i === "overview") {
    renderOverview();
  } else {
    renderDetail(PARCELS[i]);
  }
}

function renderShape(p) {
  if (!p.boundary_svg_points) return "";
  const pts = p.boundary_svg_points.map(pt => pt.join(",")).join(" ");
  const mapUrl = p.centroid
    ? `https://www.google.com/maps?q=${p.centroid.lat},${p.centroid.lon}`
    : null;
  return `
    <div class="shape-panel">
      <svg width="140" height="140" viewBox="${p.boundary_svg_viewbox}">
        <polygon points="${pts}" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2.5"/>
      </svg>
      <div>
        <div class="section-title" style="margin-top:0">Boundary shape</div>
        <p style="font-size:13px; color:var(--text-muted); margin:0 0 8px">
          Traced from official cadastre (Ktimatologio) pins, true to scale.
        </p>
        ${mapUrl ? `<a class="map-link" href="${mapUrl}" target="_blank">Open centroid on Google Maps &rarr;</a>` : ""}
      </div>
    </div>
  `;
}

function renderGallery(p) {
  if (!p.images || p.images.length === 0) return "";
  const items = p.images.map(img => `
    <figure>
      <img src="${img.site_relative_path}" alt="${img.caption}" loading="lazy">
      <figcaption>${img.caption}</figcaption>
    </figure>
  `).join("");
  return `<div class="section-title">Images</div><div class="gallery">${items}</div>`;
}

function renderSeasons(p) {
  if (!p.seasons || p.seasons.length === 0) {
    return `
      <div class="section-title">Season records</div>
      <p class="seasons-empty">No production records yet (oil yield, water used, fertilizer, etc.) &mdash; add entries to this parcel's "seasons" array in data/parcels/parcels.json as they happen.</p>
    `;
  }
  const rows = p.seasons.map(s => `
    <tr>
      <td>${s.year ?? ""}</td>
      <td>${s.oil_liters ?? ""}</td>
      <td>${s.water_m3 ?? ""}</td>
      <td>${s.fertilizer ?? ""}</td>
      <td>${s.notes ?? ""}</td>
    </tr>
  `).join("");
  return `
    <div class="section-title">Season records</div>
    <div class="notes-box">
      <table style="width:100%; border-collapse:collapse; font-size:13px;">
        <thead>
          <tr style="text-align:left; color:var(--text-muted);">
            <th>Year</th><th>Oil (L)</th><th>Water (m³)</th><th>Fertilizer</th><th>Notes</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
}

function renderDetail(p) {
  const el = document.getElementById("detail");
  const terrainTags = (p.terrain_types || []).map(t => `<span class="tag">${t}</span>`).join("");

  el.innerHTML = `
    <h2>${displayName(p)}</h2>
    <div class="kaek">ΚΑΕΚ ${p.kaek || "—"}</div>

    <div class="stat-grid">
      <div class="stat-box">
        <div class="label">Area</div>
        <div class="value">${p.area_stremmata} stremmata</div>
      </div>
      <div class="stat-box">
        <div class="label">Area (m²)</div>
        <div class="value">${p.area_m2?.toLocaleString() ?? "—"}</div>
      </div>
      <div class="stat-box">
        <div class="label">Trees (estimate)</div>
        <div class="value">${p.tree_count_estimate || "—"}</div>
      </div>
      <div class="stat-box">
        <div class="label">Last pruned</div>
        <div class="value">${p.pruned_last_season ? `${p.trees_pruned} trees (${p.trees_pruned_season})` : "—"}</div>
      </div>
    </div>

    <div class="tags">${terrainTags}</div>

    ${renderShape(p)}

    <div class="section-title">Notes</div>
    <div class="notes-box">${p.notes || "No notes yet."}</div>

    ${renderGallery(p)}

    ${renderSeasons(p)}
  `;
}

function renderOverview() {
  const el = document.getElementById("detail");
  const treeRange = OVERVIEW.trees_low === OVERVIEW.trees_high
    ? `${OVERVIEW.trees_low}`
    : `${OVERVIEW.trees_low}-${OVERVIEW.trees_high}`;

  const locationRows = OVERVIEW.locations.map(l => `
    <tr>
      <td>${l.place_name}</td>
      <td>${l.parcel_count}</td>
      <td>${l.area_stremmata}</td>
      <td>${l.trees_low === l.trees_high ? l.trees_low : `${l.trees_low}-${l.trees_high}`}</td>
    </tr>
  `).join("");

  const exactNote = OVERVIEW.exact_tree_parcels.length > 0
    ? `<p style="font-size:12px; color:var(--text-muted); margin:8px 0 0">
         Exact (not estimated) counts included in the total: ${OVERVIEW.exact_tree_parcels.map(e => `${e.name} (${e.count})`).join(", ")}.
       </p>`
    : "";

  const ownerEstimateNote = (OVERVIEW.owner_tree_estimate_low && OVERVIEW.owner_tree_estimate_high)
    ? `
      <div class="owner-estimate-callout">
        <strong>Owner's on-the-ground estimate: ${OVERVIEW.owner_tree_estimate_low}-${OVERVIEW.owner_tree_estimate_high} trees</strong>
        &mdash; higher than the satellite total above. ${OVERVIEW.owner_tree_estimate_note || ""}
      </div>
    `
    : "";

  const productionSection = OVERVIEW.has_production_records
    ? `
      <div class="stat-grid">
        <div class="stat-box"><div class="label">Total oil</div><div class="value">${OVERVIEW.total_oil_liters} L</div></div>
        <div class="stat-box"><div class="label">Total water used</div><div class="value">${OVERVIEW.total_water_m3} m³</div></div>
      </div>
    `
    : `<p class="seasons-empty">No production records yet across any parcel &mdash; once a parcel has "seasons" entries in data/parcels/parcels.json (oil yield, water used, fertilizer), the combined totals will show here automatically.</p>`;

  el.innerHTML = `
    <h2>${OVERVIEW.display_name}</h2>
    <div class="kaek">All mapped land, combined</div>

    <div class="stat-grid">
      <div class="stat-box">
        <div class="label">Total parcels</div>
        <div class="value">${OVERVIEW.total_parcels}</div>
      </div>
      <div class="stat-box">
        <div class="label">Total area</div>
        <div class="value">${OVERVIEW.total_area_stremmata} stremmata</div>
      </div>
      <div class="stat-box">
        <div class="label">Total area (ha)</div>
        <div class="value">${OVERVIEW.total_area_ha}</div>
      </div>
      <div class="stat-box">
        <div class="label">Total trees (est.)</div>
        <div class="value">${treeRange}</div>
      </div>
    </div>
    ${exactNote}
    ${ownerEstimateNote}

    <div class="section-title">All parcels on one map</div>
    <div class="overview-map-frame">
      <img src="${OVERVIEW.map_image}" alt="All parcels on one satellite map">
    </div>

    <div class="section-title">By location</div>
    <div class="notes-box">
      <table style="width:100%; border-collapse:collapse; font-size:13px;">
        <thead>
          <tr style="text-align:left; color:var(--text-muted);">
            <th>Location</th><th>Parcels</th><th>Stremmata</th><th>Trees (est.)</th>
          </tr>
        </thead>
        <tbody>${locationRows}</tbody>
      </table>
    </div>

    <div class="section-title">Production (all parcels combined)</div>
    ${productionSection}
  `;
}

renderList();
selectParcel("overview");
