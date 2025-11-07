from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    all_day = models.BooleanField(default=False)
    color = models.CharField(max_length=20, default='#4285f4')
    location = models.CharField(max_length=200, blank=True)
    recurrence_rule = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.title
