/* =========================================================
   SHARED THEME ADAPTER — SkillSwap (FINAL)
========================================================= */

const THEME_KEY = "skillswap_theme";

function setTheme(theme) {
  document.body.classList.toggle("dark", theme === "dark");
  localStorage.setItem(THEME_KEY, theme);
}

function toggleTheme() {
  const next =
    document.body.classList.contains("dark") ? "light" : "dark";
  setTheme(next);
}

function initTheme() {
  const saved = localStorage.getItem(THEME_KEY) || "light";
  setTheme(saved);
}

// Sync across tabs/windows
window.addEventListener("storage", e => {
  if (e.key === THEME_KEY && e.newValue) {
    setTheme(e.newValue);
  }
});

// 🔒 expose explicitly (important)
window.toggleTheme = toggleTheme;
window.initTheme = initTheme;
