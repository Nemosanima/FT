from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea
from slugify import slugify

# Create flask app
app = Flask(__name__)
# SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
# Postgres database
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/libertyhub"
# Add secret key
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"
# Создаем базу данных
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    favorite_color = db.Column(db.String(50))
    password_hash = db.Column(db.String(100), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def password(self):
        raise AttributeError('Получить пароль невозможно')

    @password.setter
    def password(self, value):
        self.password_hash = generate_password_hash(value)

    def verify_password(self, value):
        return check_password_hash(self.password_hash, value)

    def __repr__(self):
        return '<Name %r>' % self.name


# Post model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)


# PostForm
class PostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    text = StringField('Текст', validators=[DataRequired()], widget=TextArea())
    submit = SubmitField("Создать")


# UserForm for model User
class UserForm(FlaskForm):
    name = StringField("Имя", validators=[DataRequired()])
    email = StringField("Почта", validators=[DataRequired()])
    favorite_color = StringField("Любимый цвет")
    password_hash = PasswordField(
        'Пароль',
        validators=[DataRequired(), EqualTo('password_hash2', message='Пароли должны совпадать')]
    )
    password_hash2 = PasswordField(
        'Повторите пароль', validators=[DataRequired()]
    )
    submit = SubmitField("Отправить")


# WTF Form
class NamerForm(FlaskForm):
    name = StringField("Имя", validators=[DataRequired()])
    submit = SubmitField("Отправить")


# Test PasswordForm
class PasswordForm(FlaskForm):
    email = StringField("Почта", validators=[DataRequired()])
    password_hash = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Отправить")



@app.route('/')
def index():
    return render_template("app/index.html")


@app.errorhandler(404)
def error_404(error):
    return render_template("errors/404.html"), 404


# Test WTF Form
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash('Форма успешно отправлена')
    return render_template("app/name.html",
                           name=name,
                           form=form
    )


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            # Хешированный пароль
            hashed_ps = generate_password_hash(form.password_hash.data)
            user = User(
                name=form.name.data,
                email=form.email.data,
                favorite_color=form.favorite_color.data,
                password_hash=hashed_ps
            )
            db.session.add(user)
            db.session.commit()
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''
        flash('Пользователь добавлен в базу данных успешно')
    users = User.query.order_by(User.created)
    return render_template("users/add_user.html",
                           form=form,
                           users=users)


@app.route('/user/<int:id>/update', methods=['GET', 'POST'])
def update_user(id):
    form = UserForm()
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.favorite_color = request.form.get('favorite_color')
        #user.password_hash = request.form.get('password_hash')
        try:
            db.session.commit()
            flash('Данные пользователя обновлены')
            return render_template('users/update_user.html', form=form, user=user)
        except:
            flash('Ошибка, попробуй снова')
            return render_template('users/update_user.html', form=form, user=user)
    else:
        return render_template('users/update_user.html', form=form, user=user)


@app.route('/user/<int:id>/delete')
def delete_user(id):
    user = User.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('Пользователь удален')
        return redirect(url_for('add_user'))
    except:
        flash('Ошибка, пользователь не удален')
        return redirect(url_for('add_user'))


@app.route('/test_password', methods=['GET', 'POST'])
def test_password():
    form = PasswordForm()
    if request.method == 'GET':
        return render_template('app/test_password.html', form=form)
    email = request.form.get('email')
    password = request.form.get('password_hash')
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        user_name = user.name
        flash('Проверка пройдена', category='success')
        return render_template('app/test_password.html', form=form, user_name=user_name)
    else:
        flash('Проверка не пройдена', category='error')
        return render_template('app/test_password.html', form=form)


# Json Api
@app.route('/data')
def data():
    dict_data = {
        'Harry': 'Potter',
        'Tonny': 'Stark',
        'Elon': 'Musk',
        'Stars': ['1EGT', '#YRE', 'GIT']
    }
    return dict_data


# AddPost
@app.route('/create/post', methods=['GET', 'POST'])
def create_post():
    form = PostForm()
    if request.method == 'GET':
        return render_template('app/create_post.html', form=form)
    title = form.title.data
    text = form.text.data
    post = Post(title=title, text=text)
    try:
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    except:
        flash('Данные не валидны')
        return render_template('app/create_post.html', form=form)




if __name__ == "__main__":
    app.run(debug=True)
