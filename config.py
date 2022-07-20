import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = 'Shu7O8iVcyfpyukvrFMqLolHvLuafzQe'
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///monitoring_db.sqlite")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True
    MQTT_BROKER_URL = '104.248.147.39'
    MQTT_BROKER_PORT = 8883
    MQTT_CLIENT_ID = 'power_monitoring_server'
    MQTT_USERNAME = 'cairo'
    MQTT_PASSWORD = 'iman2dina'