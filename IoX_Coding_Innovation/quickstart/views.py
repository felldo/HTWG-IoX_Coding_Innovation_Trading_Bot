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

client = Client(api_key=os.environ['BINANCE_API_KEY'], api_secret=os.environ['BINANCE_SECRET'], testnet=False)
print(client.get_all_tickers())
print(client.get_my_trades(symbol="BTCBUSD"))


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
def get_all_coins(request: rest_framework.request.Request):
    print(request.user)
    print(request.query_params)
    data = client.get_symbol_ticker(symbol=request.query_params['name'])
    return Response(data=data, content_type="application/json")


@api_view(['GET'])
def get_coin_info(request: rest_framework.request.Request):
    data = client.get_symbol_info(symbol=request.query_params['name'])
    return Response(data=data, content_type="application/json")


@api_view(['GET'])
def snippet_detail(request, pk):
    # def snippet_detail(request, pk):
    """
    Retrieve, update or delete a code snippet.
    """
    print(request.body)

    return Response("")
