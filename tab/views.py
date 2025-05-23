# tab/views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import json
from .models import SarDataEntry
import logging # 로깅 추가

logger = logging.getLogger(__name__) # 로거 설정

VALID_TECHNOLOGIES = ["GSM", "WCDMA", "LTE", "NR", "WIFI"] 

def select_technology_view(request):
    return render(request, 'tab/select_technology.html')

def sar_table_view(request, technology_type):
    print(f"--- sar_table_view ---")
    print(f"Received technology_type from URL: '{technology_type}' (type: {type(technology_type)})")
    
    tech_upper = technology_type.upper()
    
    if not technology_type or tech_upper not in VALID_TECHNOLOGIES:
        print(f"Error: Invalid technology_type - '{technology_type}' before raising Http404")
        raise Http404(f"잘못된 기술 방식입니다: {technology_type}")

    initial_data_qs = [] # 기본값 초기화
    context = {
        'technology_type': tech_upper, # 먼저 tech_upper를 context에 할당
        'initial_sar_data': [] # initial_sar_data도 기본값으로 초기화
    }

    try:
        print(f"Attempting to filter SarDataEntry for technology_type: {tech_upper}")
        initial_data_qs = SarDataEntry.objects.filter(technology_type=tech_upper).order_by('id').values()
        context['initial_sar_data'] = list(initial_data_qs)
        print(f"Successfully fetched initial_data_qs. Count: {len(initial_data_qs)}")

    except Exception as e:
        # 데이터베이스 쿼리 또는 다른 로직에서 오류 발생 시 로깅
        print(f"Error during database query or context preparation for {tech_upper}: {e}")
        logger.error(f"Error in sar_table_view for {tech_upper}: {e}", exc_info=True)
        # 이 경우, initial_sar_data는 빈 리스트로 유지되고, technology_type은 이미 context에 있음
        # 또는, 오류 페이지를 보여주거나 다른 처리를 할 수도 있습니다.
        # 여기서는 일단 빈 데이터로 템플릿을 렌더링하도록 합니다.
        # 하지만 `technology_type`은 context에 여전히 존재해야 합니다.

    print(f"Final context for template: {context}") # 최종 컨텍스트 확인
    
    # technology_type이 context에 확실히 있는지 다시 한번 확인
    if 'technology_type' not in context or not context['technology_type']:
        print("CRITICAL ERROR: technology_type is missing or empty in final context!")
        # 이 경우 NoReverseMatch가 발생할 수 있음
        # 여기서 Http404를 발생시키거나 기본값으로 설정하는 등의 추가 방어 로직 필요
        context['technology_type'] = "UNKNOWN_ERROR" # 임시 값으로라도 설정하여 NoReverseMatch 방지 시도

    return render(request, 'tab/sar_table_template.html', context)

# ... (save_sar_data_view, load_sar_data_view 함수는 이전과 동일하게 유지) ...
@csrf_exempt 
def save_sar_data_view(request, technology_type):
    # (이전 답변의 코드와 동일)
    tech_upper = technology_type.upper()
    if not technology_type or tech_upper not in VALID_TECHNOLOGIES:
        return JsonResponse({'status': 'error', 'message': '유효하지 않은 기술 방식입니다.'}, status=400)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            SarDataEntry.objects.filter(technology_type=tech_upper).delete()
            saved_entries_count = 0
            for row_data in data:
                for key, value in row_data.items():
                    if isinstance(value, str) and value.strip() == '':
                        if key.endswith('_date') or key in ['distance_mm', 'frequency_mhz', 'measured_sar_1g', 'scaled_sar_1g', 'measured_sar_10g', 'scaled_sar_10g', 'step_size_mm', 'dis_3db_peak_mm', 'z_axis_ratio_percent']:
                            row_data[key] = None
                    elif key in ['distance_mm', 'frequency_mhz', 'measured_sar_1g', 'scaled_sar_1g', 'measured_sar_10g', 'scaled_sar_10g', 'step_size_mm', 'dis_3db_peak_mm', 'z_axis_ratio_percent'] and value is not None:
                        try:
                            row_data[key] = float(value)
                        except (ValueError, TypeError):
                            row_data[key] = None 

                SarDataEntry.objects.create(
                    technology_type=tech_upper,
                    system_check_date=row_data.get('system_check_date'),
                    test_date=row_data.get('test_date'),
                    tested_by=row_data.get('tested_by', ''),
                    sample_no=row_data.get('sample_no', ''),
                    sar_lab=row_data.get('sar_lab', ''),
                    rf_exposure_condition=row_data.get('rf_exposure_condition', ''),
                    mode=row_data.get('mode', ''),
                    dsi=row_data.get('dsi', ''),
                    distance_mm=row_data.get('distance_mm'),
                    test_position=row_data.get('test_position', ''),
                    channel=row_data.get('channel', ''),
                    frequency_mhz=row_data.get('frequency_mhz'),
                    tune_up_limit=row_data.get('tune_up_limit', ''),
                    meas_power=row_data.get('meas_power', ''), 
                    measured_sar_1g=row_data.get('measured_sar_1g'),
                    scaled_sar_1g=row_data.get('scaled_sar_1g'),
                    measured_sar_10g=row_data.get('measured_sar_10g'),
                    scaled_sar_10g=row_data.get('scaled_sar_10g'),
                    step_size_mm=row_data.get('step_size_mm'),
                    dis_3db_peak_mm=row_data.get('dis_3db_peak_mm'),
                    z_axis_ratio_percent=row_data.get('z_axis_ratio_percent')
                )
                saved_entries_count += 1
            return JsonResponse({'status': 'success', 'message': f'[{tech_upper}] {saved_entries_count}개 행이 저장되었습니다.'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '잘못된 JSON 형식입니다.'}, status=400)
        except Exception as e:
            logger.error(f"Error saving SAR data for {tech_upper}: {e}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': f'데이터 저장 중 오류 발생: {str(e)}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'POST 요청만 허용됩니다.'}, status=405)

def load_sar_data_view(request, technology_type):
    # (이전 답변의 코드와 동일)
    tech_upper = technology_type.upper()
    if not technology_type or tech_upper not in VALID_TECHNOLOGIES:
        return JsonResponse({'status': 'error', 'message': '유효하지 않은 기술 방식입니다.'}, status=400)

    if request.method == 'GET':
        try:
            entries = SarDataEntry.objects.filter(technology_type=tech_upper).order_by('id').values()
            return JsonResponse({'status': 'success', 'data': list(entries)})
        except Exception as e:
            logger.error(f"Error loading SAR data for {tech_upper}: {e}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'GET 요청만 허용됩니다.'}, status=405)