/* snake.js — a tiny, self-contained Snake game in pure JS.
 *
 * Desktop controls: arrow keys OR WASD. Mobile: swipe inside the board.
 * Score + best (localStorage). Start / pause / restart buttons.
 */
(function () {
  var canvas = document.getElementById('snakeCanvas');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');

  var GRID = 15;                 // 15x15 cells
  var CELL = canvas.width / GRID; // 20px per cell at 300x300

  var scoreEl = document.getElementById('snakeScore');
  var bestEl = document.getElementById('snakeBest');
  var startBtn = document.getElementById('snakeStart');
  var pauseBtn = document.getElementById('snakePause');
  var overlay = document.getElementById('snakeOverlay');
  var overlayTitle = document.getElementById('snakeOverlayTitle');
  var overlayText = document.getElementById('snakeOverlayText');
  var restartBtn = document.getElementById('snakeRestart');

  var snake, dir, nextDir, food, score, best, running, paused, tickId;

  function loadBest() {
    try {
      best = parseInt(localStorage.getItem('snakeBest') || '0', 10) || 0;
    } catch (e) { best = 0; }
    bestEl.textContent = best;
  }
  function saveBest() {
    try { localStorage.setItem('snakeBest', String(best)); } catch (e) {}
    bestEl.textContent = best;
  }

  function reset() {
    snake = [{ x: 7, y: 7 }, { x: 6, y: 7 }, { x: 5, y: 7 }];
    dir = { x: 1, y: 0 };
    nextDir = { x: 1, y: 0 };
    score = 0;
    scoreEl.textContent = '0';
    placeFood();
    draw();
  }

  function placeFood() {
    while (true) {
      var fx = Math.floor(Math.random() * GRID);
      var fy = Math.floor(Math.random() * GRID);
      if (!snake.some(function (s) { return s.x === fx && s.y === fy; })) {
        food = { x: fx, y: fy };
        return;
      }
    }
  }

  function isDark() {
    return document.documentElement.getAttribute('data-theme') === 'dark';
  }

  function draw() {
    var dark = isDark();
    // Background
    ctx.fillStyle = dark ? '#0a1020' : '#0f172a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Grid lines (subtle)
    ctx.strokeStyle = dark ? 'rgba(96,165,250,0.06)' : 'rgba(255,255,255,0.04)';
    ctx.lineWidth = 1;
    for (var i = 1; i < GRID; i++) {
      ctx.beginPath();
      ctx.moveTo(i * CELL, 0);
      ctx.lineTo(i * CELL, canvas.height);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(0, i * CELL);
      ctx.lineTo(canvas.width, i * CELL);
      ctx.stroke();
    }

    // Food (pulsing apple)
    var pulse = 0.7 + Math.sin(Date.now() / 200) * 0.3;
    ctx.fillStyle = '#ef4444';
    ctx.shadowColor = '#ef4444';
    ctx.shadowBlur = 10 * pulse;
    roundRect(food.x * CELL + 2, food.y * CELL + 2, CELL - 4, CELL - 4, 4);
    ctx.fill();
    ctx.shadowBlur = 0;

    // Snake
    snake.forEach(function (s, i) {
      var t = i / Math.max(snake.length - 1, 1);
      var r = Math.round(96 + (168 - 96) * t);
      var g = Math.round(165 + (85 - 165) * t);
      var b = Math.round(250 + (247 - 250) * t);
      ctx.fillStyle = 'rgb(' + r + ',' + g + ',' + b + ')';
      roundRect(s.x * CELL + 1, s.y * CELL + 1, CELL - 2, CELL - 2, 4);
      ctx.fill();
      // Eyes on the head
      if (i === 0) {
        ctx.fillStyle = dark ? '#0a1020' : '#fff';
        var ex = s.x * CELL + CELL / 2;
        var ey = s.y * CELL + CELL / 2;
        ctx.beginPath();
        ctx.arc(ex + dir.x * 3 - dir.y * 3, ey + dir.y * 3 - dir.x * 3, 2, 0, 2 * Math.PI);
        ctx.arc(ex + dir.x * 3 + dir.y * 3, ey + dir.y * 3 + dir.x * 3, 2, 0, 2 * Math.PI);
        ctx.fill();
      }
    });
  }

  function roundRect(x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  function tick() {
    if (!running || paused) return;
    dir = nextDir;
    var head = { x: snake[0].x + dir.x, y: snake[0].y + dir.y };

    // Wall collision
    if (head.x < 0 || head.x >= GRID || head.y < 0 || head.y >= GRID) {
      gameOver();
      return;
    }
    // Self collision
    if (snake.some(function (s) { return s.x === head.x && s.y === head.y; })) {
      gameOver();
      return;
    }

    snake.unshift(head);

    if (head.x === food.x && head.y === food.y) {
      score++;
      scoreEl.textContent = score;
      if (score > best) {
        best = score;
        saveBest();
      }
      placeFood();
    } else {
      snake.pop();
    }
    draw();
  }

  function start() {
    if (running && !paused) return;
    if (!running) reset();
    running = true;
    paused = false;
    overlay.style.display = 'none';
    startBtn.textContent = 'Restart';
    pauseBtn.disabled = false;
    pauseBtn.textContent = 'Pause';
    clearInterval(tickId);
    tickId = setInterval(tick, 130);
  }

  function pause() {
    if (!running) return;
    paused = !paused;
    pauseBtn.textContent = paused ? 'Resume' : 'Pause';
    if (paused) {
      overlayTitle.textContent = 'Paused';
      overlayText.textContent = 'Press Resume to continue.';
      overlay.style.display = 'flex';
    } else {
      overlay.style.display = 'none';
    }
  }

  function gameOver() {
    clearInterval(tickId);
    running = false;
    paused = false;
    pauseBtn.disabled = true;
    startBtn.textContent = 'Start';
    overlayTitle.textContent = 'Game Over';
    overlayText.innerHTML = 'Score: <strong>' + score + '</strong>' +
      (score >= best && score > 0 ? ' — new best! 🎉' : '') +
      '<br>Press Start to play again.';
    overlay.style.display = 'flex';
  }

  function setDir(nx, ny) {
    // Prevent 180° reversal
    if (nx === -dir.x && ny === -dir.y) return;
    nextDir = { x: nx, y: ny };
  }

  // Keyboard
  document.addEventListener('keydown', function (e) {
    // Only handle when the canvas (or the game section) is in view, so we
    // don't hijack arrow keys while the visitor is scrolling.
    var rect = canvas.getBoundingClientRect();
    var inView = rect.top < window.innerHeight && rect.bottom > 0;
    if (!inView) return;
    // Also skip if the terminal input is focused.
    if (document.activeElement && document.activeElement.id === 'termInput') return;

    var k = e.key.toLowerCase();
    if (k === 'arrowup' || k === 'w')    { e.preventDefault(); setDir(0, -1); if (!running && !paused) start(); }
    else if (k === 'arrowdown' || k === 's')  { e.preventDefault(); setDir(0, 1);  if (!running && !paused) start(); }
    else if (k === 'arrowleft' || k === 'a')  { e.preventDefault(); setDir(-1, 0); if (!running && !paused) start(); }
    else if (k === 'arrowright' || k === 'd') { e.preventDefault(); setDir(1, 0);  if (!running && !paused) start(); }
    else if (k === ' ' || k === 'p') {
      e.preventDefault();
      if (running) pause();
      else start();
    }
  });

  // Touch / swipe
  var touchStart = null;
  canvas.addEventListener('touchstart', function (e) {
    var t = e.touches[0];
    touchStart = { x: t.clientX, y: t.clientY };
  }, { passive: true });

  canvas.addEventListener('touchend', function (e) {
    if (!touchStart) return;
    var t = e.changedTouches[0];
    var dx = t.clientX - touchStart.x;
    var dy = t.clientY - touchStart.y;
    if (Math.abs(dx) < 20 && Math.abs(dy) < 20) {
      // Tap → start if not running
      if (!running) start();
      touchStart = null;
      return;
    }
    if (Math.abs(dx) > Math.abs(dy)) {
      setDir(dx > 0 ? 1 : -1, 0);
    } else {
      setDir(0, dy > 0 ? 1 : -1);
    }
    if (!running) start();
    touchStart = null;
  }, { passive: true });

  startBtn.addEventListener('click', start);
  pauseBtn.addEventListener('click', pause);
  restartBtn.addEventListener('click', start);

  // Re-draw on theme change so the canvas bg follows the theme.
  var themeObs = new MutationObserver(function () { if (!running) draw(); });
  themeObs.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

  loadBest();
  reset();
})();
