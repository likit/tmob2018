FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
COPY requirements.txt /app
WORKDIR /app
RUN pip install -U pip && pip install -r requirements.txt
