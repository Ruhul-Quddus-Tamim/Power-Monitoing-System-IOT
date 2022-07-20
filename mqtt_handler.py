import json
import time
from flask_mqtt import Mqtt, MQTT_LOG_ERR
from base import db, socketio
from database import Sensor, PowerUsage

mqtt = Mqtt()
start_time = time.time()

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('power_monitoring/device_data')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    global start_time
    data = json.loads(message.payload.decode())
    record = Sensor(data)
    db.session.add(record)
    db.session.commit()
    latest = Sensor.query.filter_by(id=record.id).first()
    socketio.emit('device_data', data=latest.serialize())
    
    elapsed = time.time() - start_time
    if elapsed>600: # 10 minutes time counter
        kwh = 10/60 * float(data["voltage"]) * float(data["current"])
        power_record = PowerUsage(kwh)
        db.session.add(power_record)
        db.session.commit()

        start_time = time.time()
        socketio.emit('power_data', data=kwh)

@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    if level == MQTT_LOG_ERR:
        print('Error: {}'.format(buf))
