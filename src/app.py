from flask import Flask, render_template, flash, request, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from forms import LoginForm, RegistrationForm, PostForm, ProfileEditForm, SearchForm
from werkzeug.utils import secure_filename
import uuid as uuid
import os

# Create flask app
app = Flask(__name__)
# SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
# Postgres database
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/libertyhub"
# Add secret key
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"
# For pictures
UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Создаем базу данных
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Для аунтификации
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)
    #return User.query.get(int(user_id))


@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@app.route('/')
def index():
    posts = Post.query.order_by(Post.created.desc()).all()
    return render_template("app/index.html", posts=posts)


@app.route('/posts/<int:id>')
def post_detail(id):
    post = Post.query.get_or_404(id)
    return render_template("app/post_detail.html", post=post)


@app.route('/create/post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if request.method == 'GET':
        return render_template('app/create_post.html', form=form)
    title = form.title.data
    text = form.text.data
    post = Post(title=title, text=text, author=current_user.id)
    try:
        db.session.add(post)
        db.session.commit()
        flash('Пост успешно создан')
        return redirect(url_for('index'))
    except:
        flash('Данные не валидны')
        return render_template('app/create_post.html', form=form)


@app.route('/posts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    form = PostForm()
    post = Post.query.get_or_404(id)
    if current_user != post.author_related:
        return render_template('errors/403.html'),  403
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


@app.route("/posts/<int:id>/delete")
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author_related:
        return render_template('errors/403.html'), 403
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


@app.errorhandler(403)
def error_403(error):
    return render_template("errors/403.html"), 403


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


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if request.method == 'GET':
        return render_template('users/registration.html', form=form)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            flash('Пользователь с таким логином уже существует')
            return render_template('users/registration.html', form=form)
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Пользователь с такой почтой уже существует')
            return render_template('users/registration.html', form=form)
        if user is None:
            hashed_ps = generate_password_hash(form.password.data)
            user = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=hashed_ps
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Вы успешно зарегистрировались')
            return redirect(url_for('index'))
    flash('Данные не валидны')
    return render_template('users/registration.html', form=form)


@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return render_template('users/profile.html', user=user)
    flash('Пользователь не найден')
    return redirect(url_for('index'))


@app.route('/profile/<username>/edit', methods=['GET', 'POST'])
@login_required
def profile_edit(username):
    form = ProfileEditForm()
    user = User.query.filter_by(username=username).first()
    if current_user != user:
        return render_template('errors/403.html'), 403
    if request.method == 'GET':
        return render_template('users/profile_edit.html', user=user, form=form)
    user.username = form.username.data
    user.email = form.email.data
    user.about_myself = form.about_myself.data
    user.profile_picture = form.profile_picture.data
    # image name
    picture_filename = secure_filename(user.profile_picture.filename)
    # set uuid
    picture_name = str(uuid.uuid1()) + "_" + picture_filename
    # Save picture
    user.profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], picture_name))
    # Change picture into string to save it in db
    user.profile_picture = picture_name
    try:
        flash('Профиль успешно изменен', category='success')
        db.session.commit()
        return redirect(url_for("profile", username=user.username))
    except:
        flash('Данные не валидны', category='error')
        return render_template("users/profile_edit.html", form=form, user=user)


@app.route('/profile/<username>/delete')
@login_required
def profile_delete(username):
    user = User.query.filter_by(username=username).first()
    if current_user != user:
        return render_template('errors/403.html'), 403
    try:
        logout_user()
        db.session.delete(user)
        db.session.commit()
        flash('Аккаунт удален')
        return redirect(url_for("index"))
    except:
        flash('Ошибка. Аккаунт не был удален')
        return redirect(url_for("profile", username=user.username))


@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Post.query
    if form.validate_on_submit():
        form.searched = form.searched.data
        posts = posts.filter(Post.text.like('%'.lower() + form.searched.lower() + '%'.lower()))
        posts = posts.order_by(Post.created.desc()).all()
        if len(posts) > 0:
            flash('Все, что удалось найти по вашему запросу')
            return render_template('app/search.html', form=form, posts=posts, searched=form.searched)
        flash('По вашему запросу нет совпадений')
        return render_template('app/search.html', form=form, posts=posts, searched=form.searched)


@app.route('/admin')
@login_required
def admin():
    admins = [1, 5, 15]
    if current_user.id in admins:
        return render_template('admin/admin.html')
    return render_template('errors/403.html'), 403


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    about_myself = db.Column(db.Text)
    profile_picture = db.Column(db.String())
    posts = db.relationship('Post', backref='author_related')
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


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id'))
    created = db.Column(db.DateTime, default=datetime.utcnow)


if __name__ == "__main__":
    app.run(debug=True)
