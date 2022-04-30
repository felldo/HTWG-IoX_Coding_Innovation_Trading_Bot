from django.http import HttpResponse
from rest_framework.decorators import api_view

@api_view(['GET'])
def test(request):
    return HttpResponse('Give me money')
