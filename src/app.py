from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


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
    created = db.Column(db.DateTime, default=datetime.utcnow)
    favorite_color = db.Column(db.String(50))

    def __repr__(self):
        return '<Name %r>' % self.name


# UserForm for model User
class UserForm(FlaskForm):
    name = StringField("Имя", validators=[DataRequired()])
    email = StringField("Почта", validators=[DataRequired()])
    favorite_color = StringField("Любимый цвет")
    submit = SubmitField("Отправить")


# WTF Form
class NamerForm(FlaskForm):
    name = StringField("Имя", validators=[DataRequired()])
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
            user = User(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data)
            db.session.add(user)
            db.session.commit()
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
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
        try:
            db.session.commit()
            flash('Данные пользователя обновлены')
            return render_template('users/update_user.html', form=form, user=user)
        except:
            flash('Ошибка, попробуй снова')
            return render_template('users/update_user.html', form=form, user=user)
    else:
        return render_template('users/update_user.html', form=form, user=user)





if __name__ == "__main__":
    app.run(debug=True)
