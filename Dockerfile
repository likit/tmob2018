FROM python:2
ENV PYTHONUNBUFFERED 1
RUN mkdir /code/
COPY requirements.txt /code/
WORKDIR /code
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/divio/djangocms-column.git
