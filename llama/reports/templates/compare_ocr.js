// ENGINES (list of model run stems) is injected by the report generator.
const STORE_KEY = "ocr_votes:" + ENGINES.join("|");

// votes: keyed by "<engine>|<source>", value "up" or "down"
let votes = {};
try {
  votes = JSON.parse(localStorage.getItem(STORE_KEY) || "{}");
} catch (err) {
  votes = {};
}

function counts() {
  const result = Object.fromEntries(ENGINES.map((s) => [s, { up: 0, down: 0 }]));
  for (const [key, value] of Object.entries(votes)) {
    const engine = key.split("|")[0];
    if (result[engine] && (value === "up" || value === "down")) {
      result[engine][value] += 1;
    }
  }
  return result;
}

function refresh() {
  const total = counts();
  for (const engine of ENGINES) {
    document.getElementById("up-" + engine).textContent = "▲ " + total[engine].up;
    document.getElementById("down-" + engine).textContent = "▼ " + total[engine].down;
  }
  localStorage.setItem(STORE_KEY, JSON.stringify(votes));
  document.querySelectorAll(".vote-btn").forEach((btn) => {
    const key = btn.dataset.engine + "|" + btn.dataset.source;
    btn.classList.toggle("active-up", votes[key] === "up");
    btn.classList.toggle("active-down", votes[key] === "down");
  });
}

document.querySelectorAll(".vote-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const key = btn.dataset.engine + "|" + btn.dataset.source;
    const value = btn.getAttribute("aria-label");
    if (votes[key] === value) delete votes[key];
    else votes[key] = value;
    refresh();
  });
});

function state() {
  return {
    timestamp: new Date().toISOString(),
    engines: ENGINES,
    counts: counts(),
    votes: votes,
  };
}

document.getElementById("save").addEventListener("click", () => {
  const line = JSON.stringify(state());
  const blob = new Blob([line + "\n"], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "ocr_votes_" + state().timestamp.replace(/[:.]/g, "-") + ".json";
  a.click();
  URL.revokeObjectURL(url);
  console.log(line);
});

document.getElementById("load").addEventListener("click", () => {
  document.getElementById("load-input").click();
});

document.getElementById("load-input").addEventListener("change", (ev) => {
  const file = ev.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const loaded_state = JSON.parse(reader.result);
      if (Array.isArray(loaded_state.engines) && loaded_state.engines.join("|") !== ENGINES.join("|")) {
        console.warn("Engine mismatch: state was saved for " + loaded_state.engines.join(", "));
      }
      const loaded = {};
      for (const [key, value] of Object.entries(loaded_state.votes || {})) {
        const engine = key.split("|")[0];
        if ((value === "up" || value === "down") && ENGINES.includes(engine)) {
          loaded[key] = value;
        }
      }
      votes = loaded;
      refresh();
      console.log("Loaded " + Object.keys(votes).length + " votes from " + file.name);
    } catch (err) {
      alert("Failed to load state: " + err.message);
    }
  };
  reader.readAsText(file);
  ev.target.value = "";
});

// --- Theme: light/dark toggle, persisted in localStorage ---
const THEME_KEY = "ocr_compare_theme";
const themeBtn = document.getElementById("theme");
let theme = "light";
try {
  theme = localStorage.getItem(THEME_KEY) || "light";
} catch (err) {
  theme = "light";
}
function applyTheme(t) {
  document.documentElement.setAttribute("data-theme", t);
  themeBtn.textContent = t === "dark" ? "☀️" : "🌙";
}
applyTheme(theme);
themeBtn.addEventListener("click", () => {
  theme = theme === "dark" ? "light" : "dark";
  localStorage.setItem(THEME_KEY, theme);
  applyTheme(theme);
});

// --- Lightbox: click a thumbnail to view the full-size image ---
const lightbox = document.createElement("div");
lightbox.id = "lightbox";
const lbBar = document.createElement("div");
lbBar.id = "lightbox-bar";
const lbTitle = document.createElement("span");
const lbCloseBtn = document.createElement("button");
lbCloseBtn.id = "lightbox-close";
lbCloseBtn.setAttribute("aria-label", "close");
lbCloseBtn.textContent = "×";
lbBar.append(lbTitle, lbCloseBtn);
const lightboxImg = document.createElement("img");
const lightboxNote = document.createElement("div");
lightboxNote.id = "lightbox-note";
lightboxNote.textContent = "drag bar to move · scroll to zoom · drag image to pan · esc to close";
lightbox.append(lbBar, lightboxImg, lightboxNote);
document.body.append(lightbox);

