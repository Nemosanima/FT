from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
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

# Для аунтификации
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    about_myself = db.Column(db.Text)
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
    submit = SubmitField("Отправить")


# UserForm for model User
class UserForm(FlaskForm):
    username = StringField("Логин", validators=[DataRequired()])
    email = StringField("Почта", validators=[DataRequired()])
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


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


@app.route('/')
def index():
    posts = Post.query.order_by(Post.created.desc()).all()
    return render_template("app/index.html", posts=posts)


@app.route('/posts/<int:id>')
def post_detail(id):
    post = Post.query.get_or_404(id)
    return render_template("app/post_detail.html", post=post)


# AddPost
@app.route('/create/post', methods=['GET', 'POST'])
@login_required
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
        flash('Пост успешно создан')
        return redirect(url_for('index'))
    except:
        flash('Данные не валидны')
        return render_template('app/create_post.html', form=form)


# EditPost
@app.route('/posts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    form = PostForm()
    post = Post.query.get_or_404(id)
    if request.method == 'GET':
        return render_template('app/edit_post.html', form=form, post=post)
    post.title = request.form["title"]
    post.text = request.form["text"]
    try:
        flash('Пост успешно изменен')
        db.session.commit()
        return redirect(url_for("post_detail", id=post.id))
    except:
        flash('Данные не валидны')
        return render_template("app/edit_post.html", form=form, post=post)


# DeletePost
@app.route("/posts/<int:id>/delete")
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    try:
        db.session.delete(post)
        db.session.commit()
        flash('Пост успешно удален')
        return redirect(url_for("index"))
    except:
        flash('Ошибка. Пост не был удален')
        return redirect(url_for("post_detail", id=post.id))


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
                username=form.username.data,
                email=form.email.data,
                password_hash=hashed_ps
            )
            db.session.add(user)
            db.session.commit()
        form.username.data = ''
        form.email.data = ''
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
        user.username = request.form.get('username')
        user.email = request.form.get('email')
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
@login_required
def test_password():
    form = PasswordForm()
    if request.method == 'GET':
        return render_template('app/test_password.html', form=form)
    email = request.form.get('email')
    password = request.form.get('password_hash')
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        username = user.username
        flash('Проверка пройдена', category='success')
        return render_template('app/test_password.html', form=form, username=username)
    else:
        flash('Проверка не пройдена', category='error')
        return render_template('app/test_password.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':
        return render_template('users/login.html', form=form)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Авторизация прошла успешно')
                return redirect(url_for('index'))
            flash('Неверные пароль, попробуй снова')
            return render_template('users/login.html', form=form)
        flash('Неверные логин, попробуй снова')
        return render_template('users/login.html', form=form)
    flash('Данные не валидны, попробуй снова')
    return render_template('users/login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Вы вышли из учетной записи успешно')
    return redirect(url_for('index'))


@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return render_template('users/profile.html', user=user)
    flash('Пользователь не найден')
    return redirect(url_for('index'))



if __name__ == "__main__":
    app.run(debug=True)
