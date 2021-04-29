import pandas as pd
import streamlit as st
import tensorflow_hub as hub
from  elasticsearch import Elasticsearch
from tensorflow_text import SentencepieceTokenizer


ES = Elasticsearch('es:9200')
MODEL = hub.load('https://tfhub.dev/google/universal-sentence-encoder-multilingual/3')

def query(text):
    vector = MODEL(text)[0].numpy().tolist()
    script_query = {'script_score': {
        'query': {
            'bool': {
                'must': [
                    {'exists': {'field': 'date'}},
                    {'exists': {'field': 'story'}},
                    {'exists': {'field': 'genre'}},
                ]
            }
        },
        'script': {
            'source': 'cosineSimilarity(params.vector, doc.vector) + 1.0',
            'params': {'vector': vector}
        }
    }}
    res = ES.search(
        index='movie',
        body={
            "size": 5,
            "query": script_query,
        }
    )
    
    return res['hits']['hits']


def write_header():
    st.title('Movie Search Engine')

def write_movie(r):
    md = f'''
        - date: {r['_source']['date']}
        - story: {r['_source']['story']}
        - genre: {' | '.join(r['_source']['genre'])}
        - [url]({f'https://movie.naver.com/movie/bi/mi/basic.nhn?code=' + r['_id']})
    '''
    st.header(r['_source']['title'].strip())
    st.markdown(md)

def write_input():
    text = st.text_input('Enter query')
    res = query(text)
    for r in res:
        write_movie(r)


def main():
    write_header()
    write_input()

if __name__ == '__main__':

    main()