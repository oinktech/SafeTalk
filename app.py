from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

DATABASE = 'chat.db'

# 创建用户和聊天记录数据库
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            content TEXT,
            type TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return User(user[0], user[1]) if user else None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            login_user(User(user[0], user[1]))
            return redirect(url_for('chat', room_id='default'))
        else:
            flash('登入失敗！請檢查用戶名和密碼。', 'error')

    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash('註冊成功！請登入。', 'success')
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash('用戶名已存在。', 'error')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/chat/<room_id>', methods=['GET', 'POST'])
@login_required
def chat(room_id):
    if request.method == 'POST':
        # 清除聊天记录以防止截图
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE room_id = ?", (room_id,))
        conn.commit()
        conn.close()

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE room_id = ?", (room_id,))
    messages = cursor.fetchall()
    conn.close()

    return render_template('chat.html', room_id=room_id, messages=messages)

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    room_id = request.form['room_id']
    content = request.form['content']
    msg_type = 'text'  # 假设消息类型为文本

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (room_id, user_id, content, type) VALUES (?, ?, ?, ?)",
                   (room_id, current_user.id, content, msg_type))
    conn.commit()
    conn.close()

    return redirect(url_for('chat', room_id=room_id))

@app.route('/upload_audio', methods=['POST'])
@login_required
def upload_audio():
    if 'audio' not in request.files:
        flash('未上傳音訊檔案！', 'error')
        return redirect(request.url)
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        flash('音訊檔案名稱為空！', 'error')
        return redirect(request.url)

    file_path = os.path.join('static/audio', audio_file.filename)
    audio_file.save(file_path)

    room_id = request.form['room_id']
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (room_id, user_id, content, type) VALUES (?, ?, ?, ?)",
                   (room_id, current_user.id, audio_file.filename, 'audio'))
    conn.commit()
    conn.close()

    return redirect(url_for('chat', room_id=room_id))

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=10000)
