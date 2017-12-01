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
    avisha_movie = cache.get('avisha_movie')
    if movies or avisha_movie is None:
        movies, avisha_movie = collect_movies_information()
        cache.set('movies', movies, timeout=86400)
        cache.set('avisha_movie', avisha_movie, timeout=86400)
    return movies ,avisha_movie


@app.route('/todo/api/full_information.json', methods=['GET'])
def get_api():
    movies,avisha_movie = get_movies_from_cache()
    return Response(json.dumps(movies,indent=4),
                    content_type='application/json; charset=utf-8')


@app.route('/api_description')
def api_description():
    return render_template('api.html')


@app.route('/')
def films_list():
    movies, avisha_movie = get_movies_from_cache()
    return render_template('films_list.html',movies = movies,
                                            avisha_movie = avisha_movie)
   

if __name__ == "__main__":
    app.run(host='0.0.0.0')