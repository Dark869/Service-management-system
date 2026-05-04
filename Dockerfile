FROM python:3.11

WORKDIR /code

COPY ./requirements.txt .
COPY ./run.sh /start/

RUN mkdir -p /start \
    && chmod +x /start/run.sh \
    && pip install -r requirements.txt \
    && useradd userweb -s /bin/bash

USER userweb

CMD ["/start/run.sh"]
