from flask import Flask, render_template, request
from joblib import load

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    if request.method == "POST":
        cv = load("./model/cv.pkl")
        clf = load("./model/spam_clf.pkl")

        message = cv.transform([request.form["message"]])
        prediction = clf.predict(message)

        return render_template("result.html", prediction=prediction)


if __name__ == '__main__':
    app.run(debug=True)