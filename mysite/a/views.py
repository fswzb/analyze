from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return HttpResponse(u'hello a')


def preadd(request):
    return render(request, 'home.html')


def add(request, a, b):
    c = int(a) + int(b)
    return HttpResponse(str(c))
