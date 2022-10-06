FROM python:3.10.5-alpine3.16

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/* ./

EXPOSE 5000
ENV FLASK_APP=/usr/src/app/main.py

ENTRYPOINT ["flask", "run"]
