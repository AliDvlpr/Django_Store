from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('god/', views.say_that)
]
