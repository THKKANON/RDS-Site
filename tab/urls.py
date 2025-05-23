from django.urls import path
from . import views # 'tab' 앱 내의 views.py를 import

app_name = 'tab' # 네임스페이스 정의 (매우 중요!)

urlpatterns = [
    # 예: /tab/select/ 요청 시 views.select_technology_view 함수 실행
    path('select/', views.select_technology_view, name='select_technology'),
    
    # 예: /tab/GSM/ 요청 시 views.sar_table_view 함수 실행 (technology_type='GSM' 전달)
    path('<str:technology_type>/', views.sar_table_view, name='sar_table'),
    
    # 예: /tab/GSM/save_data/ 요청 시 views.save_sar_data_view 함수 실행
    path('<str:technology_type>/save_data/', views.save_sar_data_view, name='save_sar_data'),
    
    # 예: /tab/GSM/load_data/ 요청 시 views.load_sar_data_view 함수 실행
    path('<str:technology_type>/load_data/', views.load_sar_data_view, name='load_sar_data'),
]