from django.shortcuts import render


def employee(request):
    return render(request, 'production/employee.html')