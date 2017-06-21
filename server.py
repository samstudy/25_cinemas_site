from flask import Flask, Response, render_template, request
from flask import jsonify
from flask import json
from movies_information import collect_movies_information
from flask_cache import Cache
from werkzeug.contrib.cache import SimpleCache


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
cache = SimpleCache()


def get_movies_from_cache():
    movies = cache.get('movies')
    if movies is None:
        movies = collect_movies_information()
        cache.set('movies', movies, timeout=12 * 60 * 60)
    return movies


@app.route('/todo/api/full_information.json', methods=['GET'])
def get_api():
    movies = get_movies_from_cache()
    return Response(json.dumps(movies, indent=4),
                    content_type='application/json; charset=utf-8')


@app.route('/api_description')
def api_description():
    return render_template('api.html')


@app.route('/')
def films_list():
    movies = get_movies_from_cache()
    return render_template('films_list.html',movies = movies)
   

if __name__ == "__main__":
    app.run(host='0.0.0.0')