FROM ubuntu:18.04

MAINTAINER fadawar <fadawar@gmail.com>

# Add user
RUN adduser --quiet --disabled-password qtuser

# Install Python 3, PyQt5
RUN apt-get update \
    && apt-get install -y \
      python3 \
      python3-pyqt5

ADD app ./app
COPY app ./app
RUN ls app


#RUN env DISPLAY=$DISPLAY python3 "/app/main.py"
