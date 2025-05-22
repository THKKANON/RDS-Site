from django.db import models

# Create your models here.
from django.db import models

class SarDataEntry(models.Model):
    system_check_date = models.DateField(null=True, blank=True)
    test_date = models.DateField(null=True, blank=True)
    tested_by = models.CharField(max_length=100, blank=True)
    sample_no = models.CharField(max_length=100, blank=True)
    sar_lab = models.CharField(max_length=100, blank=True)
    rf_exposure_condition = models.CharField(max_length=100, blank=True)
    mode = models.CharField(max_length=100, blank=True)
    dsi = models.CharField(max_length=100, blank=True)
    distance_mm = models.FloatField(null=True, blank=True)
    test_position = models.CharField(max_length=100, blank=True)
    channel = models.CharField(max_length=100, blank=True) # Ch#
    frequency_mhz = models.FloatField(null=True, blank=True)
    tune_up_limit = models.CharField(max_length=100, blank=True) # 숫자 또는 범위일 수 있음
    measured_sar_1g = models.FloatField(null=True, blank=True) # 1-g SAR Meas
    scaled_sar_1g = models.FloatField(null=True, blank=True)   # 1-g SAR Scaled
    measured_sar_10g = models.FloatField(null=True, blank=True) # 10-g SAR Meas
    scaled_sar_10g = models.FloatField(null=True, blank=True)  # 10-g SAR Scaled

    step_size_mm = models.FloatField(null=True, blank=True)  # step size
    dis_3db_peak_mm = models.FloatField(null=True, blank=True)  # dis 3dB
    z_axis_ratio_percent = models.FloatField(null=True, blank=True)  # Z Axis

    def __str__(self):
        return f"{self.sample_no} - {self.test_position} at {self.frequency_mhz}MHz"