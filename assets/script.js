// Theme toggle with persistence
(function () {
  const root = document.documentElement;
  const preferred = localStorage.getItem("theme");
  if (preferred) root.setAttribute("data-theme", preferred);

  const btn = document.getElementById("themeToggle");
  if (btn) {
    btn.addEventListener("click", () => {
      const current = root.getAttribute("data-theme");
      const next = current === "light" ? "dark" : "light";
      if (!current) {
        // If not set, infer from system; then toggle
        const systemDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
        root.setAttribute("data-theme", systemDark ? "light" : "light"); // force set to ensure next works
      }
      const newTheme = (root.getAttribute("data-theme") || "dark") === "light" ? "dark" : "light";
      root.setAttribute("data-theme", newTheme);
      localStorage.setItem("theme", newTheme);
      btn.textContent = newTheme === "light" ? "🌙" : "☀️";
    });
  }

  // Set initial icon
  if (btn) {
    const t = root.getAttribute("data-theme");
    btn.textContent = t === "light" ? "🌙" : "☀️";
  }

  // Year in footer
  const y = document.getElementById("year");
  if (y) y.textContent = String(new Date().getFullYear());
})();

