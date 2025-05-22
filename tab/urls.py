# tab/urls.py
from django.urls import path
from . import views

app_name = 'tab' # <--- 이 줄을 추가하세요!

urlpatterns = [
    path('', views.sar_table_view, name='sar_table'),
    path('save_data/', views.save_sar_data_view, name='save_sar_data'),
    path('load_data/', views.load_sar_data_view, name='load_sar_data'),
]