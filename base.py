from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

import logging, sys
log_handler = logging.StreamHandler(sys.stdout)
logger = logging.getLogger("Power-Monitoring")
logger.setLevel(10)

app = Flask(__name__, static_url_path='', static_folder='static')
app.config.from_object("config.Config")
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(log_handler)
db = SQLAlchemy(app)
socketio = SocketIO(app, logger=True, engineio_logger=False)