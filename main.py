from saleae import automation
from typing import  Union
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import os.path
from datetime import datetime

from fastapi import FastAPI, HTTPException


from flask_models.device_configuration import DeviceConfiguration
from flask_models.capture_configuration import CaptureCofiguration
from flask_models.capture_settings import CaptureSettings

class CaptureMode:
     @staticmethod
     def create_instance(**kwargs):
          if 'duration_seconds' in kwargs:
            return automation.CaptureConfiguration(capture_mode=automation.TimedCaptureMode(kwargs['duration_seconds'],kwargs['trim_data_seconds']),buffer_size_megabytes= kwargs['buffer_size_megabytes'])
          else:
            return automation.CaptureConfiguration(capture_mode=automation.TimedCaptureMode(kwargs['trim_data_seconds']),buffer_size_megabytes= kwargs['buffer_size_megabytes'])



app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


try:
    app.state.manager = automation.Manager.connect(connect_timeout_seconds=30)
    app.state.device_configuration = automation.LogicDeviceConfiguration(enabled_digital_channels=[0, 1, 2, 3],
        digital_sample_rate=10_000_000,
        digital_threshold_volts=3.3,)
    app.state.capture_configuration = automation.CaptureConfiguration(
        capture_mode=automation.TimedCaptureMode(duration_seconds=5.0)
    )
except:
    print('Issues opening Saleae manager')





@app.post("/configure")
async def configuration(device:DeviceConfiguration , capture:CaptureCofiguration):
    
    
    try:
        app.state.device_configuration=automation.LogicDeviceConfiguration(enabled_digital_channels=device.enabled_digital_channels, enabled_analog_channels=device.enabled_analog_channels,
                                                                digital_sample_rate=device.digital_sample_rate,analog_sample_rate=device.analog_sample_rate,digital_threshold_volts=device.digital_threshold_volts)

        app.state.capture_configuration=CaptureMode.create_instance(**capture.model_dump())
    except Exception as exp:
        raise HTTPException(status_code=500, detail=f"server error {exp}")
    else:
        results = {"device_configuration":app.state.device_configuration, "capture_configuration":app.state.capture_configuration}
        return results

@app.post("/capture")
async def capture_measurements(settings:CaptureSettings):
    try:
        with app.state.manager.start_capture(
                device_id='F4244',
                device_configuration=app.state.device_configuration,
                capture_configuration=app.state.capture_configuration) as capture:
                capture.wait()
                analyzer = capture.add_analyzer(settings.type,label=settings.label,settings=settings.settings)
                output_dir = os.path.join(os.getcwd(), f'./measurements/output-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}')
                print(output_dir)
                os.makedirs(output_dir)
                    # Export analyzer data to a CSV file
                analyzer_export_filepath = os.path.join(output_dir, 'spi_export.csv')
                capture.export_data_table(
                        filepath=analyzer_export_filepath,
                        analyzers=[analyzer]
                    )
    except Exception as exp:
        raise HTTPException(status_code=500, detail=f"server error {exp}")
    else:
        return{"message":"success"}
