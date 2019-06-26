FROM kalilinux/kali-linux-docker
RUN mkdir /app
RUN apt-get update && apt-get install -y python3
COPY requirements.txt /app/requirements.txt
WORKDIR /app