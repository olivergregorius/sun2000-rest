FROM python:3.10.5-alpine3.16

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY application .
COPY wsgi.py .

EXPOSE 5000
ENV FLASK_APP=/usr/src/app/wsgi.py

ENTRYPOINT ["flask", "run"]
