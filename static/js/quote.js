/* quote.js — rotating developer quote + scrolling tech-stack marquee.
 *
 * The quote rotator cross-fades through a curated list every ~8s.
 * The marquee lists the tech stack and scrolls infinitely (paused on
 * hover, disabled under prefers-reduced-motion).
 */
(function () {

  /* ---- QUOTE ROTATOR ---- */
  var quoteText = document.getElementById('quoteText');
  var quoteAuthor = document.getElementById('quoteAuthor');
  if (quoteText && quoteAuthor) {

    var QUOTES = [
      { q: "Any fool can write code that a computer understands. Good programmers write code that humans understand.", a: "Martin Fowler" },
      { q: "Simplicity is the soul of efficiency.", a: "Austin Freeman" },
      { q: "First, solve the problem. Then write the code.", a: "John Johnson" },
      { q: "Code is like humor. When you have to explain it, it's bad.", a: "Cory House" },
      { q: "The best error message is the one that never shows up.", a: "Thomas Fuchs" },
      { q: "Programs must be written for people to read, and only incidentally for machines to execute.", a: "Harold Abelson" },
      { q: "Talk is cheap. Show me the code.", a: "Linus Torvalds" },
      { q: "Premature optimization is the root of all evil.", a: "Donald Knuth" },
      { q: "It always seems impossible until it's done.", a: "Nelson Mandela" },
      { q: "Data is the new oil. It's valuable, but unrefined it's useless.", a: "Clive Humby" },
    ];

    var idx = 0;

    function render(advance) {
      var next = (idx + 1) % QUOTES.length;
      var item = QUOTES[advance ? next : idx];
      // Fade out, swap, fade in.
      quoteText.style.opacity = '0';
      setTimeout(function () {
        quoteText.childNodes[0].nodeValue = item.q + ' ';
        quoteAuthor.textContent = '— ' + item.a;
        quoteText.style.opacity = '1';
      }, 380);
      if (advance) idx = next;
    }

    // Initial render — no fade.
    var first = QUOTES[0];
    quoteText.childNodes[0].nodeValue = first.q + ' ';
    quoteAuthor.textContent = '— ' + first.a;
    quoteText.style.opacity = '1';
    idx = 0;

    var reduce = window.matchMedia &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (!reduce) {
      var timerId = null;
      function start() {
        if (timerId) return;
        timerId = setInterval(function () { render(true); }, 8000);
      }
      function stop() { clearInterval(timerId); timerId = null; }
      document.addEventListener('visibilitychange', function () {
        if (document.hidden) stop(); else start();
      });
      start();
    }
  }


  /* ---- TECH STACK MARQUEE ---- */
  var track = document.getElementById('marqueeTrack');
  if (track) {
    var STACK = [
      'Python', 'Django', 'FastAPI', 'PostgreSQL', 'Pandas', 'NumPy',
      'scikit-learn', 'TensorFlow', 'PyTorch', 'JavaScript', 'HTML / CSS',
      'Git & GitHub', 'Docker', 'Linux', 'Gunicorn', 'REST APIs',
    ];

    // Build the items twice so the marquee can loop seamlessly (-50%).
    var html = '';
    for (var pass = 0; pass < 2; pass++) {
      STACK.forEach(function (name) {
        html += '<span class="marquee-item"><span class="marquee-dot"></span>' + name + '</span>';
      });
    }
    track.innerHTML = html;
  }

})();
