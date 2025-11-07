const API_BASE = '/api/events/';
const FALLBACK_COORDS = { lat: 28.644800, lon: 77.216721 };
const WEATHER_API = (lat, lon) =>
  `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&daily=temperature_2m_max,temperature_2m_min&forecast_days=3&timezone=Asia%2FKolkata`;

document.addEventListener('DOMContentLoaded', async () => {
  initCalendar();
  await loadUpcomingEvents();
  await loadTodayTimeline();
  await loadWeather();
  loadSuggestions();
  initQuickAdd();
  initFocusTimer();
  setInterval(() => {
    loadUpcomingEvents();
    loadTodayTimeline();
  }, 15000);
});

/* ---------- CALENDAR SETUP ---------- */
function initCalendar() {
  const calendarEl = document.getElementById('calendar');
  const miniCalendarEl = document.getElementById('miniCalendar');
  if (!calendarEl) return;

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    editable: true,
    selectable: true,
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay'
    },
    events: fetchEvents,
    eventClick: handleEventClick,
    select: handleDateSelect,
    eventDrop: handleEventUpdate,
    eventResize: handleEventUpdate
  });

  const mini = new FullCalendar.Calendar(miniCalendarEl, {
    initialView: 'dayGridMonth',
    dateClick: (info) => calendar.gotoDate(info.date)
  });

  calendar.render();
  mini.render();
}

function fetchEvents(info, success, failure) {
  axios.get(API_BASE)
    .then(res => {
      const events = res.data.map(e => ({
        id: e.id,
        title: e.title,
        start: e.start,
        end: e.end,
        allDay: e.allDay,
        backgroundColor: e.color || '#4285f4'
      }));
      success(events);
    })
    .catch(err => failure(err));
}

function handleDateSelect(info) {
  const title = prompt("Enter event title:");
  if (title) {
    const eventData = {
      title: title,
      start: info.startStr,
      end: info.endStr,
      allDay: info.allDay
    };
    axios.post(API_BASE, eventData).then(() => {
      loadUpcomingEvents();
      loadTodayTimeline();
    });
  }
}

function handleEventClick(info) {
  if (confirm(`Delete event "${info.event.title}"?`)) {
    axios.delete(`${API_BASE}${info.event.id}/`).then(() => {
      info.event.remove();
      loadUpcomingEvents();
      loadTodayTimeline();
    });
  }
}

function handleEventUpdate(info) {
  const ev = info.event;
  axios.put(`${API_BASE}${ev.id}/`, {
    start: ev.start.toISOString(),
    end: ev.end ? ev.end.toISOString() : ev.start.toISOString()
  }).then(() => {
    loadUpcomingEvents();
    loadTodayTimeline();
  });
}

/* ---------- DASHBOARD FUNCTIONS ---------- */
async function loadUpcomingEvents() {
  const list = document.getElementById('upcomingList');
  try {
    const res = await axios.get(API_BASE);
    const events = res.data.sort((a,b)=>new Date(a.start)-new Date(b.start));
    const upcoming = events.filter(e=>new Date(e.start)>new Date()).slice(0,5);
    list.innerHTML = upcoming.length 
      ? upcoming.map(e=>`<li>📅 ${e.title} — ${new Date(e.start).toLocaleString()}</li>`).join('')
      : '<li>No upcoming events</li>';
  } catch {
    list.innerHTML = '<li>⚠️ Failed to load events</li>';
  }
}

async function loadTodayTimeline() {
  const list = document.getElementById('todayList');
  const today = new Date().toISOString().split('T')[0];
  try {
    const res = await axios.get(API_BASE);
    const events = res.data.filter(e => e.start.startsWith(today));
    list.innerHTML = events.length
      ? events.map(e => `<li>${new Date(e.start).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} — ${e.title}</li>`).join('')
      : '<li>No events today</li>';
  } catch {
    list.innerHTML = '<li>⚠️ Failed to load today’s events</li>';
  }
}

async function loadWeather() {
  const box = document.getElementById('weatherBox');
  try {
    const res = await fetch(WEATHER_API(FALLBACK_COORDS.lat, FALLBACK_COORDS.lon));
    const j = await res.json();
    box.innerHTML = j.daily.time.map((d,i)=>
      `<div><strong>${d}</strong>: ${j.daily.temperature_2m_max[i]}°C / ${j.daily.temperature_2m_min[i]}°C</div>`
    ).join('');
  } catch {
    box.innerHTML = '⚠️ Weather data unavailable';
  }
}

function loadSuggestions() {
  const list = document.getElementById('suggestionsList');
  const hour = new Date().getHours();
  const ideas = [
    "Plan your next week 🌱",
    "Take a 10-min break ☕",
    "You haven’t added an event for tomorrow 📅",
    "Try a focus session 🔥",
  ];
  const msg = hour < 12 ? "Good morning! Ready to be productive?" : 
             hour < 18 ? "Keep going strong today 💪" :
             "Wrap up your day mindfully 🌙";
  list.innerHTML = `<li>${msg}</li>` + ideas.map(i=>`<li>${i}</li>`).join('');
}

/* ---------- Quick Add ---------- */
function initQuickAdd() {
  const input = document.getElementById('quickAddInput');
  const btn = document.getElementById('quickAddBtn');
  btn.addEventListener('click', async () => {
    const text = input.value.trim();
    if (!text) return alert('Enter an event description!');
    const start = new Date();
    const payload = { title: text, start: start.toISOString(), end: start.toISOString(), allDay: true };
    try {
      await axios.post(API_BASE, payload);
      input.value = '';
      addNotification(`✅ Event added: ${text}`);
      loadUpcomingEvents();
      loadTodayTimeline();
    } catch {
      addNotification('❌ Failed to add event.');
    }
  });
}

/* ---------- Notifications ---------- */
function addNotification(msg) {
  const list = document.getElementById('notificationsList');
  const item = document.createElement('li');
  item.textContent = `${new Date().toLocaleTimeString()} — ${msg}`;
  list.prepend(item);
}

/* ---------- Focus Timer ---------- */
function initFocusTimer() {
  let seconds = 25 * 60;
  let timer;
  const display = document.getElementById('timerDisplay');
  const startBtn = document.getElementById('startTimer');
  const resetBtn = document.getElementById('resetTimer');

  function updateDisplay() {
    const m = String(Math.floor(seconds / 60)).padStart(2, '0');
    const s = String(seconds % 60).padStart(2, '0');
    display.textContent = `${m}:${s}`;
  }

  startBtn.addEventListener('click', () => {
    if (timer) return;
    timer = setInterval(() => {
      seconds--;
      updateDisplay();
      if (seconds <= 0) {
        clearInterval(timer);
        timer = null;
        addNotification('🎯 Focus session complete!');
      }
    }, 1000);
  });

  resetBtn.addEventListener('click', () => {
    clearInterval(timer);
    timer = null;
    seconds = 25 * 60;
    updateDisplay();
  });

  updateDisplay();
}
