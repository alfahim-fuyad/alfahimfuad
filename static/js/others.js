/* others.js — wires the game & video cards to the embed modal.
 *
 * Behaviour:
 *  - Clicking a card (or its Play button) opens a shared modal that loads
 *    the embed URL into an <iframe>.
 *  - The "Open original ↗" button under the iframe links to the original
 *    embed URL in a new tab.
 *  - Clicking the backdrop or the close button, or pressing Esc, closes the
 *    modal and STOPS playback by resetting the iframe src to about:blank
 *    (so embedded audio/video doesn't keep playing in the background).
 */
(function () {
  var modal = document.getElementById('othersEmbedModal');
  if (!modal) return;

  var frame = document.getElementById('othersEmbedFrame');
  var titleEl = document.getElementById('othersEmbedTitle');
  var openLink = document.getElementById('othersEmbedOpen');

  function openEmbed(embedUrl, title) {
    if (!embedUrl) return;
    if (title) titleEl.textContent = title;
    frame.setAttribute('src', embedUrl);
    if (openLink) openLink.setAttribute('href', embedUrl);
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeEmbed() {
    modal.classList.remove('open');
    // Stop any playback by clearing the iframe src.
    frame.setAttribute('src', 'about:blank');
    document.body.style.overflow = '';
  }

  function bindCard(card) {
    var embedUrl = card.getAttribute('data-embed');
    var title = card.getAttribute('data-title') || '';

    // The whole card opens the modal — except a Play button which we
    // let bubble naturally so the same handler runs once.
    card.addEventListener('click', function (e) {
      // Don't double-fire when the inner Play button is clicked.
      if (e.target.closest('[data-play]')) {
        e.preventDefault();
      }
      openEmbed(embedUrl, title);
    });
  }

  document.querySelectorAll('[data-game-card], [data-video-card]').forEach(bindCard);

  modal.addEventListener('click', function (e) {
    if (e.target === modal || e.target.hasAttribute('data-close')) {
      closeEmbed();
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && modal.classList.contains('open')) {
      closeEmbed();
    }
  });
})();
