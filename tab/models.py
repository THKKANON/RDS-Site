from django.db import models

# 기존 SarDataEntry 모델
class SarDataEntry(models.Model):
    technology_type = models.CharField(max_length=50, db_index=True, default='')
    system_check_date = models.DateField(null=True, blank=True)
    test_date = models.DateField(null=True, blank=True)
    tested_by = models.CharField(max_length=100, null=True, blank=True, default='')
    sample_no = models.CharField(max_length=100, null=True, blank=True, default='')
    sar_lab = models.CharField(max_length=100, null=True, blank=True, default='')
    rf_exposure_condition = models.CharField(max_length=100, blank=True, default='')
    mode = models.CharField(max_length=100, null=True, blank=True, default='')
    dsi = models.CharField(max_length=100, null=True, blank=True, default='')
    distance_mm = models.FloatField(null=True, blank=True)
    test_position = models.CharField(max_length=100, blank=True, default='')
    channel = models.CharField(max_length=100, blank=True, default='')
    frequency_mhz = models.FloatField(null=True, blank=True)

    # ▼▼▼ LTE/NR 기술 방식에서 사용할 새로운 필드 추가 ▼▼▼
    rb = models.CharField(max_length=50, null=True, blank=True)         # 예: RB Size/Count 등
    rb_position = models.CharField(max_length=50, null=True, blank=True) # 예: RB Start/Offset 등
    # ▲▲▲ 새로운 필드 추가 완료 ▲▲▲

    tune_up_limit = models.CharField(max_length=100, null=True, blank=True, default='')
    meas_power = models.CharField(max_length=100, null=True, blank=True, default='')
    measured_sar_1g = models.FloatField(null=True, blank=True)
    scaled_sar_1g = models.FloatField(null=True, blank=True)
    measured_sar_10g = models.FloatField(null=True, blank=True)
    scaled_sar_10g = models.FloatField(null=True, blank=True)
    step_size_mm = models.FloatField(null=True, blank=True)
    dis_3db_peak_mm = models.FloatField(null=True, blank=True)
    z_axis_ratio_percent = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"[{self.technology_type}] SN:{self.sample_no} - {self.test_position}"

    class Meta:
        verbose_name = "SAR Data Entry"
        verbose_name_plural = "SAR Data Entries"


class TechnologyChannelConfig(models.Model):
    technology_type = models.CharField(max_length=50, unique=True, db_index=True)
    channel_count = models.PositiveIntegerField()
    config_locked = models.BooleanField(default=False) # 채널 구성이 저장되어 수정 불가 상태인지 여부

    def __str__(self):
        return f"{self.technology_type} - {self.channel_count} channels (Locked: {self.config_locked})"

class ChannelDetail(models.Model):
    config = models.ForeignKey(TechnologyChannelConfig, related_name='channel_details', on_delete=models.CASCADE)
    channel_number_ui = models.PositiveIntegerField() # UI상의 채널 번호 (1부터 시작)
    ch_name = models.CharField(max_length=100, blank=True, default='') # Ch# (예: Low, Mid, High 또는 숫자)
    frequency_mhz = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.config.technology_type} - UI Ch {self.channel_number_ui}: {self.ch_name} ({self.frequency_mhz} MHz)"