from pydantic import BaseModel
from saleae import automation

class DeviceConfiguration(BaseModel):
    enabled_digital_channels : list[int]  = [];
    enabled_analog_channels: list[int]  = [];
    digital_sample_rate:int | None = None;
    analog_sample_rate:int | None = None;
    digital_threshold_volts:float | None = None;

