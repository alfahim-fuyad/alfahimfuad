/* scroll-utils.js — two small site-wide UX features:
 *
 * 1) Scroll-to-top button — fades in after the visitor scrolls down
 *    ~400px. Click → smooth-scrolls back to the top.
 * 2) Reading progress bar — a thin gradient line at the very top of
 *    the page that fills as the visitor scrolls, showing how far
 *    through the content they are.
 *
 * Both are lightweight, passive listeners — no performance impact.
 */
(function () {
  var scrollBtn = document.getElementById('scrollTopBtn');
  var progress = document.getElementById('readingProgress');

  var ticking = false;

  function update() {
    var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    var scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
    var pct = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;

    // Scroll-to-top button: visible after 400px of scrolling.
    if (scrollBtn) {
      if (scrollTop > 400) {
        scrollBtn.classList.add('visible');
      } else {
        scrollBtn.classList.remove('visible');
      }
    }

    // Reading progress bar: 0% → 100%.
    if (progress) {
      progress.style.width = pct + '%';
    }

    ticking = false;
  }

  function onScroll() {
    if (!ticking) {
      window.requestAnimationFrame(update);
      ticking = true;
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  update();  // initial state

  // Scroll-to-top click → smooth scroll to top.
  if (scrollBtn) {
    scrollBtn.addEventListener('click', function () {
      var reduce = window.matchMedia &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      window.scrollTo({
        top: 0,
        behavior: reduce ? 'auto' : 'smooth',
      });
    });
  }
})();
