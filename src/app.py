from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create flask app
app = Flask(__name__)
# Add database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
# Add secret key
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"
# Создаем базу данных
db = SQLAlchemy(app)


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Name %r>' % self.name


# UserForm for model User
class UserForm(FlaskForm):
    name = StringField("Имя", validators=[DataRequired()])
    email = StringField("Почта", validators=[DataRequired()])
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
            user = User(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
        form.name.data = ''
        form.email.data = ''
        flash('Пользователь добавлен в базу данных успешно')
    users = User.query.order_by(User.created)
    return render_template("users/add_user.html",
                           form=form,
                           users=users)


if __name__ == "__main__":
    app.run(debug=True)
