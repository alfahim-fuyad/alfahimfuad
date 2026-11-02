/* chatbot.js — floating chat widget for fuadFolio.
 *
 * Talks to /chatbot/chat/ (see chatbot/views.py).
 *
 * Conversation history is kept in memory on the client only — the
 * backend is stateless and the page reload resets the conversation.
 *
 * Failover is handled SERVER-SIDE: the backend tries Groq first and
 * OpenRouter as fallback. When a provider's rate limit is exhausted,
 * the next one is used automatically.
 */

(function () {
  var ENDPOINT = '/chatbot/chat/';
  var WELCOME =
    "Hi! I'm fuadBot — ask me anything about Fuad's projects, experience, " +
    "certifications, skills, or how to get in touch.";

  var bubble = document.getElementById('chatbotBubble');
  var panel = document.getElementById('chatbotPanel');
  if (!bubble || !panel) return;

  var openBtn = bubble;
  var closeBtn = document.getElementById('chatbotClose');
  var clearBtn = document.getElementById('chatbotClear');
  var sendBtn = document.getElementById('chatbotSend');
  var input = document.getElementById('chatbotInput');
  var log = document.getElementById('chatbotLog');
  var statusPill = document.getElementById('chatbotProvider');
  var form = document.getElementById('chatbotForm');

  var history = [];
  var sending = false;

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function addMessage(role, text) {
    var div = document.createElement('div');
    div.className = 'cb-msg cb-msg-' + role;
    div.innerHTML = '<div class="cb-bubble">' + escapeHtml(text) + '</div>';
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
    return div;
  }

  function addTyping() {
    var div = document.createElement('div');
    div.className = 'cb-msg cb-msg-assistant cb-typing';
    div.innerHTML = '<div class="cb-bubble"><span></span><span></span><span></span></div>';
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
    return div;
  }

  function setStatus(provider) {
    if (!statusPill) return;
    var label = '';
    if (provider === 'groq') label = 'Groq';
    else if (provider === 'openrouter') label = 'OpenRouter';
    else if (provider === 'fallback') label = 'Offline';
    else if (provider === 'none-configured') label = 'No key';
    statusPill.textContent = label;
    statusPill.setAttribute('data-provider', provider || '');
    statusPill.style.display = label ? '' : 'none';
  }

  function openPanel() {
    panel.classList.add('open');
    bubble.classList.add('hidden');
    setTimeout(function () { input && input.focus(); }, 60);
  }

  function closePanel() {
    panel.classList.remove('open');
    bubble.classList.remove('hidden');
  }

  openBtn.addEventListener('click', openPanel);
  closeBtn.addEventListener('click', closePanel);

  // "Clear all" button — wipes the conversation log + history, then
  // re-seeds the welcome message so the bot greets the visitor again.
  if (clearBtn) {
    clearBtn.addEventListener('click', function () {
      log.innerHTML = '';
      history = [];
      addMessage('assistant', WELCOME);
      history.push({ role: 'assistant', content: WELCOME });
      setStatus('');
      if (input) input.focus();
    });
  }

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && panel.classList.contains('open')) {
      closePanel();
    }
  });

  function setSending(v) {
    sending = v;
    sendBtn.disabled = v;
    input.disabled = v;
    if (!v && input) input.focus();
  }

  function send(text) {
    if (sending || !text) return;
    addMessage('user', text);
    history.push({ role: 'user', content: text });
    input.value = '';

    var typingEl = addTyping();
    setSending(true);

    fetch(ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: JSON.stringify({
        message: text,
        history: history.slice(-12),
      }),
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (typingEl && typingEl.parentNode) typingEl.parentNode.removeChild(typingEl);
        var reply = data.reply || 'Sorry, no reply.';
        addMessage('assistant', reply);
        history.push({ role: 'assistant', content: reply });
        setStatus(data.provider);
      })
      .catch(function () {
        if (typingEl && typingEl.parentNode) typingEl.parentNode.removeChild(typingEl);
        addMessage('assistant',
          'Network hiccup — please try again in a moment.');
        setStatus('fallback');
      })
      .finally(function () { setSending(false); });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var text = (input.value || '').trim();
    if (text) send(text);
  });

  // Pressing Enter without Shift sends the message.
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      var text = (input.value || '').trim();
      if (text) send(text);
    }
  });

  // Seed the conversation with a welcome message from the bot.
  addMessage('assistant', WELCOME);
  history.push({ role: 'assistant', content: WELCOME });
  setStatus('');
})();
