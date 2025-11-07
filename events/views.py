from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import calendar, json, requests
from .models import Event
from rest_framework import viewsets
from .serializers import EventSerializer


# ------------------------------
# 1️⃣ Main Calendar + Dashboard Page
# ------------------------------
def calendar_dashboard(request):
    """
    Renders the unified Calendar + Smart Dashboard view.
    Replaces old `calendar_view` and `dashboard_view`.
    """
    now = datetime.now()
    year = now.year
    month = now.month

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.itermonthdays2(year, month)

    days = [
        {'day': day, 'weekday': calendar.day_name[weekday]}
        for day, weekday in month_days if day != 0
    ]

    return render(request, 'events/calendar_dashboard.html', {
        'month_name': calendar.month_name[month],
        'year': year,
        'days': days
    })


# ------------------------------
# 2️⃣ DRF ViewSet (Optional)
# ------------------------------
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


# ------------------------------
# 3️⃣ Helper: Get Indian holidays for a given year
# ------------------------------
def get_indian_holidays_for_year(year: int):
    """Fetch Indian holidays via API or fallback list."""
    holidays_url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/IN"
    holidays = []

    try:
        response = requests.get(holidays_url, timeout=10)
        if response.status_code == 200:
            holidays = response.json()
        else:
            print(f"⚠️ API returned {response.status_code} for {year}, using fallback data.")
    except Exception as e:
        print(f"🌐 Error fetching holidays for {year}: {e}")

    # Fallback if API fails
    if not holidays:
        holidays = [
            {"localName": "Republic Day", "date": f"{year}-01-26"},
            {"localName": "Holi", "date": f"{year}-03-14"},
            {"localName": "Independence Day", "date": f"{year}-08-15"},
            {"localName": "Gandhi Jayanti", "date": f"{year}-10-02"},
            {"localName": "Diwali", "date": f"{year}-10-21"},
            {"localName": "Christmas", "date": f"{year}-12-25"},
        ]

    # Format for frontend
    formatted = [
        {
            "title": f"🇮🇳 {h['localName']}",
            "start": h["date"],
            "allDay": True,
            "color": "#ff6666"
        }
        for h in holidays
    ]
    return formatted


# ------------------------------
# 4️⃣ Unified Events Endpoint
# ------------------------------
def event_list(request):
    """
    Return combined list of user events + Indian holidays
    for the visible calendar range.
    """
    print("🟢 Processing /api/events request")

    # Handle calendar date range
    start = request.GET.get('start')
    end = request.GET.get('end')

    start_year = datetime.fromisoformat(start).year if start else datetime.now().year
    end_year = datetime.fromisoformat(end).year if end else start_year

    # User-created events
    db_events = [
        {
            'id': e.id,
            'title': e.title,
            'start': e.start.isoformat(),
            'end': e.end.isoformat(),
            'allDay': e.all_day,
            'color': getattr(e, 'color', '#4285f4')
        }
        for e in Event.objects.all()
    ]
    print(f"🟢 Found {len(db_events)} user events")

    # Fetch Indian holidays
    all_holidays = []
    for year in range(start_year, end_year + 1):
        all_holidays.extend(get_indian_holidays_for_year(year))

    # Combine
    data = db_events + all_holidays
    print(f"✅ Returning total events: {len(data)}")
    return JsonResponse(data, safe=False)


# ------------------------------
# 5️⃣ CRUD Endpoints for Events
# ------------------------------
@csrf_exempt
def event_create(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        event = Event.objects.create(
            title=data.get('title', 'Untitled Event'),
            start=data['start'],
            end=data.get('end', data['start']),
            all_day=data.get('allDay', True),
            color=data.get('color', '#4285f4')
        )
        return JsonResponse({
            'id': event.id,
            'title': event.title,
            'start': event.start.isoformat(),
            'end': event.end.isoformat(),
            'allDay': event.all_day,
            'color': event.color,
        })


@csrf_exempt
def event_delete(request, pk):
    if request.method == 'DELETE':
        try:
            event = Event.objects.get(pk=pk)
            event.delete()
            return JsonResponse({'success': True})
        except Event.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=404)


@csrf_exempt
def event_update(request, pk):
    """Handle PUT requests for event update (drag, resize, edit)."""
    if request.method == 'PUT':
        try:
            event = Event.objects.get(pk=pk)
            data = json.loads(request.body)
            event.start = data.get('start', event.start)
            event.end = data.get('end', event.end)
            event.all_day = data.get('allDay', event.all_day)
            event.color = data.get('color', event.color)
            event.save()
            return JsonResponse({'success': True})
        except Event.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=404)
