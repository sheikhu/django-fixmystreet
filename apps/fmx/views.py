from django.shortcuts import render
from django.http import HttpResponse


def ack(request):
    return HttpResponse('ok ack')

def attachments(request, report_id):
    return HttpResponse('ok attachments %s' %report_id)

def categories(request):
    return HttpResponse('ok categories')

def detail(request, report_id):
    return HttpResponse('ok report %s' %report_id)

def stats(request):
    return HttpResponse('ok stats')
