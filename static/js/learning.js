/* learning.js — rotates the first "Currently Learning" card through a list
 * of topics so the home page feels alive without being noisy.
 *
 * Only the first card rotates (the one with id="learningTitle"); the
 * other two stay static. This keeps the section dynamic but calm.
 */
(function () {
  var titleEl = document.getElementById('learningTitle');
  var descEl = document.getElementById('learningDesc');
  if (!titleEl || !descEl) return;

  var TOPICS = [
    {
      icon: '🧠',
      title: 'LangChain & RAG',
      desc: 'Building retrieval-augmented generation pipelines with LangChain, vector stores, and OpenAI embeddings.',
    },
    {
      icon: '🤖',
      title: 'Local LLMs',
      desc: 'Running quantized Llama 3 and Phi-3 models on consumer hardware with llama.cpp and Ollama.',
    },
    {
      icon: '⚡',
      title: 'FastAPI + WebSockets',
      desc: 'Real-time dashboards with FastAPI, WebSockets, and async Postgres for streaming analytics.',
    },
    {
      icon: '🐳',
      title: 'Docker & CI/CD',
      desc: 'Containerising Django apps and shipping them through GitHub Actions to Render and Railway.',
    },
    {
      icon: '🔬',
      title: 'Experiment Tracking',
      desc: 'Logging ML experiments with MLflow and Weights & Biases for reproducible model training.',
    },
    {
      icon: '🎨',
      title: 'Design Systems',
      desc: 'Crafting reusable CSS variable systems and component libraries for consistent, fast UIs.',
    },
  ];

  var idx = 0;
  var card = titleEl.closest('.learning-card');
  var iconEl = card ? card.querySelector('.learning-icon') : null;

  function render(topic) {
    // Fade out, swap, fade in
    if (card) card.style.opacity = '0.4';
    setTimeout(function () {
      titleEl.textContent = topic.title;
      descEl.textContent = topic.desc;
      if (iconEl) iconEl.textContent = topic.icon;
      if (card) card.style.opacity = '1';
    }, 250);
  }

  // Start with the first topic, then rotate every 5 seconds.
  // Skip the initial render (the template already shows the first topic).
  idx = 1;

  // Pause rotation when the tab is not visible.
  var timerId = null;
  function startTimer() {
    if (timerId) return;
    timerId = setInterval(function () {
      render(TOPICS[idx]);
      idx = (idx + 1) % TOPICS.length;
    }, 5000);
  }
  function stopTimer() {
    clearInterval(timerId);
    timerId = null;
  }

  // Respect prefers-reduced-motion.
  var reduce = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (!reduce) {
    startTimer();
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) stopTimer();
      else startTimer();
    });
  }
})();
