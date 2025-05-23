from django.db import models

class SarDataEntry(models.Model):
    # 새로운 필드 추가 (이전에 추가됨)
    technology_type = models.CharField(max_length=50, db_index=True) # 예: "GSM", "LTE", "WIFI" 등

    # 기존 필드들
    system_check_date = models.DateField(null=True, blank=True)
    test_date = models.DateField(null=True, blank=True)
    tested_by = models.CharField(max_length=100, blank=True, default='')
    sample_no = models.CharField(max_length=100, blank=True, default='')
    sar_lab = models.CharField(max_length=100, blank=True, default='')
    rf_exposure_condition = models.CharField(max_length=100, blank=True, default='')
    mode = models.CharField(max_length=100, blank=True, default='')
    dsi = models.CharField(max_length=100, blank=True, default='')
    distance_mm = models.FloatField(null=True, blank=True)
    test_position = models.CharField(max_length=100, blank=True, default='')
    channel = models.CharField(max_length=100, blank=True, default='') # Ch#
    frequency_mhz = models.FloatField(null=True, blank=True)
    tune_up_limit = models.CharField(max_length=100, blank=True, default='')

    meas_power = models.CharField(max_length=100, blank=True, default='') 
    
    measured_sar_1g = models.FloatField(null=True, blank=True)
    scaled_sar_1g = models.FloatField(null=True, blank=True)
    measured_sar_10g = models.FloatField(null=True, blank=True)
    scaled_sar_10g = models.FloatField(null=True, blank=True)
    step_size_mm = models.FloatField(null=True, blank=True)
    dis_3db_peak_mm = models.FloatField(null=True, blank=True)
    z_axis_ratio_percent = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"[{self.technology_type}] SN:{self.sample_no} - {self.test_position} ({self.frequency_mhz}MHz)"

    class Meta:
        verbose_name = "SAR Data Entry"
        verbose_name_plural = "SAR Data Entries"
        # ordering = ['-test_date', 'sample_no'] # 예시 정렬 순서