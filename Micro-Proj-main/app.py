from pydantic import BaseModel, validator
from typing import List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os
import httpx
from fastapi import FastAPI, HTTPException

class VoltageData(BaseModel):
    timestamp: datetime
    voltage: float
    current: float

    @validator('timestamp', pre=True)
    def parse_timestamp(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, '%d-%m-%Y %H:%M')
        return value

    @validator('voltage', 'current')
    def round_to_three_decimals(cls, value):
        return round(value, 3)

app = FastAPI()

# Connect to MongoDB
client = AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.volt
voltage_collection = db.voltage_data 
ELECTICITY_RATE = 4 

async def send_line_notify(message: str):
    line_token = "TKYcPVB3L64orl1zYU2GvKqCdBBa6KrAh32KHHSU7Fz" # Change with your LINE token
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {line_token}'}
    data = {'message': message}

    async with httpx.AsyncClient() as client:
        response = await client.post(line_notify_api, headers=headers, data=data)
        return response.status_code

@app.post("/add_voltage_data/")
async def add_voltage_data(data: VoltageData):
    document = data.dict()
    result = await voltage_collection.insert_one(document)
    if result.inserted_id:
        power_watt = data.voltage * data.current
        energy_kwh = power_watt * 1 / 1000 # Assuming 1 hour
        electricity_cost = energy_kwh * ELECTICITY_RATE 
        await send_line_notify(f"**New voltage data:**\n\n"
                               f"Date and time: {data.timestamp}\n"
                               f"Voltage: {data.voltage} V\n"
                               f"Current: {data.current} A\n"
                               f"Electricity cost: {electricity_cost:.4f} THB\n" 
                              )
        return {"status": "success", "inserted_id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=400, detail="Failed to add data.")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/get_voltage_data/", response_model=List[VoltageData])
async def get_voltage_data():
    voltage_data = await voltage_collection.find().to_list(100) 
    return voltage_data

@app.get("/get_voltage_data_with_cost/", response_model=List[VoltageData])
async def get_voltage_data_with_cost():
    voltage_data = await voltage_collection.find().to_list(100)
    for data in voltage_data:
        data["power_watt"] = data["voltage"] * data["current"]
        data["energy_kwh"] = data["power_watt"] * 1 / 1000
    return voltage_data