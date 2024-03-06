import json
import requests
import paho.mqtt.client as mqtt
import datetime

# กำหนดค่า MQTT Broker
MQTT_BROKER = '192.168.43.89'  # หรือ IP ของ MQTT broker ของคุณ
MQTT_PORT = 1883  # พอร์ตมาตรฐานสำหรับ MQTT
MQTT_TOPIC = 'sensor/voltage'  # เปลี่ยน 'your/topic' เป็น topic ที่คุณใช้

# กำหนด URL ของ FastAPI endpoint
FASTAPI_URL = 'http://fastapi:8000/add_voltage_data/'


# ฟังก์ชัน callback เมื่อเชื่อมต่อกับ MQTT broker สำเร็จ
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(MQTT_TOPIC)

# ฟังก์ชัน callback เมื่อได้รับข้อความจาก MQTT broker
def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode('utf-8'))
    voltage = data['voltage']
    current = data['current']
    timestamp = data['timestamp']  
    post_data = {'voltage': voltage, 'current': current, 'timestamp': timestamp}
    
    response = requests.post(FASTAPI_URL, json=post_data)
    print(f"Data posted to FastAPI: {response.text}")

# สร้าง MQTT client และกำหนดฟังก์ชัน callback
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# เชื่อมต่อกับ MQTT broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# เริ่มลูปเพื่อรับและส่งข้อมูล
client.loop_forever()
