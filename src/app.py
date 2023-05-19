from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"


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
    return render_template("app/name.html",
                           name=name,
                           form=form
    )


if __name__ == "__main__":
    app.run(debug=True)
