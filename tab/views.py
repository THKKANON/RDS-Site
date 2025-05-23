from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
import json
from .models import SarDataEntry, TechnologyChannelConfig, ChannelDetail # 새 모델 임포트
import logging

logger = logging.getLogger(__name__)
VALID_TECHNOLOGIES = ["GSM", "WCDMA", "LTE", "NR", "WIFI"]

def select_technology_view(request):
    return render(request, 'tab/select_technology.html')

@ensure_csrf_cookie # GET 요청에도 CSRF 쿠키 설정 (POST 시 JavaScript에서 사용)
def sar_table_view(request, technology_type):
    tech_upper = technology_type.upper()
    if not technology_type or tech_upper not in VALID_TECHNOLOGIES:
        raise Http404(f"잘못된 기술 방식입니다: {technology_type}")

    channel_config = TechnologyChannelConfig.objects.filter(technology_type=tech_upper).first()
    initial_page_config = {
        'isChannelConfigDone': False,
        'configuredNumChannels': 0,
        'channelDetails': []
    }
    if channel_config and channel_config.config_locked:
        initial_page_config['isChannelConfigDone'] = True
        initial_page_config['configuredNumChannels'] = channel_config.channel_count
        details = ChannelDetail.objects.filter(config=channel_config).order_by('channel_number_ui')
        for detail in details:
            initial_page_config['channelDetails'].append({'ch': detail.ch_name, 'freq': detail.frequency_mhz})

    initial_sar_data = list(SarDataEntry.objects.filter(technology_type=tech_upper).order_by('id').values())
    
    context = {
        'technology_type': tech_upper,
        'initial_sar_data': initial_sar_data, # For table data itself
        'initial_page_config': initial_page_config # For page state (channel config)
    }
    return render(request, 'tab/sar_table_template.html', context)


@csrf_exempt 
def save_channel_config_view(request, technology_type):
    tech_upper = technology_type.upper()
    if not technology_type or tech_upper not in VALID_TECHNOLOGIES:
        return JsonResponse({'status': 'error', 'message': '유효하지 않은 기술 방식입니다.'}, status=400)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            num_channels = int(data.get('num_channels', 0))
            channel_details_data = data.get('channel_details', [])

            if not (1 <= num_channels <= 6 and len(channel_details_data) == num_channels):
                return JsonResponse({'status': 'error', 'message': '채널 개수 또는 채널 정보가 올바르지 않습니다.'}, status=400)

            # 기존 설정이 있다면 업데이트, 없다면 새로 생성 (config_locked=True로 설정)
            config, created = TechnologyChannelConfig.objects.update_or_create(
                technology_type=tech_upper,
                defaults={'channel_count': num_channels, 'config_locked': True}
            )
            
            # 기존 채널 상세 정보 삭제 후 새로 저장
            ChannelDetail.objects.filter(config=config).delete()
            for i, detail_data in enumerate(channel_details_data):
                ChannelDetail.objects.create(
                    config=config,
                    channel_number_ui=i + 1,
                    ch_name=detail_data.get('ch', ''),
                    frequency_mhz=float(detail_data.get('freq')) if detail_data.get('freq') else None
                )
            
            return JsonResponse({
                'status': 'success', 
                'message': f'[{tech_upper}] 채널 설정이 저장되었습니다. 채널 개수: {num_channels}',
                'channel_config_updated': True, # 프론트엔드 상태 업데이트용
                'configured_channel_count': num_channels,
                'channel_details': channel_details_data
            })

        except Exception as e:
            logger.error(f"Error saving channel config for {tech_upper}: {e}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': f'채널 설정 저장 중 오류: {str(e)}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'POST 요청만 허용됩니다.'}, status=405)


@csrf_exempt
def save_sar_data_view(request, technology_type):
    tech_upper = technology_type.upper()
    if not technology_type or tech_upper not in VALID_TECHNOLOGIES:
        return JsonResponse({'status': 'error', 'message': '유효하지 않은 기술 방식입니다.'}, status=400)

    # 채널 구성이 먼저 완료되었는지 확인 (선택적이지만 권장)
    channel_config = TechnologyChannelConfig.objects.filter(technology_type=tech_upper, config_locked=True).first()
    if not channel_config:
        return JsonResponse({'status': 'error', 'message': '먼저 채널 설정을 저장해야 합니다.'}, status=400)

    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            rows_data = payload.get('rows', [])
            
            updated_count = 0
            created_count = 0

            for row_data in rows_data:
                db_id = row_data.pop('id', None) # id 필드를 가져오고 row_data에서는 제거

                # 숫자 및 날짜 필드에 대한 None 및 타입 변환 처리
                for key, value in row_data.items():
                    if isinstance(value, str) and value.strip() == '':
                        if key.endswith('_date') or key in ['distance_mm', 'frequency_mhz', 'measured_sar_1g', 'scaled_sar_1g', 'measured_sar_10g', 'scaled_sar_10g', 'step_size_mm', 'dis_3db_peak_mm', 'z_axis_ratio_percent']:
                            row_data[key] = None
                    elif key in ['distance_mm', 'frequency_mhz', 'measured_sar_1g', 'scaled_sar_1g', 'measured_sar_10g', 'scaled_sar_10g', 'step_size_mm', 'dis_3db_peak_mm', 'z_axis_ratio_percent'] and value is not None:
                        try:
                            row_data[key] = float(value)
                        except (ValueError, TypeError):
                            row_data[key] = None
                
                # technology_type은 URL에서 받은 것을 사용
                row_data['technology_type'] = tech_upper

                if db_id: # ID가 있으면 업데이트
                    SarDataEntry.objects.filter(id=db_id, technology_type=tech_upper).update(**row_data)
                    updated_count += 1
                else: # ID가 없으면 새로 생성
                    # 필수 필드가 row_data에 모두 있는지 확인하는 로직 추가 가능
                    SarDataEntry.objects.create(**row_data)
                    created_count += 1
            
            return JsonResponse({'status': 'success', 'message': f'[{tech_upper}] 데이터 저장 완료 (생성: {created_count}건, 업데이트: {updated_count}건)'})
        except Exception as e:
            logger.error(f"Error saving SAR data for {tech_upper}: {e}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': f'데이터 저장 중 오류 발생: {str(e)}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'POST 요청만 허용됩니다.'}, status=405)


def load_sar_data_view(request, technology_type):
    # (이전 답변의 코드와 거의 동일, technology_type.upper() 사용)
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