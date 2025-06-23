FROM python:3.11

RUN mkdir /code
COPY ./requirements.txt /code
WORKDIR /code

RUN pip install -r requirements.txt

RUN mkdir /start
COPY ./run.sh /start
RUN chmod +x /start/run.sh

RUN useradd tazo -s /bin/bash
USER tazo

CMD ["/start/run.sh"]
