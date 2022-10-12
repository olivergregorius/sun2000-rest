FROM alpine:3.16

EXPOSE 5000
WORKDIR /usr/src/app
ENV UWSGI_WORKERS=5

RUN apk add --no-cache python3 py3-pip uwsgi-python3

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

COPY application ./application
COPY wsgi.py ./wsgi.py

CMD ["uwsgi", "--http-socket", "0.0.0.0:5000", \
                "--uid", "uwsgi", \
                "--plugins", "python3", \
                "--wsgi", "wsgi:app"]
