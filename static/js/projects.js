/* projects.js — search, filter, sort, and grid/list toggle for the Projects page.
 *
 * All work happens client-side against the already-rendered project cards.
 * The cards carry data-* attributes (name, desc, lang, stars, updated,
 * showcase) that this script reads to decide what to show and in what
 * order.
 */
(function () {
  var grid = document.getElementById('projectGrid');
  if (!grid) return;

  var searchInput = document.getElementById('projSearch');
  var searchClear = document.getElementById('projSearchClear');
  var langFilter = document.getElementById('projLangFilter');
  var sortSelect = document.getElementById('projSort');
  var viewToggle = document.getElementById('projViewToggle');
  var countEl = document.getElementById('projCount');
  var noResults = document.getElementById('projNoResults');
  var resetBtn = document.getElementById('projReset');

  // Collect all project cards once.
  var cards = Array.prototype.slice.call(
    grid.querySelectorAll('.project-card')
  );

  // Build the language filter dropdown from the cards' data-lang values.
  var langs = {};
  cards.forEach(function (c) {
    var lang = (c.getAttribute('data-lang') || '').trim();
    if (lang) langs[lang] = (langs[lang] || 0) + 1;
  });
  Object.keys(langs).sort().forEach(function (lang) {
    var opt = document.createElement('option');
    opt.value = lang;
    opt.textContent = lang + ' (' + langs[lang] + ')';
    langFilter.appendChild(opt);
  });

  var totalCards = cards.length;

  function applyFilters() {
    var query = (searchInput.value || '').trim().toLowerCase();
    var lang = langFilter.value;
    var sort = sortSelect.value;

    // Build a list of [card, sortKey] pairs for the cards that match.
    var matching = [];
    cards.forEach(function (c) {
      var name = c.getAttribute('data-name') || '';
      var desc = c.getAttribute('data-desc') || '';
      var cLang = c.getAttribute('data-lang') || '';

      var matchesQuery = !query ||
        name.indexOf(query) !== -1 ||
        desc.indexOf(query) !== -1;
      var matchesLang = !lang || cLang === lang;

      if (matchesQuery && matchesLang) {
        matching.push(c);
      }
    });

    // Sort the matching cards.
    if (sort === 'stars') {
      matching.sort(function (a, b) {
        return (parseInt(b.getAttribute('data-stars'), 10) || 0) -
               (parseInt(a.getAttribute('data-stars'), 10) || 0);
      });
    } else if (sort === 'name') {
      matching.sort(function (a, b) {
        return (a.getAttribute('data-name') || '').localeCompare(
               (b.getAttribute('data-name') || ''));
      });
    } else if (sort === 'updated') {
      matching.sort(function (a, b) {
        return (b.getAttribute('data-updated') || '').localeCompare(
               (a.getAttribute('data-updated') || ''));
      });
    }
    // 'default' = original DOM order, no sort.

    // Hide every card first, then re-append the matching ones in order.
    cards.forEach(function (c) { c.style.display = 'none'; });
    matching.forEach(function (c) {
      c.style.display = '';
      grid.appendChild(c);  // re-append → moves to the end, preserving order
    });

    // Update the count line.
    if (countEl) {
      if (matching.length === totalCards) {
        countEl.textContent = totalCards + ' project' + (totalCards === 1 ? '' : 's');
      } else {
        countEl.textContent = matching.length + ' of ' + totalCards + ' projects';
      }
    }

    // Toggle the "no results" state.
    if (noResults) {
      noResults.style.display = (matching.length === 0 && totalCards > 0) ? 'block' : 'none';
    }

    // Toggle the clear-search × button.
    if (searchClear) {
      searchClear.style.display = query ? 'flex' : 'none';
    }
  }

  // Debounce typing so we don't reflow on every keystroke.
  var debounceId = null;
  searchInput.addEventListener('input', function () {
    clearTimeout(debounceId);
    debounceId = setTimeout(applyFilters, 120);
  });
  searchInput.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      searchInput.value = '';
      applyFilters();
      searchInput.blur();
    }
  });

  if (searchClear) {
    searchClear.addEventListener('click', function () {
      searchInput.value = '';
      applyFilters();
      searchInput.focus();
    });
  }

  langFilter.addEventListener('change', applyFilters);
  sortSelect.addEventListener('change', applyFilters);

  if (resetBtn) {
    resetBtn.addEventListener('click', function () {
      searchInput.value = '';
      langFilter.value = '';
      sortSelect.value = 'default';
      applyFilters();
    });
  }

  // Grid / list view toggle.
  if (viewToggle) {
    var iconGrid = viewToggle.querySelector('.icon-grid');
    var iconList = viewToggle.querySelector('.icon-list');
    viewToggle.addEventListener('click', function () {
      var isList = grid.classList.toggle('project-grid--list');
      if (iconGrid) iconGrid.style.display = isList ? 'none' : '';
      if (iconList) iconList.style.display = isList ? '' : 'none';
      try { localStorage.setItem('proj-view', isList ? 'list' : 'grid'); } catch (e) {}
    });
    // Restore saved preference.
    try {
      if (localStorage.getItem('proj-view') === 'list') {
        viewToggle.click();
      }
    } catch (e) {}
  }

  // Initial count.
  applyFilters();
})();
