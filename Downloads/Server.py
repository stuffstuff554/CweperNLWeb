import eventlet
eventlet.monkey_patch()

from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO, emit

import os

os.system("Created by Cweper NL, South Australia 2025")

print("🔥 Game Server Booting...")

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

players = {}

@app.route('/')
def index():
    print("📄 Serving game.html")
    return send_from_directory('.', 'game.html')

@app.route('/<path:path>')
def static_files(path):
    print(f"📄 Serving file: {path}")
    return send_from_directory('.', path)

@socketio.on('connect')
def handle_connect():
    sid = request.sid
    print(f"✅ Player connected: {sid}")
    players[sid] = {'x': 100, 'y': 100}
    emit('init', {'id': sid, 'players': players}, room=sid)
    emit('player_joined', {'id': sid, 'x': 100, 'y': 100}, broadcast=True, include_self=False)

@socketio.on('move')
def handle_move(data):
    sid = request.sid
    if sid in players:
        dx = data.get('dx', 0)
        dy = data.get('dy', 0)
        players[sid]['x'] += dx
        players[sid]['y'] += dy
        print(f"🎮 Movement from {sid}: dx={dx}, dy={dy}")
        emit('update_position', {
            'id': sid,
            'x': players[sid]['x'],
            'y': players[sid]['y']
        }, broadcast=True)

@socketio.on('chat_message')
def handle_chat_message(data):
    text = data.get('text')
    username = data.get('username', 'Anonymous')
    sid = request.sid
    print(f"💬 Chat from {username} ({sid}): {text}")
    emit('chat_message', {'text': text, 'id': sid, 'username': username}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    print(f"❌ Player disconnected: {sid}")
    players.pop(sid, None)
    emit('player_left', {'id': sid}, broadcast=True)

if __name__ == '__main__':
    try:
        print("🚀 Starting game server on port 4999...")
        socketio.run(app, host='0.0.0.0', port=4999, use_reloader=False)
    except Exception as e:
        print(f"❌ Server crashed: {e}")
