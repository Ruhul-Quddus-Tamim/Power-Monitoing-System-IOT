#!/usr/bin/env python3
import os
import json
from dotenv import load_dotenv
load_dotenv()

from flask import request, url_for, render_template, redirect, flash, jsonify, session
import flask_login
from base import app, socketio
from database import User, get_last_hour, total_power_usage
from mqtt_handler import mqtt

HOST: str = os.getenv('HOST', '0.0.0.0')
PORT: int = os.getenv('PORT', 8080)
URL_SCHEME: str = os.getenv('URL_SCHEME', 'http')

login_manager = flask_login.LoginManager()
login_manager.login_view = 'sign_in'
login_manager.init_app(app)

mqtt.init_app(app)


class Login_User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    user_query = User.query.filter_by(name=username).first()
    if user_query:
        user = Login_User()
        user.id = username
        user.is_admin = user_query.is_admin
        return user
    else:
        return


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    password = request.form.get('password')
    user_query = User.query.filter_by(name=username).first()
    if not user_query or not user_query.verify_password(password):
        return
    else:
        user = Login_User()
        user.id = username
        user.is_admin = user_query.is_admin
        return user

@app.before_request
def clear_jinja_cache():
    # When you import jinja2 macros, they get cached which is annoying for local
    # development, so wipe the cache every request.
    if 'localhost' in request.host_url or '0.0.0.0' in request.host_url:
        app.jinja_env.cache = {}

app.before_request(clear_jinja_cache)

@app.route('/')
@flask_login.login_required
def index():
    record = get_last_hour(1)
    power = total_power_usage(1)
    total_power = (0 if not power.total_power else power.total_power)
    try:
        ac_mode = session['ac_mode']
    except KeyError:
        ac_mode = "Auto"
    return render_template('index.html', device_data=json.dumps(record), field_list=record.keys(), power_usage=format(total_power, '.2f'), ac_mode=ac_mode)

@app.route('/get_sensor_reading')
@flask_login.login_required
def get_sensor_reading():
    sensor = request.args.get('sensor')
    hour = request.args.get('hour')
    if "energy" in sensor:
        query_result = total_power_usage(int(hour))
        record = {}
        record["total_power"] = query_result.total_power
    else:
        record = get_last_hour(int(hour), sensor)
    return jsonify(record)

@app.route('/send_command')
@flask_login.login_required
def send_command():
    mode = request.args.get('mode')
    mqtt.publish("power_monitoring/ac_mode", mode)
    session['ac_mode'] = mode
    return jsonify("OK")

@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'GET':
        return render_template('sign-in.html')
    
    username = request.form.get('username')
    password = request.form.get('password')
    user_query = User.query.filter_by(name=username).first()
    if not user_query or not user_query.verify_password(password):
        flash('Please check your login details and try again.', category="warning")
        return redirect(url_for('sign_in', _external=True))
    else:
        session['ac_mode'] = 'Auto'
        user = Login_User()
        user.id = username
        flask_login.login_user(user)
        return redirect(url_for('index'))

@app.route('/sign_out')
@flask_login.login_required
def sign_out():
    flask_login.logout_user()
    return redirect(url_for('sign_in'))

if __name__ == '__main__':
    print("\nRunning on {}:{}...\n".format(HOST, PORT))
    #app.run(host=HOST, port=PORT, debug=True)
    socketio.run(app, host=HOST, port=PORT, debug=False, log_output=True)