// The about page: theme shared with the app, and a copy button per snippet.
// Pure helpers live in about-copy.js so the tests can exercise them without
// a DOM.
import { copyLabel } from "./about-copy.js";

/** The theme the app last stored, else the OS preference. */
function initialTheme() {
  let stored = null;
  try { stored = localStorage.getItem("atlas-theme"); } catch { /* fine */ }
  if (stored === "light" || stored === "dark") return stored;
  return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

let theme = initialTheme();

function applyTheme() {
  document.documentElement.dataset.theme = theme;
  const btn = document.getElementById("themebtn");
  if (btn) btn.textContent = theme === "dark" ? "☀" : "◐";
}

applyTheme();

document.getElementById("themebtn")?.addEventListener("click", () => {
  theme = theme === "dark" ? "light" : "dark";
  // The app reads the same key, so the choice follows the reader back.
  try { localStorage.setItem("atlas-theme", theme); } catch { /* fine */ }
  applyTheme();
});

// A copy button on every [data-copy] block. Added here rather than in the
// markup so a snippet never ships a button that does nothing.
for (const box of document.querySelectorAll("[data-copy]")) {
  const pre = box.querySelector("pre");
  if (!pre) continue;
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "copy";
  btn.textContent = copyLabel("idle");
  btn.addEventListener("click", async () => {
    try {
      // A hidden or unfocused document can leave writeText pending for ever,
      // which would leave the button saying nothing at all. Give up after a
      // second and tell the reader to copy by hand instead.
      await Promise.race([
        navigator.clipboard.writeText(pre.textContent.trim()),
        new Promise((_, reject) => setTimeout(reject, 1000)),
      ]);
      btn.textContent = copyLabel("done");
      btn.classList.add("done");
    } catch {
      btn.textContent = copyLabel("fail");
    }
    setTimeout(() => {
      btn.textContent = copyLabel("idle");
      btn.classList.remove("done");
    }, 1600);
  });
  box.appendChild(btn);
}

// The queries section ships closed. A link to it — the nav, or a URL someone
// shared — should open it, or the reader lands on a collapsed heading and
// sees nothing. Covers both the initial hash and later in-page clicks.
const queriesFold = document.getElementById("queries-detail");

function openFoldFor(hash) {
  if (hash === "#queries" && queriesFold) queriesFold.open = true;
}

if (queriesFold) {
  const label = queriesFold.querySelector(".fold-label");
  queriesFold.addEventListener("toggle", () => {
    if (label) {
      label.textContent = queriesFold.open
        ? "Hide the queries"
        : "Show the queries";
    }
  });
}

openFoldFor(location.hash);
window.addEventListener("hashchange", () => openFoldFor(location.hash));
