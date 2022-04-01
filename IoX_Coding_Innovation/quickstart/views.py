# Create your views here.
import rest_framework.request
from django.contrib.auth.models import User, Group
# from requests import Response
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from IoX_Coding_Innovation.quickstart.serializers import UserSerializer, GroupSerializer
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import json
import os

client = Client(os.environ['BINANCE_API_KEY'], os.environ['BINANCE_SECRET'])


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
def hello_world(request: rest_framework.request.Request):
    print(request.user)
    print(request.query_params)
    print(request.query_params['id'])
    # data = {}
    # list = [1, 2, 3, 4]
    # data['x'] = "test"
    # data['y'] = list
    # print(json.dumps(data))
    data = client.get_symbol_ticker(symbol=request.query_params['id'])
    return Response(data=data, content_type="application/json")
    # return Response({"message": "Hello, world!"})


@api_view(['GET'])
def snippet_detail(request, pk):
    # def snippet_detail(request, pk):
    """
    Retrieve, update or delete a code snippet.
    """
    print(request.body)

    return Response("")
