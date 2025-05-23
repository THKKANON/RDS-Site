from django.contrib import admin
from .models import SarDataEntry, TechnologyChannelConfig, ChannelDetail # 현재 앱의 models.py에서 모델들을 가져옵니다.

# 각 모델을 admin 사이트에 등록합니다.
admin.site.register(SarDataEntry)
admin.site.register(TechnologyChannelConfig)
admin.site.register(ChannelDetail)