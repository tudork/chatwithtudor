from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room,\
    close_room, rooms, disconnect
import random, string, sqlite3, hashlib, sys, os, hashlib, base64


async_mode = None
users_conn =sqlite3.connect('database.db', check_same_thread=False)
users_cursor = users_conn.cursor()
users = {}
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def index():
    if 'username' in session: return redirect('/user/' + session['username'])
    else: return render_template('login.html', async_mode=async_mode)


@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    if 'username' in session: return ('trebuie sa dai logout')
    users_cursor.execute('''SELECT 1 FROM users WHERE username = ? ;''',
                         (username,))
    if not users_cursor.fetchone():
        m = hashlib.sha256()
        m.update(password.encode('utf-8'))
        users_cursor.execute('''INSERT INTO users VALUES
            (NULL, ?, ?, 0, NULL);''', (username, m.hexdigest() ))
        users_conn.commit()
        return redirect('/user/' + username)
    else: return ('username deja in baza de date')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if 'username' in session: return redirect('/user/' + session['username'])
    m = hashlib.sha256()
    m.update(password.encode('utf-8'))
    users_cursor.execute('''SELECT 1 FROM users WHERE username = ? and
                        password = ?;''', (username, m.hexdigest()))
    if users_cursor.fetchone():
        session['username'] = username
        return redirect('/user/' + username)
    else: return ('login esuat')

@app.route('/user/<username>')
def tindex(username):
    if 'username' not in session:
        session['username'] = username
        users.update({username:''})
    return render_template('index.html', async_mode=async_mode)

@socketio.on('connect')
def tconnect():
    users.update({session['username']: request.sid})
    print("connect", users)
    emit('users_list', {'data': [i for i in users.keys()]}, broadcast=True)

@socketio.on('disconnect')
def tdisconnect():
    print("tdisconnect")
    if 'username' in session:
        print("tdisconnect user", session['username'])
        #disconnect(users.get(session['username']))
        users.pop(session['username'])

        print("disconnect", users)
    emit('users_list', {'data': [i for i in users.keys()]}, broadcast=True)

@socketio.on('send_request')
def send_request(message):

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
    print('room', message['data'])
    emit('message_event', {'data': 'Connected', 'user': session['username']},
         room = message['data'])

@socketio.on('send_message')
def send_message(message):
    emit('message_event', {'data': message['data'], 'user': session['username']},
         room = message['room'])

@socketio.on('send_file')
def send_file(message):
    print(message['filename'])
    file_ext = os.path.splitext(message['filename'])
    m = hashlib.md5()

    m.update(message['data'].encode('utf-8'))
    filepath = "static/files/" + m.hexdigest() + file_ext[1]

    file = open(filepath, 'w')
    file.write(message['data'])
    emit('file_event', {'data': message['filename'], 'url' : m.hexdigest(),
                           'user': session['username'], 'file_ext': file_ext[1]},
                              room = message['room'])

@socketio.on('disconnected')
def disconnect(message):
    print('da')
    leave_room(message['data'])
    emit('message_event', {'data': 'Disconnected', 'user': session['username']},
         room = message['data'])

@app.route('/file/<fileHash>')
def getFile(fileHash):

    return redirect(url_for('static', filename = 'files/' + fileHash))

@app.route('/logout')
def logout():
    print("logout")
    if 'username' in session:
        print("logout user")
        users.pop(session['username'])
        session.pop('username', None)

    return redirect("/")

if __name__ == '__main__':
    socketio.run(app, debug = True)