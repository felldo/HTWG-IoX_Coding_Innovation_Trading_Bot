from django.urls import path
from . import views

urlpatterns = [
    path('tickers/', views.get_all_tickers),
    path('ticker/', views.get_symbol_ticker),
    path('kline/', views.get_klines_data),
    path('symbol/', views.get_symbol_info),
    path('account/', views.get_account_info),
    path('overview/', views.get_overview),
    path('bot_trading/', views.get_bot_is_trading),
]

