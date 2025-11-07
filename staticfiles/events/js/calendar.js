const calendar = new FullCalendar.Calendar(calendarEl, {
  initialView: 'dayGridMonth',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,timeGridDay'
  },
  editable: true,
  selectable: true,

  // 👇 Multiple event sources: your API + Indian holidays feed
  eventSources: [
    {
      url: '/api/events/',
      method: 'GET',
      failure: () => alert('Error loading your events!')
    },
    {
      url: 'https://calendar.google.com/calendar/ical/en.indian%23holiday%40group.v.calendar.google.com/public/basic.ics',
      format: 'ics',
      color: '#d32f2f',
      textColor: 'white'
    }
  ],

  select: async function (info) {
    const title = prompt('Enter Event Title:');
    if (title) {
      try {
        const response = await axios.post('/api/events/', {
          title,
          start: info.startStr,
          end: info.endStr,
          all_day: info.allDay
        });
        calendar.addEvent({
          id: response.data.id,
          title,
          start: info.start,
          end: info.end,
          allDay: info.allDay
        });
      } catch (e) {
        alert('Failed to save event.');
      }
    }
    calendar.unselect();
  },

  eventClick: async function (info) {
    if (confirm(`Delete event "${info.event.title}"?`)) {
      try {
        await axios.delete(`/api/events/${info.event.id}/`);
        info.event.remove();
      } catch {
        alert('Failed to delete event.');
      }
    }
  }
});
