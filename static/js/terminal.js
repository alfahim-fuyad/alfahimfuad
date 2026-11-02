/* terminal.js — interactive command prompt on the home page.
 *
 * The visitor types a command and gets a text answer about Fuad.
 * Everything runs client-side; no data is sent anywhere.
 *
 * Commands: help, whoami, about, skills, projects, experience,
 * certifications, education, contact, social, cv, ls, date,
 * echo [text], joke, theme [dark|light], game, clear, sudo
 */
(function () {
  var input = document.getElementById('termInput');
  var output = document.getElementById('termOutput');
  var body = document.getElementById('terminalBody');
  if (!input || !output || !body) return;

  // Pull site info from the footer socials (rendered server-side) so the
  // terminal answers match whatever the admin configured.
  var site = {
    name: 'Al Fahim Fuad',
    title: 'Data Scientist | ML Engineer | AI Builder',
    location: 'Dhaka, Bangladesh',
    email: '',
    github: '',
    linkedin: '',
    facebook: '',
  };
  try {
    var foot = document.querySelector('.site-foot');
    if (foot) {
      var mail = foot.querySelector('a[aria-label="Email"]');
      var gh = foot.querySelector('a[aria-label="GitHub"]');
      var li = foot.querySelector('a[aria-label="LinkedIn"]');
      var fb = foot.querySelector('a[aria-label="Facebook"]');
      if (mail) site.email = mail.getAttribute('href').replace(/^mailto:/, '');
      if (gh) site.github = gh.getAttribute('href');
      if (li) site.linkedin = li.getAttribute('href');
      if (fb) site.facebook = fb.getAttribute('href');
    }
  } catch (e) {}

  var history = [];
  var histIdx = -1;

  var JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "There are 10 kinds of people: those who understand binary and those who don't.",
    "I would tell you a UDP joke, but you might not get it.",
    "A SQL query walks into a bar, walks up to two tables and asks: 'Mind if I join you?'",
    "Why did the developer go broke? Because he used up all his cache.",
    "Debugging: removing the bugs. Programming: putting them in.",
    "How many programmers does it take to change a light bulb? None — that's a hardware problem.",
  ];

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function print(html, cls) {
    var div = document.createElement('div');
    div.className = 'term-line' + (cls ? ' ' + cls : '');
    div.innerHTML = html;
    output.appendChild(div);
    body.scrollTop = body.scrollHeight;
  }

  function printRaw(text, cls) {
    print(escapeHtml(text), cls);
  }

  function clearOutput() {
    output.innerHTML = '';
  }

  function scrollToGame() {
    var g = document.getElementById('snakeCanvas');
    if (g) g.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  function setTheme(theme) {
    if (theme !== 'dark' && theme !== 'light') {
      print("usage: theme [dark|light]", 'term-err');
      return;
    }
    try { localStorage.setItem('fuadfolio-theme', theme); } catch (e) {}
    document.documentElement.setAttribute('data-theme', theme);
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', theme === 'dark' ? '#0b1220' : '#eaf2ff');
    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      btn.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
      btn.setAttribute('data-theme-current', theme);
    });
    print("Theme switched to " + theme + ".", 'term-ok');
  }

  var COMMANDS = {
    help: function () {
      print("Available commands:", 'term-ok');
      print("  help              — show this list");
      print("  whoami            — one-line bio");
      print("  about             — longer intro");
      print("  skills            — tech stack");
      print("  projects          — link to my GitHub projects");
      print("  experience        — work experience summary");
      print("  certifications    — certifications summary");
      print("  education         — education journey");
      print("  contact           — email, phone, location");
      print("  social            — GitHub, LinkedIn, Facebook");
      print("  cv                — download my CV (PDF)");
      print("  ls                — list site sections");
      print("  game              — jump to the Snake mini-game");
      print("  theme [dark|light]— switch site theme");
      print("  date              — current date &amp; time");
      print("  echo [text]       — echo back your text");
      print("  joke              — a random programming joke");
      print("  clear             — clear the terminal");
    },

    whoami: function () {
      print(site.name + " — " + site.title, 'term-ok');
      print("Based in " + site.location + ". CSE student at East West University, Dhaka.");
    },

    about: function () {
      print(site.name, 'term-ok');
      print("A data scientist &amp; ML engineer who loves turning messy data into clean,");
      print("useful products. Currently studying CSE at East West University and");
      print("building AI-powered side projects in my spare time.");
      print("Focus areas: Data Science, Machine Learning, Deep Learning, Django web apps.");
    },

    skills: function () {
      print("Languages:   Python, SQL, JavaScript, HTML/CSS", 'term-ok');
      print("Data/ML:     Pandas, NumPy, scikit-learn, TensorFlow, PyTorch, Matplotlib");
      print("Backend:     Django, FastAPI, REST APIs, PostgreSQL, SQLite");
      print("Tools:       Git &amp; GitHub, Jupyter, VS Code, Linux, Gunicorn");
    },

    projects: function () {
      print("My public GitHub repos are on the Projects page:", 'term-ok');
      print('  → <a href="/portfolio/" class="term-link">/portfolio/</a>');
      if (site.github) print('  → GitHub: <a href="' + site.github + '" target="_blank" rel="noopener" class="term-link">' + escapeHtml(site.github) + '</a>');
    },

    experience: function () {
      print("Work experience lives on the Others (professional) page:", 'term-ok');
      print('  → <a href="/others/" class="term-link">/others/</a>');
    },

    certifications: function () {
      print("Certifications &amp; achievements are on the Others page:", 'term-ok');
      print('  → <a href="/others/" class="term-link">/others/</a>');
    },

    education: function () {
      print("Education journey:", 'term-ok');
      print("  School    — Anjuman Adarsha Govt. High School, Netrakona (SSC)");
      print("  College   — Agricultural University College, Mymensingh (HSC)");
      print("  University— East West University, Dhaka (BSc in CSE, currently studying)");
      print('  → details on the <a href="/about/" class="term-link">About</a> page');
    },

    contact: function () {
      print("Contact:", 'term-ok');
      if (site.email) print("  Email:    " + escapeHtml(site.email));
      print("  Phone:    +880 1338-136424");
      print("  Location: " + escapeHtml(site.location));
      print("  Permanent: Ghatail, Tangail");
    },

    social: function () {
      print("Find me online:", 'term-ok');
      if (site.github)   print('  GitHub:   <a href="' + site.github + '" target="_blank" rel="noopener" class="term-link">' + escapeHtml(site.github) + '</a>');
      if (site.linkedin) print('  LinkedIn: <a href="' + site.linkedin + '" target="_blank" rel="noopener" class="term-link">' + escapeHtml(site.linkedin) + '</a>');
      if (site.facebook) print('  Facebook: <a href="' + site.facebook + '" target="_blank" rel="noopener" class="term-link">' + escapeHtml(site.facebook) + '</a>');
    },

    cv: function () {
      print("Download my CV (auto-generated PDF):", 'term-ok');
      print('  → <a href="/cv/" class="term-link">/cv/</a>');
    },

    ls: function () {
      print("about/   portfolio/   others/   myworld/   contact/   admin/   cv.pdf", 'term-ok');
    },

    game: function () {
      print("Scrolling down to the Snake game…", 'term-ok');
      scrollToGame();
    },

    theme: function (args) {
      setTheme((args[0] || '').toLowerCase());
    },

    date: function () {
      print(new Date().toString(), 'term-ok');
    },

    echo: function (args) {
      print(args.join(' ') || '');
    },

    joke: function () {
      print(JOKES[Math.floor(Math.random() * JOKES.length)], 'term-ok');
    },

    clear: function () {
      clearOutput();
    },

    sudo: function () {
      print("Nice try. You are not in the sudoers file. This incident will be reported.", 'term-err');
    },

    exit: function () {
      print("There is no escape. Try 'clear' instead.", 'term-dim');
    },
  };

  function run(raw) {
    var line = (raw || '').trim();
    print('<span class="term-prompt-inline">fuad@portfolio:~$</span> ' + escapeHtml(line), 'term-cmd');

    if (!line) return;

    var parts = line.split(/\s+/);
    var cmd = parts[0].toLowerCase();
    var args = parts.slice(1);

    if (COMMANDS[cmd]) {
      try {
        COMMANDS[cmd](args);
      } catch (e) {
        print("error: " + (e.message || e), 'term-err');
      }
    } else {
      print("command not found: " + escapeHtml(cmd) + " — type 'help' for the list.", 'term-err');
    }
  }

  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      var val = input.value;
      if (val.trim()) {
        history.push(val);
        if (history.length > 50) history.shift();
      }
      histIdx = -1;
      run(val);
      input.value = '';
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (!history.length) return;
      if (histIdx === -1) histIdx = history.length - 1;
      else if (histIdx > 0) histIdx--;
      input.value = history[histIdx] || '';
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (histIdx === -1) return;
      if (histIdx < history.length - 1) {
        histIdx++;
        input.value = history[histIdx] || '';
      } else {
        histIdx = -1;
        input.value = '';
      }
    } else if (e.key === 'l' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      clearOutput();
    }
  });

  // Tap anywhere in the terminal body to focus the input.
  body.addEventListener('click', function () {
    input.focus();
  });

  // Auto-focus on desktop only (avoid the mobile keyboard popping up
  // unexpectedly on page load).
  if (window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          input.focus();
          obs.disconnect();
        }
      });
    }, { threshold: 0.5 });
    obs.observe(body);
  }
})();
