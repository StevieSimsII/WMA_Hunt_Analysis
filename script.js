const DATA_URL = "decision_2026_27.json";

const categoryLabel = {
  archery: "Archery",
  gun: "Gun",
  primitive_weapon: "Primitive",
  group: "Group",
  youth: "Youth",
  senior: "Senior",
};

const PAGE_SIZE = 18;

let DATA = null;
let activeCategory = "all";
let visibleCount = PAGE_SIZE;

function score(n) {
  return Number(n).toFixed(2);
}

function oddsTone(label) {
  if (!label) return "tone-soft";
  const lower = label.toLowerCase();
  if (lower.includes("unknown")) return "tone-soft";
  if (lower.includes("high") || lower.includes("extreme")) return "tone-warn";
  if (lower.includes("low")) return "tone-good";
  return "tone-soft";
}

function whyLine(hunt, rank) {
  if (rank === 0) return "Best overall mix of peak timing and workable historical odds.";
  if (hunt.rut_period === "peak_rut") return "Sits inside the scarce Dec 29–Jan 4 peak rut window.";
  if (hunt.rut_period === "pre_peak_rut") return "Pre-peak chasing window with solid hunt length.";
  if (hunt.apps_per_permit_2025 != null && hunt.apps_per_permit_2025 <= 5) {
    return "Historically softer draw pressure than most premium dates.";
  }
  if (hunt.category === "gun") return "Adds gun coverage without overlapping the other picks.";
  return `${hunt.rut_label}. ${hunt.competition_label} competition in 2025.`;
}

async function loadData() {
  const res = await fetch(DATA_URL);
  if (!res.ok) throw new Error(`Could not load ${DATA_URL}`);
  return res.json();
}

function renderStrategy(data) {
  const ranked = [...data.strategy].sort((a, b) => b.decision_score - a.decision_score);
  const root = document.getElementById("strategyList");
  root.innerHTML = ranked
    .map((hunt, i) => {
      const odds =
        hunt.apps_per_permit_2025 != null
          ? `${hunt.apps_per_permit_2025} apps/permit in 2025`
          : "No 2025 history yet";
      return `
        <li class="slate-item" style="animation-delay:${i * 70}ms">
          <div class="slate-rank">${String(i + 1).padStart(2, "0")}</div>
          <div>
            <h3>${hunt.hunt_name}</h3>
            <p class="slate-why">${whyLine(hunt, i)}</p>
            <ul class="slate-facts">
              <li>${hunt.date_label}</li>
              <li>${categoryLabel[hunt.category] || hunt.category}</li>
              <li>${hunt.permits_available} permits</li>
              <li class="${oddsTone(hunt.competition_label)}">${odds}</li>
              <li class="score">${score(hunt.decision_score)}</li>
            </ul>
          </div>
        </li>
      `;
    })
    .join("");
}

function renderPeak(data) {
  document.getElementById("peakList").innerHTML = data.peak_rut.top
    .map(
      (hunt) => `
      <article class="peak-item">
        <div>
          <h3>${hunt.hunt_name}</h3>
          <p>${hunt.date_label} · ${categoryLabel[hunt.category] || hunt.category} · ${hunt.permits_available} permits</p>
        </div>
        <div class="hunt-side">
          <span class="score">${score(hunt.decision_score)}</span>
          <small class="${oddsTone(hunt.competition_label)}">${hunt.competition_label}</small>
        </div>
      </article>
    `
    )
    .join("");
}

function renderOdds(data) {
  const adult = data.hunts.filter((h) =>
    ["archery", "gun", "primitive_weapon", "group"].includes(h.category)
  );
  const withOdds = adult.filter((h) => h.apps_per_permit_2025 != null);
  const sleepers = [...withOdds].sort((a, b) => a.apps_per_permit_2025 - b.apps_per_permit_2025).slice(0, 6);
  const hottest = [...withOdds].sort((a, b) => b.apps_per_permit_2025 - a.apps_per_permit_2025).slice(0, 6);
  const maxHot = Math.max(...hottest.map((h) => h.apps_per_permit_2025), 1);

  const sleeperMax = Math.max(...sleepers.map((h) => h.apps_per_permit_2025), 1);

  document.getElementById("sleeperList").className = "pressure cool";
  document.getElementById("hotList").className = "pressure hot";

  document.getElementById("sleeperList").innerHTML = sleepers
    .map((h) => {
      const width = Math.max(8, (h.apps_per_permit_2025 / sleeperMax) * 100);
      return `
        <li>
          <div class="pressure-top">
            <span>${h.hunt_name}</span>
            <strong>${h.apps_per_permit_2025}</strong>
          </div>
          <div class="bar"><span style="width:${width}%"></span></div>
        </li>
      `;
    })
    .join("");

  document.getElementById("hotList").innerHTML = hottest
    .map((h) => {
      const width = Math.max(8, (h.apps_per_permit_2025 / maxHot) * 100);
      return `
        <li>
          <div class="pressure-top">
            <span>${h.hunt_name}</span>
            <strong>${h.apps_per_permit_2025}</strong>
          </div>
          <div class="bar"><span style="width:${width}%"></span></div>
        </li>
      `;
    })
    .join("");
}

