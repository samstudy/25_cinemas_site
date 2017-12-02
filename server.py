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
    afisha_link = cache.get('afisha_link')
    if movies or afisha_link is None:
        movies, afisha_link = collect_movies_information()
        cache.set('movies', movies, timeout=86400)
        cache.set('afisha_link', afisha_link, timeout=86400)
    return movies ,afisha_link


@app.route('/todo/api/full_information.json', methods=['GET'])
def get_api():
    movies,afisha_link = get_movies_from_cache()
    return Response(json.dumps(movies,indent=4),
                    content_type='application/json; charset=utf-8')


@app.route('/api_description')
def api_description():
    return render_template('api.html')


@app.route('/')
def films_list():
    movies, afisha_link = get_movies_from_cache()
    return render_template('films_list.html',movies = movies,
                                            afisha_link = afisha_link)
   

if __name__ == "__main__":
    app.run(host='0.0.0.0')