const BAR_H = 32; // title bar height, image area starts below it

let lbScale = 1;
let lbX = 0;
let lbY = 0;
let lbFit = 1;

function lbApply() {
  lightboxImg.style.transform = `translate(${lbX}px, ${lbY + BAR_H}px) scale(${lbScale})`;
}

function lbCenter() {
  const pw = lightbox.clientWidth;
  const ph = lightbox.clientHeight - BAR_H;
  const nw = lightboxImg.naturalWidth || 1;
  const nh = lightboxImg.naturalHeight || 1;
  lbFit = Math.min(pw / nw, ph / nh, 1);
  lbScale = lbFit;
  lbX = (pw - nw * lbScale) / 2;
  lbY = (ph - nh * lbScale) / 2;
  lbApply();
}

// px, py are panel-relative coordinates
function lbZoomAt(px, py, factor) {
  const nw = lightboxImg.naturalWidth || 1;
  const maxZoom = Math.max(2, nw / lightbox.clientWidth); // up to original pixels
  const next = Math.min(Math.max(lbScale * factor, lbFit / 4), maxZoom);
  // keep the point under the cursor fixed
  const ux = (px - lbX) / lbScale;
  const uy = (py - lbY) / lbScale;
  lbScale = next;
  lbX = px - ux * lbScale;
  lbY = py - uy * lbScale;
  lbApply();
}

function lbOpen(sourceImg) {
  lbTitle.textContent = (sourceImg.dataset.full || sourceImg.alt || "").split("/").pop();
  lightboxImg.onload = lbCenter;
  lightboxImg.onerror = () => {
    if (lightboxImg.src !== sourceImg.dataset.thumb) {
      lightboxImg.src = sourceImg.dataset.thumb; // fall back to embedded thumbnail
    }
  };
  lightboxImg.src = sourceImg.dataset.full || sourceImg.src;
  lightbox.classList.add("open");
}

function lbClose() {
  lightbox.classList.remove("open");
  lightboxImg.removeAttribute("src");
}

document.querySelectorAll("td.source img").forEach((img) => {
  img.addEventListener("click", (e) => {
    e.stopPropagation();
    lbOpen(img);
  });
});

lbCloseBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  lbClose();
});

lightbox.addEventListener("click", (e) => {
  if (e.target === lightbox) lbClose();
});

lightboxImg.addEventListener("wheel", (e) => {
  e.preventDefault();
  const rect = lightbox.getBoundingClientRect();
  lbZoomAt(e.clientX - rect.left, e.clientY - rect.top - BAR_H, e.deltaY < 0 ? 1.25 : 1 / 1.25);
}, { passive: false });

let dragging = null; // image panning
let panelDrag = null; // panel moving
lightboxImg.addEventListener("mousedown", (e) => {
  e.preventDefault();
  dragging = { px: e.clientX, py: e.clientY, x: lbX, y: lbY };
});
lbBar.addEventListener("mousedown", (e) => {
  e.preventDefault();
  const rect = lightbox.getBoundingClientRect();
  panelDrag = { px: e.clientX, py: e.clientY, left: rect.left, top: rect.top };
});
window.addEventListener("mousemove", (e) => {
  if (panelDrag) {
    lightbox.style.left = panelDrag.left + (e.clientX - panelDrag.px) + "px";
    lightbox.style.top = panelDrag.top + (e.clientY - panelDrag.py) + "px";
    lightbox.style.right = "auto";
  }
  if (!dragging) return;
  lbX = dragging.x + (e.clientX - dragging.px);
  lbY = dragging.y + (e.clientY - dragging.py);
  lbApply();
});
window.addEventListener("mouseup", () => {
  dragging = null;
  panelDrag = null;
});
window.addEventListener("keydown", (e) => {
  if (e.key === "Escape") lbClose();
});
window.addEventListener("resize", () => {
  if (lightbox.classList.contains("open")) lbCenter();
});

refresh();
