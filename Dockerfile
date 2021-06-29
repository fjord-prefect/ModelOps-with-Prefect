FROM python:3.6
WORKDIR /home

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 -y
RUN apt-get install git vim zip graphviz -y
RUN pip install --upgrade pip

ADD requirements.txt /home
RUN pip install -r requirements.txt

ADD . /home
RUN pip install .

CMD jupyter-lab --ip=0.0.0.0 --no-browser --allow-root
