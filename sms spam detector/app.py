from pathlib import Path
from flask import Flask, render_template, request
from joblib import load

model_path = Path.cwd().joinpath("sms spam detector", "model")

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    if request.method == "POST":
        # chargement du CountVectorizer
        cv = load(model_path.joinpath("cv.pkl"))

        # chargement du classifier
        clf = load(model_path.joinpath("spam_clf.pkl"))

        # pre-processing du message à classifier
        message = cv.transform([request.form["message"]])

        # prédiction
        prediction = clf.predict(message)

        return render_template("result.html", prediction=prediction)


if __name__ == '__main__':
    app.run(debug=True)