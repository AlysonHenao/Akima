from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def home(request):
    return render(request,'home.html')

def owner(request):
    return HttpResponse('<h1>Owner</h1>')

def employee(request):
    return HttpResponse('<h1>Employee</h1>')

