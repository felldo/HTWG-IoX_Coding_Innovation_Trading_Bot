from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from binance import Client
import rest_framework.request
import os

@api_view(['GET'])
def test(request):
    return HttpResponse('Give me money')
