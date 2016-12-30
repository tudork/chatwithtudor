from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room,\
    close_room, rooms, disconnect
import random, string
async_mode = None
users = {}
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/user/<username>')
def index(username):
    if 'username' not in session:
        session['username'] = username
        users.update({username:''})
    return render_template('index.html', async_mode=async_mode)

@socketio.on('connect')
def tconnect():
    users.update({session['username']: request.sid})
    print(users)
    emit('users_list', {'data': [i for i in users.keys()]}, broadcast=True)

@socketio.on('disconnect')
def tdisconnect():
    if 'username' in session:
        users.pop(session['username'])
    emit('users_list', {'data': [i for i in users.keys()]}, broadcast=True)

@socketio.on('send_request')
def send_request(message):
    print('da')
    code = ''.join(random.SystemRandom().choice \
                       (string.ascii_letters + string.digits) for _ in range(8))
    emit('redirect', {'data': code})
    emit('send_request', {'data': code}, room = users.get(message['data']))

@app.route('/room/<code>')
def room(code):
    if 'username' in session:
        return render_template('chat.html', async_mode=async_mode)

@socketio.on('connected')
def connect(message):
    join_room(message['data'])
    print('mesag', message['data'])
    emit('message_event', {'data': 'Connected', 'user': session['username']},
         room = message['data'])

@socketio.on('send_message')
def send_message(message):
    emit('message_event', {'data': message['data'], 'user': session['username']},
         room = message['room'])

@socketio.on('disconnected')
def disconnect(message):
    print('da')
    leave_room(message['data'])
    emit('message_event', {'data': 'Disconnected', 'user': session['username']},
         room = message['data'])

@socketio.on('close_room')
def close_room(message):

    close_room(message['data'])


@app.route('/logout')
def logout():
    if 'username' in session:
        users.pop(session['username'])
        session.pop('username', None)
    return redirect("http://www.google.com")

if __name__ == '__main__':
    socketio.run(app, debug = True)