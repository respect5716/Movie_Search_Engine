FROM python:3.7

VOLUME ["/app"]
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 8501
EXPOSE 8888

CMD ["streamlit", "run", "app.py"]