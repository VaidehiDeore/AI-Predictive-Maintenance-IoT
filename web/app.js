
const $ = (id) => document.getElementById(id);

let timer = null;
let localReadings = [];
let activeView = "overview";

const pct = (v) => `${Math.round((Number(v) || 0) * 100)}%`;

// Sidebar navigation: show a focused view for each menu item.
const viewConfig = {
  overview: {
    title: "Overview",
    sections: ["overview", "monitoring", "analytics", "equipment", "alerts"],
  },
  equipment: {
    title: "Equipment",
    sections: ["equipment"],
  },
  monitoring: {
    title: "Live Monitoring",
    sections: ["monitoring"],
  },
  analytics: {
    title: "Analytics",
    sections: ["analytics"],
  },
  alerts: {
    title: "Maintenance Alerts",
    sections: ["alerts"],
  },
};

function setPage(view, updateHash = true) {
  if (!viewConfig[view]) view = "overview";
  activeView = view;

  const visibleSections = viewConfig[view].sections;

  // The welcome header and KPI cards are part of the overview.
  const overviewExtras = [
    document.querySelector(".welcome"),
    document.querySelector(".notice"),
    document.querySelector(".kpi-grid"),
  ];

  overviewExtras.forEach((element) => {
    if (element) {
      element.hidden = view !== "overview";
    }
  });

  // Show only the sections belonging to the selected view.
  ["monitoring", "analytics", "equipment", "alerts"].forEach((id) => {
    const section = $(id);
    if (section) {
      section.hidden = !visibleSections.includes(id);
    }
  });

  // The risk panel belongs to overview; keep it with the telemetry
  // only when overview is selected, rather than leaving it orphaned.
  const riskPanel = document.querySelector(".risk-panel");
  if (riskPanel) {
    riskPanel.hidden = view !== "overview";
  }

  // Preserve the grid layout when the risk panel is hidden.
  const mainContentGrid = document.querySelector(".content-grid");
  if (mainContentGrid) {
    mainContentGrid.hidden =
      view !== "overview" &&
      !visibleSections.includes("monitoring") &&
      !visibleSections.includes("analytics");
  }

  document.querySelectorAll(".nav-item").forEach((link) => {
    const target = link.getAttribute("href")?.replace("#", "");
    link.classList.toggle("active", target === view);
    if (target === view) {
      link.setAttribute("aria-current", "page");
    } else {
      link.removeAttribute("aria-current");
    }
  });

  const crumb = document.querySelector(".crumb");
  if (crumb) {
    crumb.innerHTML = `<span>Workspace</span><b>/</b> ${viewConfig[view].title}`;
  }

  if (updateHash && location.hash !== `#${view}`) {
    history.replaceState(null, "", `#${view}`);
  }

  window.scrollTo({ top: 0, behavior: "smooth" });
}

function toast(message) {
  const el = $("toast");
  if (!el) return;

  el.textContent = message;
  el.classList.add("show");
  clearTimeout(toast._t);
  toast._t = setTimeout(() => el.classList.remove("show"), 2800);
}

function setRisk(prob, risk, recommendation) {
  const p = Math.max(0, Math.min(1, Number(prob) || 0));
  const value = Math.round(p * 100);

  if ($("risk-score")) $("risk-score").innerHTML = `${value}<small>%</small>`;
  if ($("gauge-number")) $("gauge-number").textContent = value;

  if ($("gauge-fill")) {
    $("gauge-fill").setAttribute("stroke-dasharray", `${value} 100`);
    const color =
      risk === "CRITICAL" || risk === "HIGH"
        ? "#ff6e72"
        : risk === "WATCH"
          ? "#ffbd67"
          : "#62d7b0";
    $("gauge-fill").style.stroke = color;
  }

  const badge = $("risk-badge");
  if (badge) {
    badge.textContent = `${risk} RISK`;
    badge.className = `risk-badge ${String(risk).toLowerCase()}`;
  }

  if ($("recommendation")) {
    $("recommendation").textContent =
      recommendation || "Continue routine monitoring.";
  }

  if ($("health-score")) {
    $("health-score").innerHTML = `${Math.max(0, 100 - value)}<small>/100</small>`;
  }

  if ($("risk-note")) $("risk-note").textContent = "Latest model probability";
  if ($("confidence")) {
    $("confidence").textContent =
      `${Math.round((1 - Math.abs(p - 0.5) * 0.55) * 100)}%`;
  }
}

function setSensor(reading) {
  const t = Number(reading.temperature_c || 0);
  const v = Number(reading.vibration_mm_s || 0);
  const c = Number(reading.current_a || 0);

  if ($("temp-val")) $("temp-val").innerHTML = `${t.toFixed(1)} <small>°C</small>`;
  if ($("vib-val")) $("vib-val").innerHTML = `${v.toFixed(2)} <small>mm/s</small>`;
  if ($("current-val")) $("current-val").innerHTML = `${c.toFixed(1)} <small>A</small>`;

  if ($("temp-meter")) $("temp-meter").style.width = `${Math.min(100, t / 110 * 100)}%`;
  if ($("vib-meter")) $("vib-meter").style.width = `${Math.min(100, v / 12 * 100)}%`;
  if ($("current-meter")) $("current-meter").style.width = `${Math.min(100, c / 20 * 100)}%`;

  if ($("operating-mode")) $("operating-mode").textContent = "Monitoring";

  localReadings.unshift({ t: Math.min(100, t), v: Math.min(100, v * 8) });
  localReadings = localReadings.slice(0, 12);
  drawTrend();
}

