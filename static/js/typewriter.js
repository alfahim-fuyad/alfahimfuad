/* typewriter.js — rotating typing + deleting animation below the hero name.
 *
 * Cycles through a list of sentences, typing each character-by-character,
 * pausing, then deleting smoothly before typing the next one.
 *
 * - Uses the existing --cyan accent color (inherited from .hero-typewriter).
 * - Prevents layout shift: the container has a fixed min-height and the
 *   text node uses white-space: pre so it never wraps mid-type.
 * - Respects prefers-reduced-motion: shows the first sentence statically
 *   with a steady cursor, no typing animation.
 */
(function () {
  var el = document.getElementById('typewriterText');
  if (!el) return;

  var SENTENCES = [
    "Data Scientist  •  ML Engineer  •  AI Builder",
  ];

  var reduce = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (reduce) {
    // Reduced-motion: show the first sentence statically, steady cursor.
    el.textContent = SENTENCES[0];
    return;
  }

  // Timing (ms). Tuned to feel natural but not slow.
  var TYPE_SPEED   = 55;   // per character while typing
  var TYPE_JITTER  = 35;   // random extra 0..35ms per char for realism
  var ERASE_SPEED  = 28;   // per character while deleting
  var PAUSE_FULL   = 1800; // pause after a sentence is fully typed
  var PAUSE_EMPTY  = 280;  // pause after a sentence is fully erased

  var idx = 0;       // which sentence we're on
  var charIdx = 0;   // how many chars of the current sentence are shown
  var erasing = false;
  var timerId = null;

  function tick() {
    var sentence = SENTENCES[idx];

    if (!erasing) {
      // Typing forward
      charIdx++;
      el.textContent = sentence.slice(0, charIdx);

      if (charIdx >= sentence.length) {
        // Fully typed — pause, then start erasing.
        timerId = setTimeout(function () {
          erasing = true;
          tick();
        }, PAUSE_FULL);
        return;
      }
      // Schedule next char with a small random jitter for realism.
      var delay = TYPE_SPEED + Math.floor(Math.random() * TYPE_JITTER);
      timerId = setTimeout(tick, delay);

    } else {
      // Erasing backward
      charIdx--;
      el.textContent = sentence.slice(0, charIdx);

      if (charIdx <= 0) {
        // Fully erased — move to next sentence, pause, then type.
        erasing = false;
        idx = (idx + 1) % SENTENCES.length;
        timerId = setTimeout(tick, PAUSE_EMPTY);
        return;
      }
      timerId = setTimeout(tick, ERASE_SPEED);
    }
  }

  // Pause when the tab is hidden so we don't burn CPU in the background.
  function start() {
    if (timerId) return;
    tick();
  }
  function stop() {
    if (timerId) { clearTimeout(timerId); timerId = null; }
  }

  document.addEventListener('visibilitychange', function () {
    if (document.hidden) stop();
    else start();
  });

  // Kick off.
  start();
})();
