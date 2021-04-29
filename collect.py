# REFERENCE: https://github.com/lovit/naver_movie_scraper
import time
import requests
from tqdm.auto import tqdm
from bs4 import BeautifulSoup

from tensorflow_text import SentencepieceTokenizer
import tensorflow_hub as hub
from elasticsearch import Elasticsearch


import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--start_idx', type=int, default=10001)
parser.add_argument('--end_idx', type=int,  default=202000)
args = parser.parse_args()


class MovieCollector(object):
    def __init__(self, index):
        self.model = hub.load('https://tfhub.dev/google/universal-sentence-encoder-multilingual/3')
        self.es = Elasticsearch('es:9200')
        self.index = index
        self.check_index()
    
    def check_index(self):
        indices = self.es.indices.get("*").keys()
        if self.index not in indices:
            self.create_index()
        else:
            print(f'Index {self.index} existed')
    
    def create_index(self):
        mapping = {"mappings": {
            "properties": {
                "vector": {"type": "dense_vector", "dims":512}
            }
        }}
    
        self.es.indices.create(index=self.index, body=mapping)
        print(f'Created index {self.index}')
    
    def text2vec(self, text):
        return self.model(text)[0].numpy().tolist()
    
    def _collect_movie(self, movie_code):
        data = crawl_movie(movie_code)
        if data['title']:
            vector = self.text2vec(data['story']) if data['story'] else self.text2vec(data['title'])
            data['vector'] = vector
            self.es.index(index=self.index, id=movie_code, body=data)

    def collect_movie(self, movie_code, update=False):
        if update:
            self._collect_movie(movie_code)
        else:
            try:
                self.es.get(index=self.index, id=movie_code)
            except:
                self._collect_movie(movie_code)

    def collect(self, start_idx=10001, end_idx=202000, update=False):
        for movie_code in tqdm(range(start_idx, end_idx+1)):
            self.collect_movie(movie_code, update)
            time.sleep(0.1)

            
def url_to_soup(url):
    req = requests.get(url)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    return soup

            
def crawl_movie(movie_code):
    basic_url = f'https://movie.naver.com/movie/bi/mi/basic.nhn?code={movie_code}'
    detail_url = f'https://movie.naver.com/movie/bi/mi/detail.nhn?code={movie_code}'
    basic_soup = url_to_soup(basic_url)
    detail_soup = url_to_soup(detail_url)
    
    return {
        'title': crawl_title(basic_soup),
        'story': crawl_story(basic_soup),
        'date': crawl_date(basic_soup),
        'genre': crawl_genre(basic_soup),
        'nation': crawl_nation(basic_soup),
        'grade': crawl_grade(basic_soup),
        'actors': crawl_actors(detail_soup),
        'directors': crawl_directors(detail_soup)
    }

def crawl_title(basic_soup):
    tag = basic_soup.select('h3.h_movie a')
    return tag[0].text if tag else None

def crawl_story(basic_soup):
    tag = basic_soup.select('p.con_tx')
    return tag[0].text if tag else None

def crawl_date(basic_soup):
    date = basic_soup.select('dl[class=info_spec] a[href*=open]')
    return date[-1].get('href').split('=')[1] if date else None

def crawl_genre(basic_soup):
    genre = basic_soup.select('dl[class=info_spec] a[href*=genre]')
    genre = [i.text for i in genre]
    return genre

def crawl_nation(basic_soup):
    nation = basic_soup.select('dl[class=info_spec] a[href*=nation]')
    nation = [i.text for i in nation]
    return nation

def crawl_grade(basic_soup):
    grade = basic_soup.select('dl[class=info_spec] a[href*=grade]')
    grade = [i.text for i in grade]
    return grade

def crawl_actors(detail_soup):
    # actor url = f'https://movie.naver.com/movie/bi/pi/basic.nhn?code={actor_code}'
    actors = detail_soup.select('div.made_people div.p_info > a')
    names = [i.text for i in actors]
    codes = [i.get('href').split('=')[1] for i in actors]
    actors = [{'name':i, 'code':j} for i,j in zip(names, codes)]
    return actors

def crawl_directors(detail_soup):
    directors = detail_soup.select('div.director div.dir_product > a')
    names = [i.text for i in directors]
    codes = [i.get('href').split('=')[1] for i in directors]
    directors = [{'name':i, 'code':j} for i,j in zip(names, codes)]
    return directors


if __name__ == '__main__':
    movie = MovieCollector('movie')
    movie.collect(args.start_idx, args.end_idx)