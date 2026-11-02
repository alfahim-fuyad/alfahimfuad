/* gh-stats.js — animated count-up of live GitHub stats.
 *
 * Fetches /github-stats/ (cached 5 min on the server), then animates
 * each counter from 0 to its target value when the stats grid scrolls
 * into view.
 */
(function () {
  var grid = document.getElementById('ghStatsGrid');
  if (!grid) return;

  var els = {
    repos: document.getElementById('ghRepos'),
    stars: document.getElementById('ghStars'),
    forks: document.getElementById('ghForks'),
    followers: document.getElementById('ghFollowers'),
  };

  function animateCount(el, target, duration) {
    if (!el) return;
    target = parseInt(target, 10) || 0;
    duration = duration || 1400;
    var start = null;
    function step(ts) {
      if (!start) start = ts;
      var progress = Math.min((ts - start) / duration, 1);
      // Ease-out cubic for a nice deceleration.
      var eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.floor(eased * target).toLocaleString();
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = target.toLocaleString();
    }
    requestAnimationFrame(step);
  }

  var animated = false;

  function run() {
    if (animated) return;
    animated = true;

    fetch('/github-stats/', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data || !data.ok) {
          // GitHub API unavailable — show dashes instead of 0.
          Object.keys(els).forEach(function (k) {
            if (els[k]) els[k].textContent = '—';
          });
          return;
        }
        animateCount(els.repos, data.public_repos);
        animateCount(els.stars, data.stars);
        animateCount(els.forks, data.forks);
        animateCount(els.followers, data.followers);
      })
      .catch(function () {
        Object.keys(els).forEach(function (k) {
          if (els[k]) els[k].textContent = '—';
        });
      });
  }

  // Trigger when the grid scrolls into view.
  var reduce = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (reduce) {
    // Skip animation, just fetch and show the final numbers.
    animated = false;
    fetch('/github-stats/', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data || !data.ok) return;
        if (els.repos) els.repos.textContent = data.public_repos.toLocaleString();
        if (els.stars) els.stars.textContent = data.stars.toLocaleString();
        if (els.forks) els.forks.textContent = data.forks.toLocaleString();
        if (els.followers) els.followers.textContent = data.followers.toLocaleString();
      });
    return;
  }

  if ('IntersectionObserver' in window) {
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { run(); obs.disconnect(); }
      });
    }, { threshold: 0.3 });
    obs.observe(grid);
  } else {
    run();
  }
})();
