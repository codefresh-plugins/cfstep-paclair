FROM python:3.6.4-alpine3.7

ENV LANG C.UTF-8

RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
        git \
        nodejs && \
    pip install --no-cache-dir paclair && \
    npm install codefresh -g

COPY script/paclair.py /paclair.py

CMD [""]