FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /code/
COPY requirements.txt /code/
WORKDIR /code
RUN pip install -U pip && pip install -r requirements.txt && python -m nltk.downloader wordnet && python -m nltk.downloader stopwords
