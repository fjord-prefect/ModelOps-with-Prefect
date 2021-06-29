FROM python:3.6
WORKDIR /home

LABEL maintainer="fjord-prefect" name="ModelOps-with-Prefect" version="0.1"

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 -y
RUN apt-get install git vim zip graphviz -y
RUN pip install --upgrade pip

ADD requirements.txt /home
RUN pip install -r requirements.txt

ADD . /home
RUN pip install .

CMD jupyter-lab --ip=0.0.0.0 --no-browser --allow-root
