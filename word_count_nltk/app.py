import os
import requests
import operator
from pathlib import Path
import re
import nltk
from flask import Flask, render_template, request
from collections import Counter
from bs4 import BeautifulSoup
from models import Result
from extensions import db
from stop_words import stops

# project directory
project_dir = Path.cwd()

# app factory
def create_app(config):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config)
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(flask_app)

    return flask_app


app = create_app(os.environ['APP_SETTINGS'])


@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = {}
    if request.method == "POST":
        try:
            url = request.form["url"]
            r = requests.get(url)
            print(r)
        except:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."
            )
            return render_template('index.html', errors=errors)
        if r:
            raw = BeautifulSoup(r.text, "html.parser").get_text()
            nltk.data.path.append("./nltk_data/")
            tokens = nltk.word_tokenize(raw)
            text = nltk.Text(tokens)

            # remove punctuation
            non_punct = re.compile(".*[A-Za-z].*")
            raw_words = [w for w in text if non_punct.match(w)]
            raw_word_count = Counter(raw_words)

            # stop words
            no_stop_words = [w for w in raw_words if w.lower() not in stops]
            no_stop_words_count = Counter(no_stop_words)

            # save the results
            results = sorted(
                no_stop_words_count.items(),
                key=operator.itemgetter(1),
                reverse=True
            )[:10]
            try:
                result = Result(
                    url=url,
                    result_all=raw_word_count,
                    result_no_stop_words=no_stop_words_count
                )
                db.session.add(result)
                db.session.commit()
            except:
                errors.append("Unable to add item to database.")

    return render_template("index.html", errors=errors, results=results)


@app.route("/results")
def results():
    if request.method == "GET":
        select = Result.query.all()[-10:]
        results = [
            {
                "url": s.url,
                "words": list(s.result_no_stop_words)[:15]
            } for s in select]
    return render_template("results.html", results=results)


if __name__ == '__main__':
    app.run()
