/* theme.js — day/night theme toggle for fuadFolio.
 *
 * Behaviour:
 *  - The toggle button lives in the navbar (.theme-toggle).
 *  - The chosen theme is stored in localStorage under 'fuadfolio-theme'.
 *  - On first load, the stored theme wins; if none is stored, the OS
 *    preference (prefers-color-scheme: dark) decides; otherwise 'light'.
 *  - The <html data-theme="..."> attribute drives the CSS variables
 *    defined in style.css — both the original light theme AND the new
 *    dark theme.
 *  - The meta theme-color is updated to match the active theme so the
 *    mobile browser chrome follows along.
 *
 * The script is intentionally tiny and inline-loaded BEFORE the page
 * paints, to avoid a flash of the wrong theme.
 */
(function () {
  var STORAGE_KEY = 'fuadfolio-theme';
  var root = document.documentElement;
  var meta = document.querySelector('meta[name="theme-color"]');

  function resolveInitial() {
    var stored = null;
    try { stored = localStorage.getItem(STORAGE_KEY); } catch (e) {}
    if (stored === 'light' || stored === 'dark') return stored;
    if (window.matchMedia &&
        window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  }

  function apply(theme) {
    root.setAttribute('data-theme', theme);
    if (meta) {
      meta.setAttribute('content', theme === 'dark' ? '#0b1220' : '#eaf2ff');
    }
    // Update toggle button ARIA + icon swap.
    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      btn.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
      btn.setAttribute(
        'aria-label',
        theme === 'dark' ? 'Switch to day theme' : 'Switch to night theme'
      );
      btn.setAttribute('data-theme-current', theme);
    });
  }

  function toggle() {
    var current = root.getAttribute('data-theme') || 'light';
    var next = current === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem(STORAGE_KEY, next); } catch (e) {}
    apply(next);
  }

  // Apply before paint to prevent flash.
  apply(resolveInitial());

  // Bind the toggle button(s) once DOM is ready.
  function bind() {
    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      if (btn.__themeBound) return;
      btn.__themeBound = true;
      btn.addEventListener('click', toggle);
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bind);
  } else {
    bind();
  }

  // Follow OS changes only when the user hasn't explicitly chosen.
  if (window.matchMedia) {
    try {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener(
        'change', function (e) {
          var stored = null;
          try { stored = localStorage.getItem(STORAGE_KEY); } catch (err) {}
          if (stored === 'light' || stored === 'dark') return;
          apply(e.matches ? 'dark' : 'light');
        }
      );
    } catch (e) { /* older browsers */ }
  }
})();
