# coding=utf-8
# Portfolio v 0.2
import random
import sqlite3
import os

import flask_login
from flask_wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired, Email
from contextlib import closing

from flask import Flask, render_template, g, request, url_for, session, flash, send_from_directory, current_app
from werkzeug.utils import redirect, secure_filename


DATABASE = '/tmp/portfolio.db'
DEBUG = True
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


class RegisterForm(Form):
    email = TextField('Email address', [DataRequired(), Email()])
    login = TextField('login', validators = [DataRequired()])
    password = TextField('pass', validators = [DataRequired()])



@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exeption):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/', methods=['POST', 'GET'])
def authorisation():
    if request.method == 'POST':
            data = g.db.execute(
                'select login, password, id '
                'from users where login = ?', [request.form['login']])
            try:
                data = data.fetchall()[0]
            except IndexError:
                flash('Неверный логин или пароль'.decode('utf-8'))
                return render_template('authorisation.html')
            if request.form['pass'] == data[1]:
                session['username'] = request.form['login']
                session['id'] = data[2]
                return redirect(url_for('show_profile'))
            else:
                flash('Неверный логин или пароль'.decode('utf-8'))
                return render_template('authorisation.html')
    else:
        return render_template('authorisation.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('authorisation'))


@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        g.db.execute(
            'insert into users (login, password, email) '
            'values (?, ?, ?)',
            [request.form['login'], request.form['password'], request.form['email']])
        g.db.commit()
        return redirect(url_for('authorisation'))
    else:
        return render_template('registration.html')


#course register
'''@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User(email = form.email.data, username = form.username.data, password = generate_password_hash(form.password.data))
        return redirect(url_for('authorisation'))
    return render_template('register.html', form = form)
'''


@app.route('/admin/students/all')
def show_students():
    cur = g.db.execute(
        'select id, first_name, second_name, third_name, sex, birthday, about_me '
        'from students order by id desc')
    students = [dict(id=row[0], first_name=row[1], second_name=row[2], third_name=row[3], sex=row[4], birthday=row[5],
                     about_me=row[6]) for row in cur.fetchall()]
    return render_template('students.html', students=students)


@app.route('/add', methods=['POST', 'GET'])
def add_info():
    if 'username' in session:
        if request.method == 'POST':
            g.db.execute(
                'insert into students (first_name, second_name, third_name, sex, birthday, about_me, group_name, id) '
                'values (?, ?, ?, ?, ?, ?, ?, ?)',
                [request.form['first_name'], request.form['second_name'], request.form['third_name'], request.form['sex'],
                 request.form['birthday'], request.form['about_me'], request.form['group_name'], session['id']])
            g.db.commit()
            return redirect(url_for('show_profile'))
        else:
            return render_template('add_info.html')
    else:
        return redirect(url_for('authorisation'))


@app.route('/profile/portfolio/add', methods=['POST', 'GET'])
def add_to_portfolio():
    filename = ''
    if 'username' in session:
        if request.method == 'POST':
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = str(random.randint(0, 999999)) + secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                print filename
            g.db.execute(
                'insert into portfolio (text, image, student_id) '
                'values (?, ?, ?)',
                [request.form['text'], filename, session['id']])
            g.db.commit()
            return redirect(url_for('show_profile'))
        else:
            return render_template('add_to_portfolio.html')
    else:
        return redirect(url_for('authorisation'))


@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=filename)


@app.route('/profile')
def show_profile():
    if 'username' in session:
        d_stud = get_data_from(session['id'], 'students')
        d_port = g.db.execute(
                    'select * '
                    'from portfolio where student_id = ?', [session['id']])
        try:
            d_port = d_port.fetchall()
        except IndexError:
            d_port = ''
        return render_template('profile.html', d_stud=d_stud, d_port=d_port)
    else:
        return redirect(url_for('authorisation'))


def get_data_from(id=None, table=None):
    data = g.db.execute(
        'select * '
        'from ' + table + ' where id = ' + str(id))
    try:
        data = data.fetchall()[0]
    except IndexError:
        data = ''
    return data


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run()
    init_db()
