from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    all_day = models.BooleanField(default=False)
    color = models.CharField(max_length=20, default="#4285f4")  # 👈 important
    location = models.CharField(max_length=255, blank=True, null=True)
    recurrence_rule = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title
