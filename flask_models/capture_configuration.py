from pydantic import BaseModel

class CaptureCofiguration(BaseModel):
    buffer_size_megabytes:int | None = None;
    trim_data_seconds: float | None = None;
    duration_seconds:float| None = None;