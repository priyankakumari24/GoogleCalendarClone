# Calendar Clone (Advanced)

A Google Calendar-like Django application with FullCalendar integration, a date sidebar and a "Smart Dashboard". This README documents features, libraries, architecture and design decisions, setup and run instructions, business logic and edge cases handled, notes on animations/interactions, and suggested future enhancements.

---

Contents
- Features & libraries
- Setup & run (detailed)
- Architecture and technology choices
- Business logic & edge cases handled
- Animations & interaction implementation notes
- Code snippets (quick references)
- Suggestions for future enhancements

---

Features & libraries

Features
- Full month / week / day calendar views powered by FullCalendar
- Sidebar with minicalendar and quick date navigation
- Create / edit / delete events with modal UI
- Drag & drop and resize events (persisted)
- Event categories / color labels
- Search/filter events client-side
- Mini "Smart Dashboard" showing upcoming events, today timeline, suggestions, quick-add, notifications and a focus timer
- Weather snippet for selected day (Open-Meteo)
- Toast notifications for user feedback
- Recurrence field (RRULE) support in event model (backend read/write expected)
- CSRF-safe AJAX via axios
- Seed data helper for local development

Main third-party libraries used
- Django (backend)
- Django REST Framework (API endpoints)
- FullCalendar (calendar UI, drag/drop, views)
- Axios (AJAX for REST calls)
- Bootstrap 5 (layout, modals, buttons, toasts)
- Open-Meteo (weather API)
- Optional: rrule or python-dateutil on backend to interpret RRULE strings (recommended)

Files of interest
- Templates:
  - events/templates/events/calendar.html (main calendar)
  - events/templates/events/calendar_dashboard.html (dashboard UI)
- Frontend scripts:
  - events/static/events/js/calendar_dashboard.js (dashboard + calendar behaviour)
- Seed helper:
  - events/seed_data.py
- Static vendor files under staticfiles/ (bundled third-party assets)

---

Setup & run instructions (detailed)

1. Python environment
   - Create virtual environment:
     - Unix/macOS: 
```bash
# filepath: c:\Users\rajku\calendar_clone\README.md
python -m venv .venv && source .venv/bin/activate
```
     - Windows:
```powershell
# filepath: c:\Users\rajku\calendar_clone\README.md
python -m venv .venv
.venv\Scripts\activate
```
   - Install dependencies:
```bash
# filepath: c:\Users\rajku\calendar_clone\README.md
pip install -r requirements.txt
# or at minimum:
pip install django djangorestframework python-dateutil
```

2. Database and migrations
```bash
# filepath: c:\Users\rajku\calendar_clone\README.md
python manage.py migrate
```

3. Create a superuser (optional)
```bash
# filepath: c:\Users\rajku\calendar_clone\README.md
python manage.py createsuperuser
```

4. Seed sample events (optional)
```bash
# filepath: c:\Users\rajku\calendar_clone\README.md
python manage.py shell -c "from events.seed_data import run; run()"
```

5. Run the development server:
```bash
# filepath: c:\Users\rajku\calendar_clone\README.md
python manage.py runserver
# Open http://127.0.0.1:8000/
```

6. Static files (production):
```bash
# filepath: c:\Users\rajku\calendar_clone\README.md
python manage.py collectstatic
```

7. Notes on local APIs
   - The frontend expects REST endpoints:
     - GET /api/events/  — list events (supports start/end params when used by FullCalendar)
     - POST /api/events/ — create event
     - PUT /api/events/<id>/ — update event
     - DELETE /api/events/<id>/ — delete event
   - Ensure the API returns event objects with fields: id, title, start (ISO), end (ISO), allDay (bool), color (optional), and extendedProps as needed.

---

Architecture and technology choices

Backend (Django + DRF)
- Rationale: Django provides a mature, batteries-included web framework; Django REST Framework makes building RESTful APIs straightforward and maintainable.
- Responsibilities:
  - Persist events and recurrence rules.
  - Validate input (times, RRULE format if supported, ownership/permissions).
  - Provide paginated or full lists for the calendar range (FullCalendar will request events for visible range).

Frontend (FullCalendar, Axios, Bootstrap)
- FullCalendar chosen for a robust, production-ready calendar UI with built-in drag/drop, resize, multiple views and event rendering.
- Axios for promise-based AJAX and easy CSRF header configuration.
- Bootstrap for consistent layout, modals and toast UI.

Why FullCalendar?
- Handles many calendar-related interactions (drag+drop, resizing, view switching), reducing frontend complexity.
- Extensible render hooks (eventDidMount) let us adapt event styles (e.g., holidays with flags).

Design notes
- The UI is split into a left sidebar (dates and controls), the calendar area, and a right "Smart Dashboard". This improves information density and quick actions.
- The frontend treats the server as the source-of-truth for event IDs to avoid mismatch on update/delete — newly created events are re-fetched from the backend to obtain their server-assigned IDs.

