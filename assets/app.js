/* South Delta Szn — 2025-26 WMA draw planner */
(() => {
  "use strict";

  const DATA = window.HUNT_DATA;
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  const TYPE_META = {
    "Deer Archery":          { short: "Archery",   color: "var(--green)" },
    "Deer Primitive Weapon": { short: "Primitive", color: "var(--blue)" },
    "Deer Gun":              { short: "Gun",       color: "var(--accent)" },
    "Deer Group":            { short: "Group",     color: "var(--purple)" },
    "Teal":                  { short: "Teal",      color: "var(--red)" }
  };

  const STORE = {
    shortlist: "sds.shortlist",
    theme: "sds.theme",
    radiusOn: "sds.radiusOn",
    radiusMin: "sds.radiusMin"
  };

  const read = (k, fallback) => {
    try { const v = localStorage.getItem(k); return v === null ? fallback : JSON.parse(v); }
    catch { return fallback; }
  };
  const write = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* private mode */ } };

  const state = {
    view: "hunts",
    search: "",
    types: new Set(),
    wma: "",
    month: "",
    sort: "score",
    radiusOn: read(STORE.radiusOn, true),
    radiusMin: read(STORE.radiusMin, 90),
    shortlist: new Set(read(STORE.shortlist, []))
  };

  /* ── Helpers ───────────────────────────────────────────────────────── */
  const parseDay = (iso) => {
    const [y, m, d] = iso.split("-").map(Number);
    return new Date(y, m - 1, d);
  };

  const fmtRange = (startIso, endIso) => {
    const s = parseDay(startIso), e = parseDay(endIso);
    const mon = (d) => d.toLocaleDateString("en-US", { month: "short" });
    if (startIso === endIso) return `${mon(s)} ${s.getDate()}`;
    if (s.getMonth() === e.getMonth()) return `${mon(s)} ${s.getDate()}–${e.getDate()}`;
    return `${mon(s)} ${s.getDate()} – ${mon(e)} ${e.getDate()}`;
  };

  // "Wed–Sun" — which days of the week the hunt actually falls on.
  const fmtDows = (startIso, endIso) => {
    const dow = (iso) => parseDay(iso).toLocaleDateString("en-US", { weekday: "short" });
    return startIso === endIso ? dow(startIso) : `${dow(startIso)}–${dow(endIso)}`;
  };

  const fmtDrive = (min) => {
    const h = Math.floor(min / 60), m = min % 60;
    return h ? `${h}h ${String(m).padStart(2, "0")}m` : `${m}m`;
  };

  const countyLabel = (county) =>
    `${county} ${county.includes("/") ? "counties" : "County"}`;

  const monthKey = (iso) => iso.slice(0, 7);
  const monthLabel = (key) => {
    const [y, m] = key.split("-").map(Number);
    return new Date(y, m - 1, 1).toLocaleDateString("en-US", { month: "long", year: "numeric" });
  };

  const isPeakRut = (iso) => iso >= DATA.peakRut.start && iso <= DATA.peakRut.end;

  // The loaded data covers a season that has already ended.
  const isStaleSeason = () => {
    const lastDay = DATA.hunts.reduce((max, h) => (h.end > max ? h.end : max), "");
    return new Date().toISOString().slice(0, 10) > lastDay;
  };

  const moonOnDay = (iso) => {
    const SYN = 29.530588853;
    const epoch = Date.UTC(2000, 0, 6, 18, 14);
    const [y, m, d] = iso.split("-").map(Number);
    const days = (Date.UTC(y, m - 1, d, 12) - epoch) / 86400000;
    return ((days % SYN) + SYN) % SYN;
  };
  const isNewMoonWindow = (iso) => {
    const age = moonOnDay(iso);
    return Math.min(age, 29.530588853 - age) <= 3;
  };

  /* ── Filtering ─────────────────────────────────────────────────────── */
  function inRadius(h) {
    return !state.radiusOn || h.driveMinutes <= state.radiusMin;
  }

  function visibleHunts() {
    const q = state.search.trim().toLowerCase();
    let out = DATA.hunts.filter((h) => {
      if (!inRadius(h)) return false;
      if (state.types.size && !state.types.has(h.type)) return false;
      if (state.wma && h.wma !== state.wma) return false;
      if (state.month && monthKey(h.start) !== state.month) return false;
      if (q && !(`${h.name} ${h.wma} ${h.rutPhase} ${h.moonPhase}`.toLowerCase().includes(q))) return false;
      return true;
    });

    const sorters = {
      score:   (a, b) => (b.score ?? -1) - (a.score ?? -1) || a.start.localeCompare(b.start),
      date:    (a, b) => a.start.localeCompare(b.start) || (b.score ?? -1) - (a.score ?? -1),
      drive:   (a, b) => a.driveMinutes - b.driveMinutes || (b.score ?? -1) - (a.score ?? -1),
      permits: (a, b) => (b.permits ?? 0) - (a.permits ?? 0) || (b.score ?? -1) - (a.score ?? -1)
    };
    return out.sort(sorters[state.sort]);
  }

  /* ── Rendering: stats ──────────────────────────────────────────────── */
  function renderStats() {
    const inR = DATA.hunts.filter(inRadius);
    const areas = new Set(inR.map((h) => h.wma));
    const permits = inR.reduce((s, h) => s + (h.permits || 0), 0);
    const peak = inR.filter((h) => h.rutPhase === "Peak Rut").length;
    const best = inR.reduce((b, h) => (h.score != null && (!b || h.score > b.score) ? h : b), null);

    $("#stats").innerHTML = [
      { v: inR.length, l: "Hunts available" },
      { v: areas.size, l: "WMAs in range" },
      { v: permits.toLocaleString(), l: "Total permits" },
      { v: peak, l: "Peak-rut hunts" },
      { v: best ? best.score.toFixed(2) : "—", l: "Top score", accent: true }
    ].map((s) => `
      <div class="stat${s.accent ? " accent" : ""}"><b>${s.v}</b><span>${s.l}</span></div>
    `).join("");
  }

  /* ── Rendering: hunt cards ─────────────────────────────────────────── */
  function huntCard(h) {
    const meta = TYPE_META[h.type] || { short: h.type, color: "var(--line)" };
    const scored = h.score !== null && h.score !== undefined;
    const tier = !scored ? "tier-none" : h.score >= 8 ? "tier-1" : h.score >= 7 ? "tier-2" : "";
    const starred = state.shortlist.has(h.id);
    const far = h.driveMinutes > state.radiusMin;

    return `
      <article class="hunt" style="--type-color:${meta.color}" data-id="${h.id}" tabindex="0">
        <button class="star${starred ? " is-on" : ""}" data-star="${h.id}"
                aria-label="${starred ? "Remove from" : "Add to"} shortlist">${starred ? "★" : "☆"}</button>
        <div class="hunt-head">
          <div class="score ${tier}">${scored
              ? `<b>${h.score.toFixed(1)}</b><small>SCORE</small>`
              : `<b>—</b><small>${h.species.toUpperCase()}</small>`}</div>
          <div class="hunt-title">
            <h3>${h.name}</h3>
            <p>${fmtRange(h.start, h.end)} · <span class="dow">${fmtDows(h.start, h.end)}</span>
               · ${h.days} day${h.days > 1 ? "s" : ""} · ${meta.short}</p>
          </div>
        </div>
        <div class="hunt-meta">
          ${h.planned ? `<span class="tag planned">📌 In your plan${h.conflictsWith?.length ? " — conflict" : ""}</span>` : ""}
          ${h.rutPhase ? `<span class="tag${h.rutPhase === "Peak Rut" ? " hot" : ""}">🦌 ${h.rutPhase}</span>` : ""}
          <span class="tag">🌙 ${h.moonPhase}</span>
          ${h.maxParty > 2 ? `<span class="tag">👥 up to ${h.maxParty}</span>` : ""}
          ${h.restriction ? `<span class="tag">⚠️ ${h.restriction}</span>` : ""}
        </div>
        <div class="hunt-foot">
          <span class="tag${far ? " far" : ""}">🚗 ${fmtDrive(h.driveMinutes)}</span>
          <span class="stats-inline">
            <span>${h.agency === "USFWS" ? "USFWS" : `${h.permits} permits`}</span>
            <span>${h.driveMiles} mi</span>
          </span>
        </div>
      </article>`;
  }

  function renderHunts() {
    const list = visibleHunts();
    $("#hunt-grid").innerHTML = list.map(huntCard).join("");
    $("#hunts-empty").hidden = list.length > 0;
    $("#result-count").textContent =
      `${list.length} hunt${list.length === 1 ? "" : "s"} · ${list.reduce((s, h) => s + (h.permits || 0), 0)} permits`;
  }

  function renderChips() {
    const counts = {};
    DATA.hunts.filter(inRadius).forEach((h) => { counts[h.type] = (counts[h.type] || 0) + 1; });
    $("#type-chips").innerHTML = Object.keys(TYPE_META).map((type) => `
      <button class="chip${state.types.has(type) ? " is-on" : ""}" data-type="${type}">
        <i class="dot" style="background:${TYPE_META[type].color}"></i>${TYPE_META[type].short}
        <span class="n">${counts[type] || 0}</span>
      </button>`).join("");
  }

  /* ── Rendering: calendar ───────────────────────────────────────────── */
  function renderCalendar() {
    const list = visibleHunts();
    const byDay = new Map();
    list.forEach((h) => {
      const start = parseDay(h.start), end = parseDay(h.end);
      for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
        const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
        if (!byDay.has(key)) byDay.set(key, new Set());
        byDay.get(key).add(h.type);
      }
    });

    const months = [...new Set(DATA.hunts.flatMap((h) => [monthKey(h.start), monthKey(h.end)]))].sort();
    const dow = ["S", "M", "T", "W", "T", "F", "S"];

    const plannedDays = new Set((DATA.planned || []).flatMap((p) => eachDay(p.start, p.end)));
    const conflicts = conflictDays();

    $("#cal-months").innerHTML = months.map((key) => {
      const [y, m] = key.split("-").map(Number);
      const first = new Date(y, m - 1, 1);
      const total = new Date(y, m, 0).getDate();
      const cells = [];
      for (let i = 0; i < first.getDay(); i++) cells.push('<div class="cal-day blank"></div>');
      for (let day = 1; day <= total; day++) {
        const iso = `${y}-${String(m).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
        const types = byDay.get(iso);
        const cls = ["cal-day"];
        if (types) cls.push("has-hunt");
        if (isPeakRut(iso)) cls.push("is-peak");
        if (isNewMoonWindow(iso)) cls.push("is-newmoon");
        if (plannedDays.has(iso)) cls.push("is-planned");
        if (conflicts.has(iso)) cls.push("is-conflict");
        const dots = types
          ? [...types].map((t) => `<i class="dot" style="background:${TYPE_META[t].color}"></i>`).join("")
          : "";
        const title = types ? `${iso} — ${[...types].map((t) => TYPE_META[t].short).join(", ")}` : iso;
        cells.push(`<div class="${cls.join(" ")}" title="${title}">${day}<span class="dots">${dots}</span></div>`);
      }
      return `<div class="cal-month"><h3>${monthLabel(key)}</h3>
        <div class="cal-grid">${dow.map((d) => `<div class="cal-dow">${d}</div>`).join("")}${cells.join("")}</div>
      </div>`;
    }).join("");
  }

  /* ── Rendering: the plan ───────────────────────────────────────────── */
  const eachDay = (startIso, endIso) => {
    const out = [];
    for (let d = parseDay(startIso), end = parseDay(endIso); d <= end; d.setDate(d.getDate() + 1)) {
      out.push(isoOf(d));
    }
    return out;
  };

  function isoOf(d) {
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  }

  // Days covered by more than one planned hunt — the ones you can't be at both of.
  function conflictDays() {
    const seen = new Map();
    (DATA.planned || []).forEach((p) => {
      eachDay(p.start, p.end).forEach((iso) => seen.set(iso, (seen.get(iso) || 0) + 1));
    });
    return new Set([...seen].filter(([, n]) => n > 1).map(([iso]) => iso));
  }

  function renderPlan() {
    const plan = DATA.planned || [];
    if (!plan.length) return;
    $("#plan-panel").hidden = false;

    const conflicts = conflictDays();

    // Hunts cluster into a few tight blocks with long dead space between (a
    // September teal hunt and a December deer block, say). One timeline across
    // the whole season would squash every bar into a sliver, so split on gaps.
    const GAP_DAYS = 10;
    const clusters = [];
    [...plan].sort((a, b) => a.start.localeCompare(b.start)).forEach((p) => {
      const last = clusters[clusters.length - 1];
      const gap = last
        ? (parseDay(p.start) - parseDay(last.end)) / 86400000
        : Infinity;
      if (last && gap <= GAP_DAYS) {
        last.items.push(p);
        if (p.end > last.end) last.end = p.end;
      } else {
        clusters.push({ start: p.start, end: p.end, items: [p] });
      }
    });

    $("#plan-gantt").innerHTML = clusters.map(renderCluster).join("");

    function renderCluster(cluster) {
      // A little context on either side of the block.
      const first = parseDay(cluster.start);
      first.setDate(first.getDate() - 2);
      const lastDate = parseDay(cluster.end);
      lastDate.setDate(lastDate.getDate() + 2);

      const days = [];
      for (let d = new Date(first); d <= lastDate; d.setDate(d.getDate() + 1)) days.push(isoOf(d));
      const col = (iso) => days.indexOf(iso) + 2;   // +2: label occupies column 1

    const header = days.map((iso) => {
      const d = parseDay(iso);
      const cls = ["plan-dow"];
      if (conflicts.has(iso)) cls.push("is-conflict");
      if (isPeakRut(iso)) cls.push("is-peak");
      return `<div class="${cls.join(" ")}" style="grid-column:${col(iso)}">
        <small>${"SMTWTFS"[d.getDay()]}</small>${d.getDate()}</div>`;
    }).join("");

      const rows = cluster.items.map((p, i) => {
      const hunt = DATA.hunts.find((h) => h.name === p.name) || {};
      const clash = p.conflictsWith.length > 0;
      // A conflict that traps the same hunter in two places is the hard kind.
      const trapped = p.conflictsWith.some((c) => c.sharedHunters.length);
      const bar = `<div class="plan-bar${clash ? " is-conflict" : ""}${trapped ? " is-hard" : ""}"
            style="grid-column:${col(p.start)} / ${col(p.end) + 1}; grid-row:${i + 2}"
            title="${p.name}">
          ${fmtRange(p.start, p.end)}${hunt.driveMinutes ? ` · ${fmtDrive(hunt.driveMinutes)}` : ""}
        </div>`;
      const who = p.hunters.length ? p.hunters.join(", ") : "hunters TBD";
      const label = `<div class="plan-label" style="grid-row:${i + 2}">
          <strong>${p.name}</strong>
          <small><span class="status status-${p.status}">${p.status}</span> ${who}</small>
          ${p.groupId ? `<small class="gid">Group ID <b>${p.groupId}</b></small>` : ""}
          ${p.todo ? `<small class="todo">⚠ ${p.todo}</small>` : ""}
        </div>`;
      // Empty cells keep the row's background grid visible behind the bar.
      const cells = days.map((iso) => `<div class="plan-cell${conflicts.has(iso) ? " is-conflict" : ""}"
          style="grid-column:${col(iso)}; grid-row:${i + 2}"></div>`).join("");
      return label + cells + bar;
    }).join("");

      const span = `${monthLabel(monthKey(cluster.start))}${
        monthKey(cluster.start) !== monthKey(cluster.end)
          ? ` – ${monthLabel(monthKey(cluster.end))}` : ""}`;
      return `<div class="plan-cluster">
        <h4>${span}</h4>
        <div class="plan-grid" style="--n:${days.length}">
          <div class="plan-corner"></div>${header}${rows}
        </div></div>`;
    }

    // Report each overlapping pair once.
    const pairs = [];
    plan.forEach((p) => p.conflictsWith.forEach((c) => {
      const key = [p.name, c.name].sort().join(" ↔ ");
      if (!pairs.some((x) => x.key === key)) {
        pairs.push({ key, a: p.name, b: c.name, shared: c.sharedHunters });
      }
    }));

    // TR Complex allows one limited draw deer hunt per applicant.
    const over = DATA.refugeOverLimit || [];
    $("#plan-rule").innerHTML = over.length
      ? `<strong>Refuge one-hunt rule.</strong> The TR Complex brochure says an applicant
         may apply for only <em>one</em> limited draw deer hunt.
         ${over.map((o) => `<strong>${o.hunter}</strong> is on ${o.hunts.length}:
           ${o.hunts.join(", ")}`).join("<br>")}<br>
         Confirm with the refuge (662-836-3004) before checking out.`
      : "";
    $("#plan-rule").hidden = over.length === 0;

    $("#plan-summary").innerHTML = pairs.length
      ? `<strong class="warn">${conflicts.size} overlapping day${conflicts.size === 1 ? "" : "s"} across ${pairs.length} pair${pairs.length === 1 ? "" : "s"}.</strong><br>` +
        pairs.map((p) => `<span class="clash">${p.a}</span> vs <span class="clash">${p.b}</span>` +
          (p.shared.length
            ? ` — <strong class="warn">${p.shared.join(", ")} is on both.</strong>`
            : " — different hunters, but the dates collide.")).join("<br>")
      : "No date conflicts — every hunt sits on separate days.";
  }

  /* ── Rendering: shortlist ──────────────────────────────────────────── */
  function shortlistHunts() {
    return DATA.hunts.filter((h) => state.shortlist.has(h.id));
  }

  function renderShortlist() {
    const list = shortlistHunts();
    $("#shortlist-count").textContent = list.length;
    $("#shortlist-grid").innerHTML = list.map(huntCard).join("");
    $("#shortlist-empty").hidden = list.length > 0;

    const over = list.length > 5;
    $("#shortlist-status").innerHTML = list.length
      ? `${list.length} of 5 choices${over ? ' — <strong style="color:var(--red)">over the limit</strong>' : ""}`
      : "";
  }

  function renderHunters() {
    $("#hunters-table tbody").innerHTML = (window.HUNTERS || []).map((h) => `
      <tr><td>${h.name}</td><td>${h.dob}</td><td>${h.raid}</td><td>${h.state}</td></tr>
    `).join("");
  }

  /* ── Rendering: areas ──────────────────────────────────────────────── */
  function renderAreas() {
    $("#drive-model-note").textContent =
      `Estimated from ${DATA.camp.label.replace("Camp — ", "")} using straight-line distance × ` +
      `${DATA.driveModel.roadFactor} road factor at ${DATA.driveModel.avgMph} mph, ` +
      `plus ${DATA.driveModel.accessMinutes} min on WMA access roads.`;

    $("#area-list").innerHTML = DATA.wmas.map((w) => {
      const far = w.driveMinutes > state.radiusMin;
      return `<div class="area${far ? " is-far" : ""}">
        <h4>${w.name}</h4>
        <p class="access">${countyLabel(w.county)} — ${w.access}</p>
        <div class="drive"><b>${fmtDrive(w.driveMinutes)}</b><small>${w.driveMiles} mi · ${w.hunts} hunts</small></div>
      </div>`;
    }).join("");

    $("#weights").innerHTML = Object.entries(DATA.weights)
      .sort((a, b) => b[1] - a[1])
      .map(([k, v]) => `<div class="weight">
        <span>${k[0].toUpperCase() + k.slice(1)}</span>
        <span class="bar"><i style="width:${v * 100 / 0.4}%"></i></span>
        <span class="val">${Math.round(v * 100)}%</span>
      </div>`).join("");
  }

  /* ── Drawer ────────────────────────────────────────────────────────── */
  function openDrawer(id) {
    const h = DATA.hunts.find((x) => x.id === id);
    if (!h) return;
    const wma = DATA.wmas.find((w) => w.name === h.wma) || {};
    const starred = state.shortlist.has(h.id);
    const rows = [
      ["Area", h.wma],
      ["County", countyLabel(h.county)],
      ["Dates", `${fmtRange(h.start, h.end)}, ${parseDay(h.start).getFullYear()}`],
      ["Days of week", fmtDows(h.start, h.end)],
      ["Length", `${h.days} day${h.days > 1 ? "s" : ""}`],
      ["Permits", (h.permits ?? "not published") + (h.groupSize ? ` (${h.groupSize} hunters each)` : "")],
      ["Drive from camp", `${fmtDrive(h.driveMinutes)} · ${h.driveMiles} mi`],
      ["Best day", parseDay(h.bestDay).toLocaleDateString("en-US", { weekday: "long", month: "short", day: "numeric" })],
      ["Moon", `${h.moonPhase} · ${Math.round(h.moonIllum * 100)}% lit`]
    ];

    $("#drawer-body").innerHTML = `
      <h2>${h.name}</h2>
      <p class="sub">${TYPE_META[h.type]?.short || h.type} · ${h.score != null
          ? `Score ${h.score.toFixed(2)} / 10` : `${h.species} — not scored on deer movement`}</p>
      ${h.rutPhase ? `<div class="callout"><strong>${h.rutPhase}.</strong> ${h.rutNote}</div>` : ""}
      <dl class="dl">${rows.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("")}</dl>
      ${h.scores ? `<h3>Score breakdown</h3>
      <div class="weights">${Object.entries(h.scores).map(([k, v]) => `
        <div class="weight">
          <span>${k[0].toUpperCase() + k.slice(1)}</span>
          <span class="bar"><i style="width:${v * 10}%"></i></span>
          <span class="val">${v.toFixed(1)}</span>
        </div>`).join("")}
      </div>` : ""}
      <h3>Access</h3>
      <p class="muted" style="font-size:13px">${wma.access || "—"}</p>
      <div class="btn-row" style="margin-top:20px">
        <button class="ghost-btn" data-star="${h.id}">${starred ? "★ Remove from shortlist" : "☆ Add to shortlist"}</button>
        <a class="ghost-btn" target="_blank" rel="noopener"
           href="https://www.google.com/maps/dir/?api=1&origin=${encodeURIComponent("1149 Watertower Rd, Bentonia, MS 39040")}&destination=${wma.lat},${wma.lon}">Route it</a>
      </div>`;

    $("#drawer").hidden = false;
    $("#drawer-backdrop").hidden = false;
  }

  const closeDrawer = () => { $("#drawer").hidden = true; $("#drawer-backdrop").hidden = true; };

  /* ── Export ────────────────────────────────────────────────────────── */
  function download(filename, text, mime) {
    const url = URL.createObjectURL(new Blob([text], { type: mime }));
    const a = document.createElement("a");
    a.href = url; a.download = filename;
    document.body.appendChild(a); a.click(); a.remove();
    URL.revokeObjectURL(url);
  }

  function exportCsv() {
    const cols = ["name", "type", "wma", "start", "end", "days", "permits", "driveMinutes", "driveMiles", "rutPhase", "moonPhase", "score"];
    const esc = (v) => (/[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : v);
    const rows = visibleHunts().map((h) => cols.map((c) => esc(h[c])).join(","));
    download("delta-hunts-filtered.csv", [cols.join(","), ...rows].join("\n"), "text/csv");
  }

  function exportIcs() {
    const list = shortlistHunts();
    if (!list.length) return;
    const stamp = new Date().toISOString().replace(/[-:]/g, "").split(".")[0] + "Z";
    const compact = (iso) => iso.replace(/-/g, "");
    const nextDay = (iso) => {
      const d = parseDay(iso); d.setDate(d.getDate() + 1);
      return compact(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`);
    };
    const lines = [
      "BEGIN:VCALENDAR", "VERSION:2.0",
      "PRODID:-//South Delta Szn//WMA Draw Shortlist//EN",
      "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
      "X-WR-CALNAME:WMA Draw Shortlist 2025-26"
    ];
    list.forEach((h) => {
      lines.push(
        "BEGIN:VEVENT",
        `UID:${h.id}@southdeltaszn`,
        `DTSTAMP:${stamp}`,
        `DTSTART;VALUE=DATE:${compact(h.start)}`,
        `DTEND;VALUE=DATE:${nextDay(h.end)}`,
        `SUMMARY:${h.name}`,
        `LOCATION:${h.wma} WMA`,
        `DESCRIPTION:${h.rutPhase} · ${h.moonPhase} · ${h.permits} permits · ${fmtDrive(h.driveMinutes)} from camp · score ${h.score.toFixed(2)}`,
        "END:VEVENT"
      );
    });
    lines.push("END:VCALENDAR");
    download("wma-draw-shortlist.ics", lines.join("\r\n"), "text/calendar");
  }

  /* ── Wiring ────────────────────────────────────────────────────────── */
  function refresh() {
    renderStats();
    renderChips();
    renderHunts();
    renderPlan();
    renderCalendar();
    renderShortlist();
    renderAreas();

    const inR = DATA.hunts.filter(inRadius).length;
    const excluded = DATA.hunts.length - inR;
    // Statewide there can be a dozen excluded areas — name the nearest few,
    // which are the ones actually worth reconsidering, and count the rest.
    const farAreas = DATA.wmas.filter((w) => w.driveMinutes > state.radiusMin).map((w) => w.name);
    const named = farAreas.slice(0, 3).join(", ");
    const rest = farAreas.length - 3;
    $("#radius-summary").textContent = state.radiusOn
      ? `Showing ${inR} of ${DATA.hunts.length} hunts.` +
        (excluded
          ? ` ${excluded} hidden beyond ${fmtDrive(state.radiusMin)} — nearest cut: ${named}${rest > 0 ? ` and ${rest} more` : ""}.`
          : " Every area is inside the radius.")
      : `Radius filter off — all ${DATA.hunts.length} hunts across ${DATA.wmas.length} areas.`;
  }

  function setView(view) {
    state.view = view;
    $$("#tabs .tab").forEach((t) => t.classList.toggle("is-active", t.dataset.view === view));
    $$(".view").forEach((v) => v.classList.toggle("is-active", v.dataset.view === view));
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function toggleStar(id) {
    if (state.shortlist.has(id)) state.shortlist.delete(id); else state.shortlist.add(id);
    write(STORE.shortlist, [...state.shortlist]);
    renderHunts();
    renderShortlist();
    if (!$("#drawer").hidden) openDrawer(id);
  }

  function init() {
    // Camp + generated lines
    $("#camp-line").textContent = DATA.camp.label.replace("Camp — ", "");
    $("#generated-line").textContent =
      `Season ${DATA.season} · ${DATA.hunts.length} hunts · built ${DATA.generated} from ${DATA.sourceFiles.join(", ")}`;

    $("#source-line").textContent =
      `Data compiled from MDWFP ${DATA.season} WMA draw listings and the Theodore Roosevelt ` +
      `NWR Complex ${DATA.season} lottery. Drive times are estimates from a road-distance ` +
      `model — confirm routes before you commit.`;

    // Season labels come from the data, so a new season's CSVs retitle the app.
    document.title = `South Delta Szn — ${DATA.season} WMA Draw Planner`;
    $(".brand-text small").textContent = `${DATA.season} WMA Draw Planner`;
    $("#season-banner").hidden = !isStaleSeason();
    $("#season-banner-text").textContent =
      `Showing the ${DATA.season} draw listings. It's ${new Date().getFullYear()} — ` +
      `drop the current season's CSVs into data/ and re-run build_app_data.py to refresh.`;

    // Theme
    const theme = read(STORE.theme, "dark");
    document.documentElement.dataset.theme = theme;
    $("#theme-toggle").addEventListener("click", () => {
      const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
      document.documentElement.dataset.theme = next;
      write(STORE.theme, next);
    });

    // Radius controls
    const radiusToggle = $("#radius-toggle");
    const radiusRange = $("#radius-range");
    radiusToggle.checked = state.radiusOn;
    radiusRange.value = state.radiusMin;

    const syncRadiusLabels = () => {
      $("#radius-out").textContent = `${state.radiusMin} min`;
      $("#radius-label").textContent = fmtDrive(state.radiusMin);
    };
    syncRadiusLabels();

    radiusToggle.addEventListener("change", () => {
      state.radiusOn = radiusToggle.checked;
      write(STORE.radiusOn, state.radiusOn);
      refresh();
    });
    radiusRange.addEventListener("input", () => {
      state.radiusMin = Number(radiusRange.value);
      write(STORE.radiusMin, state.radiusMin);
      syncRadiusLabels();
      refresh();
    });

    // Tabs
    $("#tabs").addEventListener("click", (e) => {
      const tab = e.target.closest(".tab");
      if (tab) setView(tab.dataset.view);
    });

    // Filters
    $("#filter-wma").innerHTML = '<option value="">All areas</option>' +
      DATA.wmas.map((w) => `<option value="${w.name}">${w.name}</option>`).join("");

    const months = [...new Set(DATA.hunts.map((h) => monthKey(h.start)))].sort();
    $("#filter-month").innerHTML = '<option value="">All months</option>' +
      months.map((m) => `<option value="${m}">${monthLabel(m)}</option>`).join("");

    $("#search").addEventListener("input", (e) => { state.search = e.target.value; renderHunts(); });
    $("#filter-wma").addEventListener("change", (e) => { state.wma = e.target.value; renderHunts(); renderCalendar(); });
    $("#filter-month").addEventListener("change", (e) => { state.month = e.target.value; renderHunts(); renderCalendar(); });
    $("#sort").addEventListener("change", (e) => { state.sort = e.target.value; renderHunts(); });

    $("#type-chips").addEventListener("click", (e) => {
      const chip = e.target.closest(".chip");
      if (!chip) return;
      const type = chip.dataset.type;
      if (state.types.has(type)) state.types.delete(type); else state.types.add(type);
      renderChips(); renderHunts(); renderCalendar();
    });

    // Cards: star vs. open
    document.addEventListener("click", (e) => {
      const starBtn = e.target.closest("[data-star]");
      if (starBtn) { e.stopPropagation(); toggleStar(starBtn.dataset.star); return; }
      const card = e.target.closest(".hunt");
      if (card) openDrawer(card.dataset.id);
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeDrawer();
      if (e.key === "Enter") {
        const card = e.target.closest?.(".hunt");
        if (card) openDrawer(card.dataset.id);
      }
    });

    $("#drawer-close").addEventListener("click", closeDrawer);
    $("#drawer-backdrop").addEventListener("click", closeDrawer);

    // Export / clear
    $("#export-csv").addEventListener("click", exportCsv);
    $("#export-ics").addEventListener("click", exportIcs);
    $("#clear-shortlist").addEventListener("click", () => {
      if (!state.shortlist.size || !confirm("Clear the whole shortlist?")) return;
      state.shortlist.clear();
      write(STORE.shortlist, []);
      renderHunts(); renderShortlist();
    });

    renderHunters();
    refresh();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
