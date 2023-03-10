FROM python:3.10-buster
COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY . /app
WORKDIR /app
RUN chmod a+x gunicorn.sh

ENTRYPOINT ["./gunicorn.sh"]