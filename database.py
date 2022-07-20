import bcrypt
import pytz
import json
from base import db
from sqlalchemy_utc import UtcDateTime, utcnow
from sqlalchemy.inspection import inspect
from sqlalchemy.sql import func
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta

localtz = pytz.timezone('Asia/Kuala_Lumpur')

class Serializer(object):

    def serialize(self):
        result = {}
        for c in inspect(self).attrs.keys():
            if c == "created_ts":
                result[c] = self.dump_datetime(getattr(self, c))
            else:
                result[c] = getattr(self, c)
        return result

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]

    @staticmethod
    def dump_datetime(value):
        if value is None:
            return None
        return value.astimezone(localtz).isoformat()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    hashed_password = db.Column(db.LargeBinary(128), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)
    created_ts = db.Column(UtcDateTime, default=utcnow(), nullable=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    @property           
    def password(self):
        raise AttributeError("Password is not redable attribute")

    @password.setter
    def password(self, password):
        salt = bcrypt.gensalt()
        self.hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password)

class Sensor(db.Model, Serializer):
    __tablename__ = "sensors"

    id = db.Column(db.Integer, primary_key=True)
    humidity = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    ac_on = db.Column(db.Boolean, nullable=False)
    voltage = db.Column(db.Float, nullable=False)
    current = db.Column(db.Float, nullable=False)
    energy = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.Float, nullable=False)
    pf = db.Column(db.Float, nullable=False)
    created_ts = db.Column(UtcDateTime, default=utcnow(), nullable=False)

    def __init__(self, initial_data):
        for key in initial_data:
            setattr(self, key, initial_data[key])

    def serialize(self):
        d = Serializer.serialize(self)
        del d['id']
        return json.dumps(d)

class PowerUsage(db.Model):
    __tablename__ = "power_usage"

    id = db.Column(db.Integer, primary_key=True)
    kwh = db.Column(db.Float, nullable=False)
    created_ts = db.Column(UtcDateTime, default=utcnow(), nullable=False)

    def __init__(self, kwh):
        self.kwh = kwh

def total_power_usage(hours):
    oldest = datetime.now(timezone.utc) - timedelta(hours=hours)
    query_result = (db.session.query(func.sum(PowerUsage.kwh).label("total_power")).filter(PowerUsage.created_ts > oldest)).first()
    return query_result
        
def get_last_hour(hours, sensor_name=None):
    oldest = datetime.now(timezone.utc) - timedelta(hours=hours)
    if sensor_name:
        query_result = (db.session.query(getattr(Sensor, sensor_name), Sensor.created_ts).filter(Sensor.created_ts > oldest))
        device_data = {sensor_name:[],"timestamp":[]}
        for record in query_result:
            device_data[sensor_name].append(getattr(record, sensor_name))
            device_data["timestamp"].append(record.created_ts.astimezone(localtz).isoformat())
    else:
        query_result = (db.session.query(Sensor).filter(Sensor.created_ts > oldest))
        device_data = {"humidity":[],"temperature":[],"ac_on":[],"voltage":[],"current":[],"energy":[],"frequency":[],"pf":[],"timestamp":[]}
        for record in query_result:
            device_data["humidity"].append(record.humidity)
            device_data["temperature"].append(record.temperature)
            device_data["ac_on"].append(record.ac_on)
            device_data["voltage"].append(record.voltage)
            device_data["current"].append(record.current)
            device_data["energy"].append(record.energy)
            device_data["frequency"].append(record.frequency)
            device_data["pf"].append(record.pf)
            device_data["timestamp"].append(record.created_ts.astimezone(localtz).isoformat())

    return device_data
