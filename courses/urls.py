from django.urls import path
from django.http import HttpResponse

def home(request):
    return HttpResponse("Courses App Home Page")

urlpatterns = [
    path('', home),
]