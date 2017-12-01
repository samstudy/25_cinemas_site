import requests
import itertools
from bs4 import BeautifulSoup
import re
import json
from flask import jsonify
import threading, queue
from threading import Thread



def parse_page(url,q):
   
    data_from_url = requests.get(url,headers={'User-Agent':
                                                          'Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.9.1.8)'
                                                           'Gecko/20100214 Linux Mint/8 (Helena) Firefox/''3.5.8',
                                              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                              'Accept-Language': 'ru,en-us;q=0.7,en;q=0.3',
                                              'Accept-Encoding': 'deflate',
                                              'Accept-Charset': 'windows-1251,utf-8;q=0.7,*;q=0.7',
                                              'Keep-Alive': '300',
                                              'Connection': 'keep-alive',
                                              'Referer': 'http://www.kinopoisk.ru/',
                                              'Cookie': 'users_info[check_sh_bool]=none; search_last_date=2017-11-19; search_last_month=2010-02;'
                                                        'PHPSESSID=b6df76a958983da150476d9cfa0aab18',
                                               })
    soup = BeautifulSoup(data_from_url.content, 'lxml')
    q.put(soup)



def get_movies_from_afisha():
    url = 'https://www.afisha.ru/msk/schedule_cinema/'
    data_from_url = requests.get(url)
    soup = BeautifulSoup(data_from_url.content, 'lxml')
    movies_from_afisha = soup.find_all('div',{'class':'object s-votes-hover-area collapsed'})[:10]
    return movies_from_afisha

    
def get_wanted_movie_urls(movie):
    knpoisk_url = 'https://www.kinopoisk.ru/index.php?first=yes&kp_query='
    movie_afisha_link =  movie['href'].replace('https://www.afisha.ru',
                                              'https://next.afisha.ru')
    movie_knpoisk_link = knpoisk_url + movie.text
    return  movie_afisha_link, movie_afisha_link


def get_movie_details(afisha_html,knpoisk_html):
    rating = knpoisk_html.find('span',{'class':'rating_ball'})
    if rating:
        rating = float(rating.text)
    votes = knpoisk_html.find('span',{'class':'ratingCount'})
    if votes:
        votes = int(re.sub('\s+','',votes.text))
    actors = afisha_html.find_all('p',{'class':'main-actors__name'})
    if actors:
        actors = [actor.text for actor in actors]
    movie_details = {
        'description': afisha_html.find('h2',{'class':
                                                    'info-widget__header'}).text,
        'text': afisha_html.find('p',{'class':
                                              'info-widget__description'}).text,
        'genre': re.sub('\nжанр\n|\n','',afisha_html.find('li',{'class':
                                                                 'info-widget__meta-item info-widget__meta-item_genres'}).text),
        'name': afisha_html.find('h1',{'class':'object__title'}).text,
        'origin_name':afisha_html.find('p',{'class':'object__subtitle'}).text,
        'image': re.sub('2x','',afisha_html.find('img',{'class':
                                                        'trailer__item-img'})['srcset']),
        'afisha_rating': afisha_html.find('div',{'class':
                                                'rating__selector-value'}).text,
        'actors': actors,
        'rating': rating,
        'votes': votes
        }
    return movie_details


def collect_movies_information():
    q = queue.Queue()
    movies = get_movies_from_afisha()
    moviess = [movie.find('h3',{'class':'usetags'}).find('a', href=True) for movie in movies]
    knpoisk_links,afisha_links = zip(*[get_wanted_movie_urls(movie) for movie in moviess])
 
    afisha_htmls = get_page_as_html(*afisha_links)
    knpoisk_htmls = get_page_as_html(*knpoisk_links)
    movies_html_dic = dict(zip(afisha_htmls, knpoisk_htmls))
    store_movie_information = [get_movie_details(afisha_html, knpoisk_html)
                        for afisha_html,knpoisk_html in movies_html_dic.items()]
    return store_movie_information, afisha_links


def get_page_as_html(*movie_links):
    q = queue.Queue()
    threads = [threading.Thread(target=parse_page, 
                                args=(link,q)) for link in movie_links]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    store_of_htmls = [q.get() for thread in threads]
    return store_of_htmls