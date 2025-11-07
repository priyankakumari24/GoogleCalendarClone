"""
URL configuration for calendar_clone project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from events import views  

router = routers.DefaultRouter()
router.register(r'events', views.EventViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.calendar_dashboard, name='calendar_dashboard'),
    path('api/events/', views.event_list, name='event_list'),
    path('api/events/create/', views.event_create, name='event_create'),
    path('api/events/<int:pk>/delete/', views.event_delete, name='event_delete'),
]
