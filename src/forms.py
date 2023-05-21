from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, EqualTo
from wtforms.widgets import TextArea


class PostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    text = StringField('Текст', validators=[DataRequired()], widget=TextArea())
    submit = SubmitField("Отправить")


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField("Логин", validators=[DataRequired()])
    email = StringField("Почта", validators=[DataRequired()])
    about_myself = TextAreaField("О себе")
    password = PasswordField(
        'Пароль',
        validators=[DataRequired(), EqualTo('password2', message='Пароли должны совпадать')]
    )
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired()]
    )
    submit = SubmitField("Регистрация")


class ProfileEditForm(FlaskForm):
    username = StringField("Логин", validators=[DataRequired()])
    email = StringField("Почта", validators=[DataRequired()])
    about_myself = TextAreaField("О себе")
    submit = SubmitField("Изменить")


class SearchForm(FlaskForm):
    searched = StringField("Поиск", validators=[DataRequired()])
    submit = SubmitField("Найти")