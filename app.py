from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于Flash消息
app.config['WTF_CSRF_ENABLED'] = True  # 启用CSRF保护
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads/images'
app.config['UPLOADED_AUDIOS_DEST'] = 'uploads/audios'

class UploadForm(FlaskForm):
    text = TextAreaField('帖子内容', validators=[DataRequired()])
    photo = FileField('上传图片', validators=[FileAllowed(['jpg', 'jpeg', 'png'], '只能上传图片!')])
    audio = FileField('上传音频', validators=[FileAllowed(['mp3', 'wav'], '只能上传音频!')])
    submit = SubmitField('提交')

# 初始化数据库
def init_db(db_name):
    with sqlite3.connect(db_name) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                photo TEXT,
                audio TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

@app.route('/chat/index/', defaults={'suffix': None})
@app.route('/chat/index/<suffix>')
def index(suffix):
    db_name = 'forum.db' if suffix is None else f'forum_{suffix}.db'
    
    # 初始化新的数据库
    init_db(db_name)

    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM posts ORDER BY created_at DESC')
        posts = cursor.fetchall()
    
    form = UploadForm()
    return render_template('index.html', posts=posts, suffix=suffix, form=form)

@app.route('/upload', methods=['POST'])
def upload():
    form = UploadForm()
    suffix = request.form.get('suffix')  # 获取后缀

    # 根据后缀选择数据库
    db_name = 'forum.db' if suffix is None else f'forum_{suffix}.db'
    
    if form.validate_on_submit():
        text = form.text.data

        # 检查文本输入
        if not text:
            flash('請輸入文字內容！', 'danger')
            return redirect(url_for('index', suffix=suffix))

        try:
            with sqlite3.connect(db_name) as conn:
                cursor = conn.cursor()
                post = {'text': text}
                
                if form.photo.data:
                    photo = form.photo.data
                    filename = f"{text.replace(' ', '_')}_photo.jpg"
                    photo.save(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename))
                    post['photo'] = filename
                
                if form.audio.data:
                    audio = form.audio.data
                    filename = f"{text.replace(' ', '_')}_audio.mp3"
                    audio.save(os.path.join(app.config['UPLOADED_AUDIOS_DEST'], filename))
                    post['audio'] = filename
                
                cursor.execute('INSERT INTO posts (text, photo, audio) VALUES (?, ?, ?)',
                               (text, post.get('photo'), post.get('audio')))
                conn.commit()
                flash('上傳成功！', 'success')
        except Exception as e:
            flash(f'上傳失敗：{str(e)}', 'danger')

    return redirect(url_for('index', suffix=suffix))

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=10000)
