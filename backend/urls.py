from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path, include
from .views import RootView

urlpatterns = [
    path('', RootView.as_view()),
    path('admin/', admin.site.urls),
    path('auth/', include('rest_framework.urls')),
    path('api/', include('api.urls')),
]

urlpatterns = format_suffix_patterns(urlpatterns)