function filteredHunts() {
  const query = document.getElementById("filterQuery").value.trim().toLowerCase();
  const rut = document.getElementById("filterRut").value;
  const sort = document.getElementById("filterSort").value;

  let rows = [...DATA.hunts];
  if (activeCategory !== "all") rows = rows.filter((h) => h.category === activeCategory);
  if (rut !== "all") rows = rows.filter((h) => h.rut_period === rut);
  if (query) {
    rows = rows.filter((h) =>
      `${h.hunt_name} ${h.wma_location} ${h.hunt_type}`.toLowerCase().includes(query)
    );
  }

  if (sort === "decision") rows.sort((a, b) => b.decision_score - a.decision_score);
  if (sort === "odds") {
    rows.sort((a, b) => (a.apps_per_permit_2025 ?? 9999) - (b.apps_per_permit_2025 ?? 9999));
  }
  if (sort === "date") rows.sort((a, b) => a.start_date.localeCompare(b.start_date));
  if (sort === "permits") rows.sort((a, b) => b.permits_available - a.permits_available);
  return rows;
}

function renderBrowse() {
  const rows = filteredHunts();
  const shown = rows.slice(0, visibleCount);
  document.getElementById("resultMeta").textContent = `${rows.length} hunts · showing ${shown.length}`;

  document.getElementById("huntList").innerHTML = shown
    .map((hunt, index) => {
      const odds =
        hunt.apps_per_permit_2025 != null
          ? `${hunt.apps_per_permit_2025} apps/permit in 2025`
          : "No 2025 history";
      return `
        <article class="hunt" data-index="${index}">
          <button class="hunt-summary" type="button" aria-expanded="false">
            <div>
              <h3>${hunt.hunt_name}</h3>
              <p>${hunt.date_label} · ${categoryLabel[hunt.category] || hunt.category}</p>
            </div>
            <div class="hunt-side">
              <span class="score">${score(hunt.decision_score)}</span>
              <small class="${oddsTone(hunt.competition_label)}">${hunt.competition_label}</small>
            </div>
          </button>
          <div class="hunt-detail">
            <div>${hunt.wma_location}</div>
            <div>${hunt.permits_available} permits · ${hunt.duration_days} days · ${hunt.rut_label}</div>
            <div>${hunt.moon_label}</div>
            <div class="${oddsTone(hunt.competition_label)}">${odds}</div>
          </div>
        </article>
      `;
    })
    .join("");

  const more = document.getElementById("loadMore");
  more.hidden = shown.length >= rows.length;

  document.querySelectorAll(".hunt-summary").forEach((btn) => {
    btn.addEventListener("click", () => {
      const item = btn.closest(".hunt");
      const open = item.classList.toggle("is-open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });
}

function setupBrowse() {
  document.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      document.querySelectorAll(".chip").forEach((c) => c.classList.remove("is-active"));
      chip.classList.add("is-active");
      activeCategory = chip.dataset.category;
      visibleCount = PAGE_SIZE;
      renderBrowse();
    });
  });

  ["filterQuery", "filterRut", "filterSort"].forEach((id) => {
    const el = document.getElementById(id);
    el.addEventListener("input", () => {
      visibleCount = PAGE_SIZE;
      renderBrowse();
    });
    el.addEventListener("change", () => {
      visibleCount = PAGE_SIZE;
      renderBrowse();
    });
  });

  document.getElementById("loadMore").addEventListener("click", () => {
    visibleCount += PAGE_SIZE;
    renderBrowse();
  });
}

function setupNav() {
  const btn = document.querySelector(".menu-btn");
  const nav = document.getElementById("nav");
  btn?.addEventListener("click", () => {
    const open = nav.classList.toggle("is-open");
    btn.setAttribute("aria-expanded", open ? "true" : "false");
  });
  nav?.querySelectorAll("a").forEach((a) =>
    a.addEventListener("click", () => {
      nav.classList.remove("is-open");
      btn?.setAttribute("aria-expanded", "false");
    })
  );
}

async function init() {
  setupNav();
  try {
    DATA = await loadData();
    document.getElementById("deadlineNote").textContent =
      `Applications close August 15, 2026. ${DATA.totals.hunts} hunts scored across ${DATA.totals.locations} locations.`;
    document.getElementById("footStats").textContent =
      `${DATA.totals.hunts} hunts · ${DATA.totals.permits.toLocaleString()} permit seats`;
    renderStrategy(DATA);
    renderPeak(DATA);
    renderOdds(DATA);
    setupBrowse();
    renderBrowse();
  } catch (err) {
    console.error(err);
    document.getElementById("strategyList").innerHTML =
      `<li class="slate-item"><div><h3>Couldn’t load decision data.</h3><p class="slate-why">Make sure decision_2026_27.json is available.</p></div></li>`;
  }
}

document.addEventListener("DOMContentLoaded", init);
