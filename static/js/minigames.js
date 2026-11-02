/* minigames.js — three tiny games: Reaction Time, Memory Match, Tic-Tac-Toe.
 *
 * All self-contained, no dependencies. Each game initialises only if its
 * DOM element is present, so the script is safe on pages that don't have
 * the games.
 */
(function () {

  /* ============================================================
     1) REACTION TIME
     ============================================================ */
  (function reactionGame() {
    var pad = document.getElementById('reactionPad');
    var bestEl = document.getElementById('reactionBest');
    if (!pad || !bestEl) return;

    var state = 'idle';  // idle | wait | go | early | result
    var startTime = 0;
    var timeoutId = null;
    var best = null;
    try { best = parseInt(localStorage.getItem('reactionBest') || '', 10) || null; } catch (e) {}
    if (best) bestEl.textContent = best + ' ms';

    function set(stateName, text) {
      state = stateName;
      pad.className = 'reaction-pad ' + stateName;
      pad.textContent = text;
    }

    function startWait() {
      set('wait', 'Wait for green…');
      var delay = 1200 + Math.floor(Math.random() * 2800);
      timeoutId = setTimeout(function () {
        set('go', 'CLICK NOW!');
        startTime = Date.now();
      }, delay);
    }

    pad.addEventListener('click', function () {
      if (state === 'idle' || state === 'result' || state === 'early') {
        startWait();
      } else if (state === 'wait') {
        // Clicked too early.
        clearTimeout(timeoutId);
        set('early', 'Too early! Click to try again.');
      } else if (state === 'go') {
        var ms = Date.now() - startTime;
        set('result', ms + ' ms — click to retry');
        if (!best || ms < best) {
          best = ms;
          bestEl.textContent = best + ' ms';
          try { localStorage.setItem('reactionBest', String(best)); } catch (e) {}
        }
      }
    });
  })();


  /* ============================================================
     2) MEMORY MATCH (4x2 grid = 4 pairs)
     ============================================================ */
  (function memoryGame() {
    var grid = document.getElementById('memoryGrid');
    var movesEl = document.getElementById('memoryMoves');
    var resetBtn = document.getElementById('memoryReset');
    if (!grid || !movesEl) return;

    var EMOJIS = ['🐍', '🤖', '⚡', '🚀'];
    var first = null;     // {cell, emoji}
    var locked = false;
    var matched = 0;
    var moves = 0;

    function shuffle(arr) {
      for (var i = arr.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var t = arr[i]; arr[i] = arr[j]; arr[j] = t;
      }
      return arr;
    }

    function build() {
      grid.innerHTML = '';
      first = null;
      locked = false;
      matched = 0;
      moves = 0;
      movesEl.textContent = '0';

      var cards = shuffle(EMOJIS.concat(EMOJIS));
      cards.forEach(function (emoji) {
        var cell = document.createElement('div');
        cell.className = 'memory-cell';
        cell.dataset.emoji = emoji;
        cell.textContent = '';
        cell.addEventListener('click', function () { flip(cell); });
        grid.appendChild(cell);
      });
    }

    function flip(cell) {
      if (locked) return;
      if (cell.classList.contains('flipped') || cell.classList.contains('matched')) return;

      cell.classList.add('flipped');
      cell.textContent = cell.dataset.emoji;

      if (!first) {
        first = { cell: cell, emoji: cell.dataset.emoji };
        return;
      }

      // Second flip
      moves++;
      movesEl.textContent = moves;

      if (first.emoji === cell.dataset.emoji) {
        // Match!
        first.cell.classList.add('matched');
        cell.classList.add('matched');
        first = null;
        matched++;
        if (matched === EMOJIS.length) {
          // All matched — celebrate, then auto-reset after a pause.
          setTimeout(function () {
            Array.prototype.forEach.call(grid.children, function (c) {
              c.style.transform = 'scale(1.1)';
            });
            setTimeout(function () {
              Array.prototype.forEach.call(grid.children, function (c) {
                c.style.transform = '';
              });
              build();
            }, 900);
          }, 400);
        }
      } else {
        // No match — flip back after a short delay.
        locked = true;
        var a = first;
        first = null;
        setTimeout(function () {
          a.cell.classList.remove('flipped');
          a.cell.textContent = '';
          cell.classList.remove('flipped');
          cell.textContent = '';
          locked = false;
        }, 700);
      }
    }

    if (resetBtn) resetBtn.addEventListener('click', build);
    build();
  })();


  /* ============================================================
     3) TIC-TAC-TOE (you = X, AI = O, simple heuristic)
     ============================================================ */
  (function ticTacToe() {
    var grid = document.getElementById('tttGrid');
    var statusEl = document.getElementById('tttStatus');
    var resetBtn = document.getElementById('tttReset');
    if (!grid || !statusEl) return;

    var HUMAN = 'X', AI = 'O';
    var board = [];   // 9 cells, '' / 'X' / 'O'
    var gameOver = false;

    var WIN_LINES = [
      [0, 1, 2], [3, 4, 5], [6, 7, 8],   // rows
      [0, 3, 6], [1, 4, 7], [2, 5, 8],   // cols
      [0, 4, 8], [2, 4, 6],              // diagonals
    ];

    function winner(b) {
      for (var i = 0; i < WIN_LINES.length; i++) {
        var L = WIN_LINES[i];
        var a = b[L[0]], x = b[L[1]], c = b[L[2]];
        if (a && a === x && a === c) return { who: a, line: L };
      }
      return null;
    }

    function isFull(b) { return b.every(function (c) { return c; }); }

    function build() {
      grid.innerHTML = '';
      board = ['', '', '', '', '', '', '', '', ''];
      gameOver = false;
      statusEl.textContent = 'Your turn';
      for (var i = 0; i < 9; i++) {
        var cell = document.createElement('div');
        cell.className = 'ttt-cell';
        cell.dataset.idx = i;
        cell.addEventListener('click', function () { humanMove(parseInt(this.dataset.idx, 10)); });
        grid.appendChild(cell);
      }
    }

    function renderCell(idx) {
      var cell = grid.children[idx];
      var mark = board[idx];
      cell.textContent = mark;
      cell.classList.remove('x', 'o');
      if (mark) cell.classList.add(mark.toLowerCase());
    }

    function highlightWin(line) {
      line.forEach(function (idx) {
        grid.children[idx].classList.add('win');
      });
    }

    function humanMove(idx) {
      if (gameOver || board[idx]) return;
      board[idx] = HUMAN;
      renderCell(idx);
      var w = winner(board);
      if (w) { endGame(w); return; }
      if (isFull(board)) { endGame(null); return; }
      statusEl.textContent = 'AI thinking…';
      setTimeout(aiMove, 350);
    }

    function aiMove() {
      if (gameOver) return;
      // Heuristic: 1) win if possible, 2) block human win, 3) take center,
      // 4) take a corner, 5) take any empty.
      var move = findWinningMove(AI) ||
                 findWinningMove(HUMAN) ||
                 (board[4] === '' ? 4 : null) ||
                 firstEmpty([0, 2, 6, 8]) ||
                 firstEmpty([1, 3, 5, 7]);
      if (move === null) return;
      board[move] = AI;
      renderCell(move);
      var w = winner(board);
      if (w) { endGame(w); return; }
      if (isFull(board)) { endGame(null); return; }
      statusEl.textContent = 'Your turn';
    }

    function findWinningMove(who) {
      for (var i = 0; i < 9; i++) {
        if (board[i]) continue;
        var copy = board.slice();
        copy[i] = who;
        if (winner(copy) && winner(copy).who === who) return i;
      }
      return null;
    }
    function firstEmpty(idxs) {
      for (var i = 0; i < idxs.length; i++) {
        if (!board[idxs[i]]) return idxs[i];
      }
      return null;
    }

    function endGame(w) {
      gameOver = true;
      if (w) {
        if (w.who === HUMAN) {
          statusEl.textContent = 'You win! 🎉';
        } else {
          statusEl.textContent = 'AI wins. Try again.';
        }
        highlightWin(w.line);
      } else {
        statusEl.textContent = "It's a draw.";
      }
    }

    if (resetBtn) resetBtn.addEventListener('click', build);
    build();
  })();

})();
