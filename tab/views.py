from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt # 실제 운영에서는 CSRF 처리 필요
import json
from .models import SarDataEntry

def sar_table_view(request):
    # 페이지 로드 시 기존 데이터를 전달할 수 있습니다.
    # sar_entries = SarDataEntry.objects.all()
    # context = {'sar_entries': sar_entries}
    # return render(request, 'myapp/sar_table_template.html', context)
    return render(request, 'tab/sar_table_template.html') # 우선 빈 페이지 로드

@csrf_exempt # 개발 중 테스트를 위해 임시로 CSRF 비활성화, 실제로는 {% csrf_token %} 사용
def save_sar_data_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) # 프론트엔드에서 JSON으로 보낸 데이터 받기
            # 여기서는 받은 data가 테이블 행들의 리스트라고 가정합니다.
            # 각 행 데이터를 SarDataEntry 모델 객체로 만들어 저장합니다.
            # 예시: 한 행만 저장하는 경우
            # entry_data = data[0] # 첫 번째 행 데이터라고 가정
            
            # 실제로는 모든 행을 반복하며 저장하거나, 기존 데이터 업데이트 로직 필요
            # SarDataEntry.objects.all().delete() # 기존 데이터 모두 삭제 후 새로 저장 (단순화된 예시)

            saved_entries = []
            for row_data in data:
                # 빈 문자열을 None으로 변환 (FloatField, DateField 등)
                for key, value in row_data.items():
                    if value == '':
                        if key.endswith('_date'): # 날짜 필드
                            row_data[key] = None
                        elif key in ['distance_mm', 'frequency_mhz', 'measured_sar_1g', 'scaled_sar_1g', 'measured_sar_10g', 'scaled_sar_10g']: # 숫자 필드
                             row_data[key] = None
                        # 다른 숫자 필드들도 필요시 추가

                entry = SarDataEntry.objects.create(
                    system_check_date=row_data.get('system_check_date') or None,
                    test_date=row_data.get('test_date') or None,
                    tested_by=row_data.get('tested_by', ''),
                    sample_no=row_data.get('sample_no', ''),
                    sar_lab=row_data.get('sar_lab', ''),
                    rf_exposure_condition=row_data.get('rf_exposure_condition', ''),
                    mode=row_data.get('mode', ''),
                    dsi=row_data.get('dsi', ''),
                    distance_mm=row_data.get('distance_mm') if row_data.get('distance_mm') not in [None, ''] else None,
                    test_position=row_data.get('test_position', ''),
                    channel=row_data.get('channel', ''),
                    frequency_mhz=row_data.get('frequency_mhz') if row_data.get('frequency_mhz') not in [None, ''] else None,
                    tune_up_limit=row_data.get('tune_up_limit', ''),
                    measured_sar_1g=row_data.get('measured_sar_1g') if row_data.get('measured_sar_1g') not in [None, ''] else None,
                    scaled_sar_1g=row_data.get('scaled_sar_1g') if row_data.get('scaled_sar_1g') not in [None, ''] else None,
                    measured_sar_10g=row_data.get('measured_sar_10g') if row_data.get('measured_sar_10g') not in [None, ''] else None,
                    scaled_sar_10g=row_data.get('scaled_sar_10g') if row_data.get('scaled_sar_10g') not in [None, ''] else None,
                    # ... 나머지 필드들 ...
                )
                saved_entries.append(entry.id) # 저장된 객체의 ID (예시)
            return JsonResponse({'status': 'success', 'message': f'{len(saved_entries)}개 행이 저장되었습니다.', 'ids': saved_entries})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '잘못된 JSON 형식입니다.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'POST 요청만 허용됩니다.'}, status=405)

def load_sar_data_view(request):
    if request.method == 'GET':
        entries = SarDataEntry.objects.all().values() # 모든 데이터를 딕셔너리 리스트로 변환
        return JsonResponse({'status': 'success', 'data': list(entries)})
    return JsonResponse({'status': 'error', 'message': 'GET 요청만 허용됩니다.'}, status=405)

def sar_table_view(request):
    sar_entries = SarDataEntry.objects.all().order_by('id') # 예: ID 순으로 정렬
    # SarDataEntry 객체 리스트를 JSON 직렬화 가능한 형태로 변환할 필요가 있을 수 있음
    # 또는, 템플릿에서 직접 객체를 다루거나, JavaScript로 로드할 데이터만 전달할 수도 있음
    context = {
        'initial_sar_data': list(sar_entries.values()) # .values()로 딕셔너리 리스트로 변환
    }
    return render(request, 'tab/sar_table_template.html', context)