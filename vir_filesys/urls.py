from django.urls import path
from .views import home_view, OpenView

urlpatterns = [
    path('home/', home_view, name="home_view"),
    path('open/<str:file_name>/', OpenView.as_view()),
    path('open/', OpenView.as_view(), name="open_view"),
]