from flask import Flask, render_template, request, redirect, url_for, flash
from flask_uploads import UploadSet, configure_uploads, IMAGES, AUDIO, patch_request_class
from datetime import datetime
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于Flash消息

# 配置上传目录
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads/images'
app.config['UPLOADED_AUDIOS_DEST'] = 'uploads/audios'
photos = UploadSet('photos', IMAGES)
audios = UploadSet('audios', AUDIO)
configure_uploads(app, (photos, audios))
patch_request_class(app)  # 限制文件大小

# 初始化数据库
def init_db():
    with sqlite3.connect('forum.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                photo TEXT,
                audio TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
init_db()

@app.route('/')
def index():
    with sqlite3.connect('forum.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM posts ORDER BY created_at DESC')
        posts = cursor.fetchall()
    return render_template('index.html', posts=posts)

@app.route('/upload', methods=['POST'])
def upload():
    text = request.form.get('text')

    # 检查文本输入
    if not text:
        flash('請輸入文字內容！', 'danger')
        return redirect(url_for('index'))

    try:
        with sqlite3.connect('forum.db') as conn:
            cursor = conn.cursor()
            post = {'text': text}
            
            if 'photo' in request.files and request.files['photo'].filename != '':
                photo = request.files['photo']
                filename = photos.save(photo)
                post['photo'] = filename
            
            if 'audio' in request.files and request.files['audio'].filename != '':
                audio = request.files['audio']
                filename = audios.save(audio)
                post['audio'] = filename
            
            cursor.execute('INSERT INTO posts (text, photo, audio) VALUES (?, ?, ?)',
                           (text, post.get('photo'), post.get('audio')))
            conn.commit()
            flash('上傳成功！', 'success')
    except Exception as e:
        flash(f'上傳失敗：{str(e)}', 'danger')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
