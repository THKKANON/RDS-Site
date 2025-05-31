from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
import json
from .models import SarDataEntry, TechnologyChannelConfig, ChannelDetail # 모델 임포트
import logging

logger = logging.getLogger(__name__)
VALID_TECHNOLOGIES = ["GSM", "WCDMA", "LTE", "NR", "WIFI"]

# 기술 방식과 템플릿 파일명을 매핑하는 딕셔너리
TECHNOLOGY_TEMPLATE_MAP = {
    "GSM": "tab/sar_table_gsm.html",
    "WCDMA": "tab/sar_table_wcdma.html",
    "LTE": "tab/sar_table_lte.html", # LTE는 기존 템플릿을 사용하거나 필요시 "tab/sar_table_lte.html" 등으로 변경
    "NR": "tab/sar_table_nr.html",
    "WIFI": "tab/sar_table_wifi.html",
}

def select_technology_view(request):
    return render(request, 'tab/select_technology.html')

@ensure_csrf_cookie
def sar_table_view(request, technology_type):
    tech_upper = technology_type.upper()
    if not technology_type or tech_upper not in VALID_TECHNOLOGIES:
        raise Http404(f"잘못된 기술 방식입니다: {technology_type}")

    # 매핑된 템플릿 이름을 가져옵니다.
    template_name = TECHNOLOGY_TEMPLATE_MAP.get(tech_upper)
    if not template_name:
        # VALID_TECHNOLOGIES에 있지만 TECHNOLOGY_TEMPLATE_MAP에 없는 경우의 처리
        # 예를 들어, 모든 기술에 대한 기본 템플릿을 지정하거나, 에러를 발생시킬 수 있습니다.
        # 여기서는 Http404를 발생시키도록 하겠습니다.
        logger.warning(f"'{tech_upper}'에 대해 정의된 테이블 템플릿이 TECHNOLOGY_TEMPLATE_MAP에 없습니다.")
        raise Http404(f"'{tech_upper}'에 대해 정의된 테이블 템플릿이 없습니다.")

    # 1. 채널 설정 정보 로드
    channel_config = TechnologyChannelConfig.objects.filter(technology_type=tech_upper).first()
    initial_page_config = {
        'isChannelConfigDone': False,
        'configuredNumChannels': 0,
        'channelDetails': []
        # sarDataExists는 아래에서 설정
    }
    if channel_config and channel_config.config_locked:
        initial_page_config['isChannelConfigDone'] = True
        initial_page_config['configuredNumChannels'] = channel_config.channel_count
        details = ChannelDetail.objects.filter(config=channel_config).order_by('channel_number_ui')
        for detail in details:
            initial_page_config['channelDetails'].append({'ch': detail.ch_name, 'freq': detail.frequency_mhz})

    # 2. 기존 SAR 데이터 로드
    initial_sar_data = list(SarDataEntry.objects.filter(technology_type=tech_upper).order_by('id').values())
    
    # 3. SAR 데이터 존재 유무 확인 및 initial_page_config에 추가
    sar_data_exists = bool(initial_sar_data) 
    initial_page_config['sarDataExists'] = sar_data_exists

    logger.debug(f"VIEW_DEBUG: For '{tech_upper}', attempting to render with template: '{template_name}'")
    logger.debug(f"VIEW_DEBUG: For '{tech_upper}', sar_data_exists: {sar_data_exists}")
    logger.debug(f"VIEW_DEBUG: For '{tech_upper}', initial_page_config being sent: {initial_page_config}")
    logger.debug(f"VIEW_DEBUG: For '{tech_upper}', initial_sar_data count: {len(initial_sar_data)}")
    
    context = {
        'technology_type': tech_upper,
        'initial_sar_data': initial_sar_data, 
        'initial_page_config': initial_page_config 
    }
    # 선택된 템플릿으로 렌더링
    return render(request, template_name, context)


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

            config, created = TechnologyChannelConfig.objects.update_or_create(
                technology_type=tech_upper,
                defaults={'channel_count': num_channels, 'config_locked': True}
            )
            
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
                'channel_config_updated': True,
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
                db_id = row_data.pop('id', None) 

                for key, value in row_data.items():
                    if isinstance(value, str) and value.strip() == '':
                        if key.endswith('_date') or key in ['distance_mm', 'frequency_mhz', 'measured_sar_1g', 'scaled_sar_1g', 'measured_sar_10g', 'scaled_sar_10g', 'step_size_mm', 'dis_3db_peak_mm', 'z_axis_ratio_percent']:
                            row_data[key] = None
                    elif key in ['distance_mm', 'frequency_mhz', 'measured_sar_1g', 'scaled_sar_1g', 'measured_sar_10g', 'scaled_sar_10g', 'step_size_mm', 'dis_3db_peak_mm', 'z_axis_ratio_percent'] and value is not None:
                        try:
                            row_data[key] = float(value)
                        except (ValueError, TypeError):
                            row_data[key] = None
                
                row_data['technology_type'] = tech_upper

                if db_id: 
                    SarDataEntry.objects.filter(id=db_id, technology_type=tech_upper).update(**row_data)
                    updated_count += 1
                else: 
                    SarDataEntry.objects.create(**row_data)
                    created_count += 1
            
            return JsonResponse({'status': 'success', 'message': f'[{tech_upper}] 데이터 저장 완료 (생성: {created_count}건, 업데이트: {updated_count}건)'})
        except Exception as e:
            logger.error(f"Error saving SAR data for {tech_upper}: {e}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': f'데이터 저장 중 오류 발생: {str(e)}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'POST 요청만 허용됩니다.'}, status=405)


def load_sar_data_view(request, technology_type):
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