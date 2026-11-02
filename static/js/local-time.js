/* local-time.js — shows Fuad's local time (Dhaka, Asia/Dhaka) and updates
 * every second. Also rotates the "current status" text based on the hour
 * so it feels alive.
 */
(function () {
  var timeEl = document.getElementById('localTime');
  var dateEl = document.getElementById('localDate');
  var statusEl = document.getElementById('statusText');
  if (!timeEl) return;

  // Asia/Dhaka is UTC+6. We use Intl to format in the visitor's browser
  // without needing a timezone library.
  var TZ = 'Asia/Dhaka';

  function pad(n) { return n < 10 ? '0' + n : '' + n; }

  function update() {
    try {
      var now = new Date();
      // Format time as HH:MM:SS in Dhaka timezone.
      var timeParts = new Intl.DateTimeFormat('en-GB', {
        timeZone: TZ,
        hour: '2-digit', minute: '2-digit', second: '2-digit',
        hour12: false,
      }).formatToParts(now);
      var hh = '', mm = '', ss = '';
      timeParts.forEach(function (p) {
        if (p.type === 'hour') hh = p.value;
        else if (p.type === 'minute') mm = p.value;
        else if (p.type === 'second') ss = p.value;
      });
      // Intl can return '24' for midnight in some browsers — normalise.
      if (hh === '24') hh = '00';
      timeEl.textContent = hh + ':' + mm + ':' + ss;

      // Format date as "Monday, 2 November 2026"
      var dateStr = new Intl.DateTimeFormat('en-GB', {
        timeZone: TZ,
        weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
      }).format(now);
      if (dateEl) dateEl.textContent = dateStr;

      // Rotate status based on the hour (Dhaka local time).
      if (statusEl) {
        var hour = parseInt(hh, 10);
        var status, sub;
        if (hour >= 9 && hour < 18) {
          status = 'Available for collaboration';
          sub = 'Online — open to ML & AI project opportunities';
        } else if (hour >= 18 && hour < 23) {
          status = 'Building something';
          sub = 'Evening coding session in progress';
        } else if (hour >= 6 && hour < 9) {
          status = 'Starting the day';
          sub = 'Morning coffee & planning';
        } else {
          status = 'Away / sleeping';
          sub = 'Will respond in the morning';
        }
        statusEl.textContent = status;
        var subEl = statusEl.parentElement.querySelector('.status-sub-text');
        if (subEl) subEl.textContent = sub;
      }
    } catch (e) {
      // Intl not supported — show UTC fallback.
      timeEl.textContent = new Date().toUTCString().slice(17, 25);
      if (dateEl) dateEl.textContent = new Date().toUTCString().slice(0, 16);
    }
  }

  update();
  setInterval(update, 1000);
})();