---

Business logic and edge cases (what's handled and guidance)

Event identity and optimistic UI
- When creating an event, the UI sends a POST and then refetches events rather than inserting a client-only event without an ID. This ensures the created event has a server-assigned ID (required for later updates/deletes).
- For a snappy UX you can optionally add the event client-side but must preserve server ID reconciliation on the response.

Timezones
- The UI converts datetimes between local input controls and ISO used by the backend. Use timezone-aware datetimes on the backend.
- Store datetimes in UTC on the server and convert for display on clients.

All-day events
- The calendar uses allDay flags. Ensure the backend preserves all_day and the client uses the appropriate ISO format (FullCalendar expects all-day events to be date-only in many cases).

Recurring events (RRULE)
- The UI exposes an RRULE text input. Handling recurrence fully requires backend support:
  - Store the RRULE in a field (recurrence_rule).
  - For display in ranges, server should expand recurring rules to instances within the requested time range (or use a library that supports recurrence expansion).
  - Edge cases: exceptions (excluded dates), overlapping recurrence instances, daylight saving transitions.
- Recommendation: use python-dateutil or rrule library on backend to expand recurrences for range queries; store original RRULE and any EXDATEs.

Overlapping events and conflicts
- Frontend allows overlapping display by default. Business rule options:
  - Soft conflict: warn user when they create an overlapping event (check server-side on create).
  - Hard conflict: prevent overlapping if resource or room is shared.
- Implement conflict detection in backend (compare new event times with existing events for the same resource/user).

Validation and input sanitation
- Validate start < end, required title, and correct RRULE format (if enforced).
- Prevent events with no ID from being used in updates/deletes.

Partial failures and network errors
- Show toast messages on errors.
- On drag/resize failures, revert the change client-side (FullCalendar provides revert support).
- Retry policies can be added for transient errors.

Permissions and multi-user
- Backend must enforce per-user access control; events list should only return events the current user is allowed to read.
- Consider recurring events shared across users and how exceptions are modeled.

Edge cases summary
- Events without server ID: avoid adding client-only events without reconciling with server.
- DST transitions: use UTC storage and careful local rendering.
- Recurrence exceptions: store EXDATE/RECURRENCE-ID handling.
- Bulk edits (move series vs single instance): requires recurrence-aware UI and backend logic.

---

Animations and interactions (how implemented)

- FullCalendar provides native drag-and-drop and resizing; these are enabled via editable: true and eventResizableFromStart settings.
- Modal interactions:
  - Bootstrap modal used for create/edit forms (backdrop: static to avoid accidental close).
  - Form submits are performed via axios and on success the modal hides and calendar refetches.
- Toasts:
  - Bootstrap toasts used for non-blocking notifications. They are created dynamically in DOM and removed once hidden.
- Hover / selection interactions:
  - CSS hover rules on #miniCalendar cells and FullCalendar day cells provide subtle hover effects (background color changes and border-radius).
  - The mini calendar uses reduced cell padding and font sizes for compactness.
- Smoothness / transitions:
  - CSS transitions applied to theme/background color changes and iframe/dashboard hover to make interaction feel responsive.
- Revert on failed server update:
  - When a drag/resize triggers a PUT to the server that fails, the frontend calls event.revert() to restore the previous position.

---

Suggestions for future enhancements

Short-term (low effort)
- Improve RRULE UX: provide a recurrence picker UI instead of raw RRULE text.
- Add server response handling that returns the created/updated event and update the client-side event with the returned id and fields.
- Add client-side form validation for start < end, required fields.
- Add timezone selection per-user.

Medium-term
- Implement proper recurrence expansion on server with EXDATEs and exceptions; support editing a single instance vs series.
- Add conflict detection with configurable policies (warn vs block).
- Add user accounts, sharing and calendar permissions.
- Implement real-time updates with WebSockets (channels) to reflect edits by other users instantly.

Long-term (advanced)
- Offline edits with service worker + local queue + sync (PWA).
- Full two-way Google Calendar / Microsoft Calendar sync.
- Advanced analytics on dashboard (busy times, time spent in categories).
- Natural-language event creation (e.g., "Lunch tomorrow 1pm") with a parser.

---

Troubleshooting & tips

- If events show up without IDs after creating them, ensure the create endpoint returns the created object with its id or the frontend refetches events after create.
- CSRF errors with axios: ensure axios default header `X-CSRFToken` is set to the Django csrftoken cookie (the code already includes a getCookie helper).
- If FullCalendar doesn't render, verify the container exists and scripts are loaded in order: FullCalendar, then your calendar initialization script.
- For performance: return only events in the requested range (FullCalendar provides start/end parameters); avoid returning all events for very large datasets.


