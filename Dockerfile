# ベースイメージの読み込み
FROM alpine:3.14
WORKDIR /usr/app
RUN rm -rf /usr/app/*
COPY ./ /usr/app
RUN apk update
RUN apk add --no-cache python3 py3-pip
RUN apk add --no-cache ffmpeg
RUN cd /usr/app/
RUN pip install --ignore-installed distlib
RUN pip install pipenv
RUN python3 --version
RUN pipenv --python 3.9.17
RUN pipenv install -r /usr/app/requirements.txt
CMD pipenv run python -m dbot