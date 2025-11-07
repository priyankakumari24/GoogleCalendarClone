from datetime import datetime, timedelta, timezone
from django.utils import timezone as dj_timezone
from events.models import Event  # adjust if needed

def run():
    now = dj_timezone.now()

    sample_events = [
        # --- Holidays ---
        {
            "title": "🇮🇳 Republic Day",
            "start": datetime(2025, 1, 26, 0, 0, tzinfo=timezone.utc),
            "end": datetime(2025, 1, 26, 23, 59, tzinfo=timezone.utc),
            "all_day": True,
            "color": "#ff6666",
            "description": "National holiday celebrating the Constitution of India."
        },
        {
            "title": "🎆 Diwali",
            "start": datetime(2025, 10, 21, 0, 0, tzinfo=timezone.utc),
            "end": datetime(2025, 10, 21, 23, 59, tzinfo=timezone.utc),
            "all_day": True,
            "color": "#fbbc04",
            "description": "Festival of Lights — celebrate with family and friends."
        },
        {
            "title": "🎄 Christmas",
            "start": datetime(2025, 12, 25, 0, 0, tzinfo=timezone.utc),
            "end": datetime(2025, 12, 25, 23, 59, tzinfo=timezone.utc),
            "all_day": True,
            "color": "#34a853",
            "description": "Merry Christmas!"
        },

        # --- Work ---
        {
            "title": "Team Meeting",
            "start": now + timedelta(days=1, hours=9),
            "end": now + timedelta(days=1, hours=10),
            "all_day": False,
            "color": "#4285f4",
            "description": "Weekly sync with project team."
        },
        {
            "title": "Client Review Call",
            "start": now + timedelta(days=2, hours=16),
            "end": now + timedelta(days=2, hours=17),
            "all_day": False,
            "color": "#34a853",
            "description": "Quarterly project review meeting with client."
        },

        # --- Personal ---
        {
            "title": "🏋️ Gym Workout",
            "start": now + timedelta(days=1, hours=6),
            "end": now + timedelta(days=1, hours=7),
            "all_day": False,
            "color": "#a142f4",
            "description": "Morning workout session."
        },
        {
            "title": "🍽️ Dinner with Friends",
            "start": now + timedelta(days=3, hours=20),
            "end": now + timedelta(days=3, hours=22),
            "all_day": False,
            "color": "#fbbc04",
            "description": "Dinner at Olive Bistro."
        },
    ]

    for data in sample_events:
        Event.objects.get_or_create(title=data["title"], defaults=data)

    print(f"✅ Seeded {len(sample_events)} events successfully.")
