

# Movie Search Engine

## Objectives

Movie search engine using 

* [Multilingual Universal Sentence Encoder](https://arxiv.org/abs/1907.04307) 
* [ElasticSearch](https://www.elastic.co/kr/elasticsearch/)
* [Streamlit](https://github.com/streamlit/streamlit)





## Run

```shell
# Run docker
git clone https://github.com/respect5716/Movie_Search_Engine.git
cd Movie_Search_Engine
docker compose up

# Collect data
docker exec -it movie_app bash
python collect.py
```

then, connect to **localhost:8501**



## Result

![](https://github.com/respect5716/Movie_Search_Engine/blob/main/result.PNG)

