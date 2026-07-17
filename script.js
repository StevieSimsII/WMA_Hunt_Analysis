const DATA_URL = "decision_2026_27.json";

const categoryLabel = {
  archery: "Archery",
  gun: "Gun",
  primitive_weapon: "Primitive",
  group: "Group",
  youth: "Youth",
  senior: "Senior",
};

let DATA = null;

function competitionClass(label) {
  if (!label) return "unknown";
  const lower = label.toLowerCase();
  if (lower.includes("unknown")) return "unknown";
  if (lower.includes("very high") || lower.includes("extreme") || lower === "high") return "hot";
  if (lower.includes("low") || lower.includes("very low")) return "cool";
  return "";
}

function formatScore(score) {
  return Number(score).toFixed(2);
}

function competitionTag(hunt) {
  const cls = competitionClass(hunt.competition_label);
  return `<span class="tag ${cls}">${hunt.competition_label}</span>`;
}

async function loadData() {
  const response = await fetch(DATA_URL);
  if (!response.ok) {
    throw new Error(`Failed to load ${DATA_URL}`);
  }
  return response.json();
}

function renderHero(data) {
  document.getElementById("statHunts").textContent = data.totals.hunts.toLocaleString();
  document.getElementById("statLocations").textContent = data.totals.locations.toLocaleString();
  document.getElementById("statPeak").textContent = data.peak_rut.hunt_count.toLocaleString();
  document.getElementById("deadlineLine").textContent =
    `Application window: July 15 – August 15, 2026 · ${data.totals.permits.toLocaleString()} permit seats in inventory`;
}

function renderStrategy(data) {
  const list = document.getElementById("strategyList");
  const ranked = [...data.strategy].sort((a, b) => b.decision_score - a.decision_score);
  list.innerHTML = ranked
    .map((hunt, index) => {
      const odds =
        hunt.apps_per_permit_2025 != null
          ? `${hunt.apps_per_permit_2025} apps/permit (2025)`
          : "No 2025 history";
      return `
        <li class="slate-item" style="animation-delay:${index * 80}ms">
          <div class="rank">${String(index + 1).padStart(2, "0")}</div>
          <div class="slate-body">
            <span class="tag">${categoryLabel[hunt.category] || hunt.category}</span>
            <h3>${hunt.hunt_name}</h3>
            <div class="slate-meta">
              <span>${hunt.date_label}</span>
              <span>${hunt.permits_available} permits · ${hunt.duration_days} days</span>
              <span>${hunt.rut_label}</span>
              ${competitionTag(hunt)}
              <span>${odds}</span>
            </div>
          </div>
          <div class="score-pill" title="Decision score">${formatScore(hunt.decision_score)}</div>
        </li>
      `;
    })
    .join("");
}

function renderPeak(data) {
  const root = document.getElementById("peakList");
  root.innerHTML = data.peak_rut.top
    .map(
      (hunt) => `
      <article class="peak-card">
        <span class="tag">${categoryLabel[hunt.category] || hunt.category}</span>
        <h3>${hunt.hunt_name}</h3>
        <p>${hunt.date_label} · ${hunt.permits_available} permits · score ${formatScore(hunt.decision_score)}</p>
        <p>${competitionTag(hunt)} ${hunt.moon_label}</p>
      </article>
    `
    )
    .join("");
}

