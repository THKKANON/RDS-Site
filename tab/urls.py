# tab/urls.py
from django.urls import path
from . import views

app_name = 'tab'
urlpatterns = [
    path('select/', views.select_technology_view, name='select_technology'),
    path('<str:technology_type>/', views.sar_table_view, name='sar_table'),
    path('<str:technology_type>/save_data/', views.save_sar_data_view, name='save_sar_data'),
    path('<str:technology_type>/load_data/', views.load_sar_data_view, name='load_sar_data'),
    path('<str:technology_type>/save_channel_config/', views.save_channel_config_view, name='save_channel_config'), # << 새로 추가
]