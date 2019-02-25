FROM python:3.6.5
ENV PYTHONUNBUFFERED 1
RUN mkdir /code/
COPY requirements.txt /code/
WORKDIR /code
RUN pip install -U pip && pip install -r requirements.txt