function drawTrend() {
  if (!localReadings.length) return;

  const points = (key) => {
    const vals = [...localReadings].reverse();
    return vals
      .map((r, i) => `${i * (600 / Math.max(1, vals.length - 1))},${178 - (r[key] / 100) * 160}`)
      .join(" L");
  };

  if ($("temp-line")) $("temp-line").setAttribute("d", `M${points("t")}`);
  if ($("vib-line")) $("vib-line").setAttribute("d", `M${points("v")}`);
}

function renderMetrics(metrics = {}) {
  [["accuracy", "accuracy"], ["precision", "precision"], ["recall", "recall"], ["f1_score", "f1"]]
    .forEach(([key, id]) => {
      const value = Number(metrics[key] || 0);
      const bar = $(`metric-${id}`);
      const text = $(`metric-${id}-text`);

      if (bar) bar.style.width = `${value * 100}%`;
      if (text) text.textContent = pct(value);
    });
}

function renderAlerts(history = []) {
  const alerts = history
    .filter((x) => ["HIGH", "CRITICAL"].includes(x.risk_level))
    .slice(0, 4);

  if ($("open-alerts")) $("open-alerts").textContent = String(alerts.length).padStart(2, "0");
  if ($("alert-count")) $("alert-count").textContent = alerts.length;
  if ($("alert-summary")) {
    $("alert-summary").textContent = alerts.length
      ? `${alerts.length} NEED REVIEW`
      : "NO NEW ALERTS";
  }

  const list = $("alerts-list");
  if (!list) return;

  if (!alerts.length) {
    list.innerHTML = `
      <div class="empty-alert">
        <span>✓</span>
        <div>
          <b>All clear for now</b>
          <small>No high-risk readings in the latest simulation window. Keep monitoring sensor trends.</small>
        </div>
      </div>`;
    return;
  }

  list.innerHTML = alerts.map((a) => `
    <div class="alert-item">
      <span class="alert-mark">⚑</span>
      <div class="alert-content">
        <b>${a.risk_level} · ${a.machine_id} failure risk</b>
        <small>${a.recommendation} · Temp ${Number(a.temperature_c).toFixed(1)}°C · Vibration ${Number(a.vibration_mm_s).toFixed(2)} mm/s</small>
      </div>
      <span class="alert-prob">${Math.round(a.failure_probability * 100)}%</span>
    </div>`).join("");
}

async function fetchOverview() {
  try {
    const response = await fetch("/api/overview");
    if (!response.ok) throw new Error("Could not load overview data");

    const data = await response.json();
    renderMetrics(data.metrics || {});

    if (data.latest) {
      setSensor(data.latest);
      setRisk(
        data.latest.failure_probability,
        data.latest.risk_level,
        data.latest.recommendation
      );
    }

    renderAlerts(data.history || []);

    if ($("stream-status")) {
      $("stream-status").textContent = data.simulation_running ? "STREAMING" : "STANDBY";
    }

    if ($("today")) {
      $("today").textContent = new Date().toLocaleDateString(undefined, {
        weekday: "short",
        month: "short",
        day: "numeric",
      }).toUpperCase();
    }
  } catch (e) {
    console.error("Overview refresh failed:", e);
  }
}

async function post(path, body = {}) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

async function startSimulation() {
  try {
    await post("/api/simulation/start");

    if ($("stream-status")) $("stream-status").textContent = "STREAMING";
    if ($("operating-mode")) $("operating-mode").textContent = "Running";

    if (!timer) timer = setInterval(fetchOverview, 2600);

    await fetchOverview();
    toast("Virtual sensor stream started.");
  } catch (e) {
    toast(e.message);
  }
}

async function stopSimulation() {
  try {
    await post("/api/simulation/stop");

    if ($("stream-status")) $("stream-status").textContent = "STANDBY";
    if ($("operating-mode")) $("operating-mode").textContent = "Paused";

    if (timer) {
      clearInterval(timer);
      timer = null;
    }

    await fetchOverview();
    toast("Simulation paused.");
  } catch (e) {
    toast(e.message);
  }
}

async function newPrediction() {
  const reading = {
    temperature_c: 78,
    vibration_mm_s: 5.8,
    current_a: 11.4,
    pressure_bar: 5.1,
    rpm: 1280,
    machine_age_years: 9,
    hours_since_maintenance: 620,
  };

  try {
    const result = await post("/api/predict", reading);
    setSensor(reading);
    setRisk(result.failure_probability, result.risk_level, result.recommendation);
    toast("Prediction generated from a sample high-load reading.");
  } catch (e) {
    toast(e.message);
  }
}

// Bind navigation to actual view changes.
document.querySelectorAll(".nav-item").forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    const view = link.getAttribute("href")?.replace("#", "") || "overview";
    setPage(view);
  });
});

// Support browser back/forward navigation.
window.addEventListener("hashchange", () => {
  setPage(location.hash.replace("#", "") || "overview", false);
});

if ($("start-btn")) $("start-btn").addEventListener("click", startSimulation);
if ($("stop-btn")) $("stop-btn").addEventListener("click", stopSimulation);
if ($("run-prediction")) $("run-prediction").addEventListener("click", newPrediction);

setPage(location.hash.replace("#", "") || "overview", false);
fetchOverview();
