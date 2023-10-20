from pydantic import BaseModel

class CaptureSettings(BaseModel):
    type:str ;
    label: str;
    settings: dict;