/* skill-bars.js — animates the skill proficiency bars from 0% to their
 * target percentage when they scroll into view.
 */
(function () {
  var rows = document.querySelectorAll('.skill-bar-row');
  if (!rows.length) return;

  var animated = false;

  function animate() {
    if (animated) return;
    animated = true;

    rows.forEach(function (row, i) {
      var fill = row.querySelector('.skill-bar-fill');
      var pct = parseInt(row.getAttribute('data-pct'), 10) || 0;
      if (!fill) return;

      // Stagger each bar slightly so they fill one after another.
      setTimeout(function () {
        fill.style.width = pct + '%';
      }, i * 120);
    });
  }

  var reduce = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (reduce) {
    // Skip animation, set bars to their final width immediately.
    rows.forEach(function (row) {
      var fill = row.querySelector('.skill-bar-fill');
      var pct = row.getAttribute('data-pct') || '0';
      if (fill) fill.style.width = pct + '%';
    });
    return;
  }

  if ('IntersectionObserver' in window) {
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { animate(); obs.disconnect(); }
      });
    }, { threshold: 0.2 });
    obs.observe(rows[0].closest('.skills-bars') || rows[0]);
  } else {
    animate();
  }
})();
