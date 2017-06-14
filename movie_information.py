import requests
import itertools
from bs4 import BeautifulSoup
import re
import json
from flask import jsonify


def parse_afisha_page():
    inf_from_url = requests.get('https://www.afisha.ru/msk/schedule_cinema/')
    soup = BeautifulSoup(inf_from_url.content, 'lxml')
    raw_afisha_inf = soup.find_all('div',{'class':'object s-votes-hover-area collapsed'})
    return raw_afisha_inf
    

def get_movie_url():
    most_wanted = 10
    store_url = []
    movies_url = parse_afisha_page()
    for movie_url in movies_url:
        url = movie_url.find('h3',{'class':'usetags'}).find('a', href=True)
        store_url.extend([url['href']])
    return store_url[:MOST_WANTED]


def get_movie_details(page):
    description = requests.get(page)
    movie_store = []
    soup = BeautifulSoup(description.content, 'lxml')
    structure = json.loads(soup.find('script', type='application/ld+json').text)
    movie_details = {
    'description':structure['description'],
    'genre':structure['genre'],
    'image':structure['image'],
    'name':structure['name'],
    'text':structure['text'],
    'afisha_rating':structure['aggregateRating']['ratingValue'],
    'actors':[movie['name'] for movie in structure['actor']],
    'kpi':get_rating_and_counting_ball(structure['name'])
    }
    return movie_details


def get_rating_and_counting_ball(movie):
    payload = {'kp_query':movie, 'first':'yes'}
    movie_html = requests.get('https://www.kinopoisk.ru/index.php', params=payload)
    soup = BeautifulSoup(movie_html.content, 'lxml')
    movie_kpi = {
        'movie_rating': get_movie_rating(soup),
        'movie_votes': get_movie_votes(soup)
    }
    return movie_kpi


def get_movie_rating(movie):
    rating = movie.find('span',{'class':'rating_ball'})
    if rating:
        return float(rating.text)
    else:
        return None


def get_movie_votes(movie):
    votes = movie.find('span',{'class':'ratingCount'})
    if votes:
        return int(re.sub('\s+','',votes.text))
    else:
        return None


def collect_movie_information():
    movies = get_movie_url()
    store_movie_information = []
    for movie in movies:
        store_movie_information.append(get_movie_details(movie))
    return store_movie_information






