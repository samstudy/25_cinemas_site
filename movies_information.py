import requests
import itertools
from bs4 import BeautifulSoup
import re
import json
from flask import jsonify


def fetch_page(url, payload=None):
    if payload:
        data_from_url = requests.get(url, params=payload)
    else:
        data_from_url = requests.get(url)
    return data_from_url


def parse_page(page):
    soup = BeautifulSoup(page.content, 'lxml')
    return soup


def get_movies_from_afisha():
    url = 'https://www.afisha.ru/msk/schedule_cinema/'
    movies_from_afisha = parse_page(fetch_page(url)).find_all('div',{'class':'object s-votes-hover-area collapsed'})
    return movies_from_afisha


def get_wanted_movie():
    most_wanted_movie = 10
    movies = []
    movies_store = get_movies_from_afisha()
    for movie in movies_store:
        cinema = movie.find('h3',{'class':'usetags'}).find('a', href=True)
        movies.extend([cinema['href']])
    return movies[:most_wanted_movie]


def get_movie_details(page):
    movie = json.loads(parse_page(fetch_page(page)).find('script',
                                                         type='application/ld+json').text)
    movie_details = {
        'description': movie['description'],
        'genre': movie['genre'],
        'image': movie['image'],
        'name': movie['name'],
        'text': movie['text'],
        'afisha_rating': movie['aggregateRating']['ratingValue'],
        'actors': [actor['name'] for actor in movie['actor']],
        'url_to_afisha': movie['url'],
        'kpi': get_rating_and_counting_ball(movie['name'])
    }
    return movie_details


def get_rating_and_counting_ball(movie):
    url = 'https://www.kinopoisk.ru/index.php'
    payload = {'kp_query':movie, 'first':'yes'}
    movie_kpi = {
        'movie_rating': get_rating(parse_page(fetch_page(url, payload))),
        'movie_votes': get_votes(parse_page(fetch_page(url, payload)))
    }
    return movie_kpi


def get_rating(movie):
    rating = movie.find('span',{'class':'rating_ball'})
    if rating:
        return float(rating.text)
    else:
        return None


def get_votes(movie):
    votes = movie.find('span',{'class':'ratingCount'})
    if votes:
        return int(re.sub('\s+','',votes.text))
    else:
        return None


def collect_movies_information():
    movies = get_wanted_movie()
    store_movie_information = [get_movie_details(movie) for movie in movies]
    return store_movie_information
