from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def index():
    return render_template("app/index.html")


@app.errorhandler(404)
def error_404(error):
    return render_template("errors/404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