function renderOdds(data) {
  const withOdds = data.hunts.filter((h) => h.apps_per_permit_2025 != null);
  const sleepers = [...withOdds]
    .filter((h) => ["archery", "gun", "primitive_weapon", "group"].includes(h.category))
    .sort((a, b) => a.apps_per_permit_2025 - b.apps_per_permit_2025)
    .slice(0, 8);
  const hottest = [...withOdds]
    .filter((h) => ["archery", "gun", "primitive_weapon", "group"].includes(h.category))
    .sort((a, b) => b.apps_per_permit_2025 - a.apps_per_permit_2025)
    .slice(0, 8);

  document.getElementById("sleeperList").innerHTML = sleepers
    .map(
      (h) => `
      <li>
        <span>${h.hunt_name}<br /><small>${h.date_label}</small></span>
        <strong>${h.apps_per_permit_2025}</strong>
      </li>
    `
    )
    .join("");

  document.getElementById("hotList").innerHTML = hottest
    .map(
      (h) => `
      <li>
        <span>${h.hunt_name}<br /><small>${h.date_label}</small></span>
        <strong>${h.apps_per_permit_2025}</strong>
      </li>
    `
    )
    .join("");
}

function filteredHunts() {
  const query = document.getElementById("filterQuery").value.trim().toLowerCase();
  const category = document.getElementById("filterCategory").value;
  const rut = document.getElementById("filterRut").value;
  const sort = document.getElementById("filterSort").value;

  let rows = [...DATA.hunts];
  if (category !== "all") rows = rows.filter((h) => h.category === category);
  if (rut !== "all") rows = rows.filter((h) => h.rut_period === rut);
  if (query) {
    rows = rows.filter((h) =>
      `${h.hunt_name} ${h.wma_location} ${h.hunt_type}`.toLowerCase().includes(query)
    );
  }

  if (sort === "decision") {
    rows.sort((a, b) => b.decision_score - a.decision_score);
  } else if (sort === "odds") {
    rows.sort((a, b) => {
      const av = a.apps_per_permit_2025 ?? Number.POSITIVE_INFINITY;
      const bv = b.apps_per_permit_2025 ?? Number.POSITIVE_INFINITY;
      return av - bv;
    });
  } else if (sort === "date") {
    rows.sort((a, b) => a.start_date.localeCompare(b.start_date));
  } else if (sort === "permits") {
    rows.sort((a, b) => b.permits_available - a.permits_available);
  }

  return rows;
}

function renderExplore() {
  const rows = filteredHunts();
  document.getElementById("resultMeta").textContent = `${rows.length} hunts shown`;
  const list = document.getElementById("huntList");
  const visible = rows.slice(0, 60);
  list.innerHTML = visible
    .map(
      (hunt) => `
      <article class="hunt-row">
        <div>
          <span class="tag">${categoryLabel[hunt.category] || hunt.category}</span>
          <h3>${hunt.hunt_name}</h3>
          <p>${hunt.wma_location}</p>
        </div>
        <div>
          <p>${hunt.date_label}</p>
          <p>${hunt.permits_available} permits · ${hunt.rut_label}</p>
          <p>${competitionTag(hunt)}</p>
        </div>
        <div class="score-pill">${formatScore(hunt.decision_score)}</div>
      </article>
    `
    )
    .join("");

  if (rows.length > 60) {
    list.insertAdjacentHTML(
      "beforeend",
      `<p class="result-meta">Showing first 60 of ${rows.length}. Narrow filters to refine.</p>`
    );
  }
}

function setupNav() {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".nav");
  toggle?.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  });
  nav?.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => nav.classList.remove("open"));
  });
}

function setupFilters() {
  ["filterQuery", "filterCategory", "filterRut", "filterSort"].forEach((id) => {
    document.getElementById(id).addEventListener("input", renderExplore);
    document.getElementById(id).addEventListener("change", renderExplore);
  });
}

async function init() {
  setupNav();
  try {
    DATA = await loadData();
    renderHero(DATA);
    renderStrategy(DATA);
    renderPeak(DATA);
    renderOdds(DATA);
    setupFilters();
    renderExplore();
  } catch (error) {
    console.error(error);
    document.getElementById("strategyList").innerHTML =
      `<li class="slate-item"><div class="slate-body"><h3>Could not load decision data.</h3><p>Check that decision_2026_27.json is available.</p></div></li>`;
  }
}

document.addEventListener("DOMContentLoaded", init);
